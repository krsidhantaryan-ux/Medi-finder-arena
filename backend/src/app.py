"""
MediFinder — Application Factory.
Configures extensions, error handlers, blueprints, and database connections.
"""
import os
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS

from backend.src.config import settings
from backend.src.core.database import init_database, get_db
from backend.src.core.exceptions import AppError
from backend.src.core.security import get_current_user
from backend.src.models.category import CATEGORIES

# Import API Blueprints
from backend.src.blueprints.api.v1.auth import auth_api
from backend.src.blueprints.api.v1.medicines import medicines_api
from backend.src.blueprints.api.v1.pharmacies import pharmacies_api
from backend.src.blueprints.api.v1.reservations import reservations_api
from backend.src.blueprints.api.v1.reviews import reviews_api
from backend.src.blueprints.api.v1.admin import admin_api
from backend.src.blueprints.api.v1.docs import docs_api

# Import Web Blueprints
from backend.src.blueprints.web.public import public_web
from backend.src.blueprints.web.customer import customer_web
from backend.src.blueprints.web.pharmacy import pharmacy_web
from backend.src.blueprints.web.admin import admin_web


def create_app(test_config=None) -> Flask:
    """Create and configure the Flask application."""
    src_dir = Path(__file__).resolve().parent
    template_folder = str(src_dir / "templates")
    static_folder = str(src_dir / "static")

    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder,
    )

    # Load configuration
    app.config.update(
        SECRET_KEY=settings.SECRET_KEY,
        UPLOAD_FOLDER=settings.UPLOAD_FOLDER,
        MAX_CONTENT_LENGTH=settings.MAX_CONTENT_LENGTH,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    if test_config:
        app.config.update(test_config)

    # Enable CORS for REST API
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize Database
    with app.app_context():
        db = init_database()
        # Seed default categories if missing
        if db.categories.count_documents({}) == 0:
            for name, slug, icon in CATEGORIES:
                db.categories.insert_one({"name": name, "slug": slug, "icon": icon})

    # Serve static uploads
    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # Healthcheck endpoint
    @app.route("/api/v1/health")
    def health_check():
        return jsonify({
            "status": "healthy",
            "version": "2.0.0",
            "database": "mongodb",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    # Register API Blueprints under /api/v1
    api_prefix = "/api/v1"
    app.register_blueprint(auth_api, url_prefix=f"{api_prefix}/auth")
    app.register_blueprint(medicines_api, url_prefix=f"{api_prefix}/medicines")
    app.register_blueprint(pharmacies_api, url_prefix=f"{api_prefix}/pharmacies")
    app.register_blueprint(reservations_api, url_prefix=f"{api_prefix}/reservations")
    app.register_blueprint(reviews_api, url_prefix=f"{api_prefix}/reviews")
    app.register_blueprint(admin_api, url_prefix=f"{api_prefix}/admin")
    app.register_blueprint(docs_api, url_prefix=api_prefix)

    # Register Web Blueprints
    app.register_blueprint(public_web)
    app.register_blueprint(customer_web)
    app.register_blueprint(pharmacy_web)
    app.register_blueprint(admin_web)

    # Global Template Context
    @app.context_processor
    def inject_globals():
        return {
            "current_year": datetime.now().year,
            "current_user": get_current_user(),
            "default_lat": settings.DEFAULT_LAT,
            "default_lng": settings.DEFAULT_LNG,
        }

    # Centralized Error Handlers
    @app.errorhandler(AppError)
    def handle_app_error(err: AppError):
        if request.path.startswith("/api/"):
            return jsonify(err.to_dict()), err.status_code
        return render_template("error.html", code=err.status_code, message=err.message), err.status_code

    @app.errorhandler(404)
    def handle_404(err):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "status_code": 404, "error": "Endpoint not found"}), 404
        return render_template("error.html", code=404, message="The requested page could not be found."), 404

    @app.errorhandler(500)
    def handle_500(err):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "status_code": 500, "error": "Internal server error"}), 500
        return render_template("error.html", code=500, message="An unexpected error occurred. Our team is notified."), 500

    return app

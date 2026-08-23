"""
Authentication REST API endpoints.
"""
from flask import Blueprint, request
from backend.src.core.responses import success_response, error_response
from backend.src.core.security import require_auth, get_current_user
from backend.src.services.auth_service import AuthService

auth_api = Blueprint("auth_api", __name__, url_prefix="/auth")


@auth_api.route("/register/customer", methods=["POST"])
def register_customer():
    data = request.get_json(silent=True) or {}
    result = AuthService.register_customer(data)
    return success_response(data=result, message="Customer registered successfully", status_code=201)


@auth_api.route("/login/customer", methods=["POST"])
def login_customer():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    password = data.get("password", "")
    result = AuthService.login_customer(email, password)
    return success_response(data=result, message="Login successful")


@auth_api.route("/register/pharmacy", methods=["POST"])
def register_pharmacy():
    data = request.get_json(silent=True) or {}
    result = AuthService.register_pharmacy(data)
    return success_response(data=result, message="Pharmacy registered for review", status_code=201)


@auth_api.route("/login/pharmacy", methods=["POST"])
def login_pharmacy():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    password = data.get("password", "")
    result = AuthService.login_pharmacy(email, password)
    return success_response(data=result, message="Pharmacy login successful")


@auth_api.route("/login/admin", methods=["POST"])
def login_admin():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")
    result = AuthService.login_admin(username, password)
    return success_response(data=result, message="Admin authentication successful")


@auth_api.route("/me", methods=["GET"])
@require_auth()
def get_current_user_profile():
    user = get_current_user()
    return success_response(data=user, message="Current authenticated user")

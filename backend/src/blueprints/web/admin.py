"""
Admin Verification & Platform Governance Web Routes.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from backend.src.config import settings
from backend.src.services.auth_service import AuthService
from backend.src.services.admin_service import AdminService

admin_web = Blueprint("admin_web", __name__, url_prefix="/admin")


@admin_web.route("", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_web.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        try:
            AuthService.login_admin(username, password)
            session["admin_logged_in"] = True
            session["admin_user"] = username
            flash("Welcome, Administrator!", "success")
            return redirect(url_for("admin_web.dashboard"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("admin_login.html")


@admin_web.route("/dashboard")
def dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_web.login"))

    metrics = AdminService.get_dashboard_metrics()
    return render_template(
        "admin_dashboard.html",
        stats=metrics["counts"],
        shops=metrics["recent_shops"],
        audit_logs=metrics["audit_logs"],
    )


@admin_web.route("/shop/<string:shop_id>/<string:action>", methods=["POST"])
def shop_action(shop_id: str, action: str):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_web.login"))

    note = request.form.get("rejection_note", "").strip()
    try:
        AdminService.set_pharmacy_status(shop_id, action, note)
        flash(f"Pharmacy status updated to: {action.capitalize()}.", "success")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("admin_web.dashboard"))


@admin_web.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_user", None)
    flash("Admin logged out successfully.", "info")
    return redirect(url_for("admin_web.login"))

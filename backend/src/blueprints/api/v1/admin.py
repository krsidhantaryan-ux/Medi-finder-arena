"""
Admin REST API endpoints.
"""
from flask import Blueprint, request
from backend.src.core.responses import success_response
from backend.src.core.security import require_auth
from backend.src.services.admin_service import AdminService

admin_api = Blueprint("admin_api", __name__, url_prefix="/admin")


@admin_api.route("/metrics", methods=["GET"])
@require_auth(roles=["admin"])
def get_metrics():
    metrics = AdminService.get_dashboard_metrics()
    return success_response(data=metrics, message="Admin dashboard metrics")


@admin_api.route("/pharmacy/<string:shop_id>/<string:action>", methods=["POST"])
@require_auth(roles=["admin"])
def set_status(shop_id: str, action: str):
    data = request.get_json(silent=True) or {}
    note = data.get("note")
    updated = AdminService.set_pharmacy_status(shop_id, action, note)
    return success_response(data=updated, message=f"Pharmacy {action} action completed")

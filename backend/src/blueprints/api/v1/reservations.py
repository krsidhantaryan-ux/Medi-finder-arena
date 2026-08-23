"""
Reservations REST API endpoints.
"""
from flask import Blueprint, request
from backend.src.core.responses import success_response
from backend.src.core.security import require_auth, get_current_user
from backend.src.services.reservation_service import ReservationService

reservations_api = Blueprint("reservations_api", __name__, url_prefix="/reservations")


@reservations_api.route("", methods=["POST"])
def create_reservation():
    data = request.get_json(silent=True) or {}
    user = get_current_user()

    customer_id = user.get("id") if user and user.get("role") == "customer" else None
    customer_name = data.get("customer_name") or (user.get("customer_name") if user else None)

    res = ReservationService.create_reservation(
        inventory_id=data.get("inventory_id", ""),
        pharmacy_id=data.get("pharmacy_id", ""),
        customer_phone=data.get("customer_phone", ""),
        customer_name=customer_name,
        customer_id=customer_id,
        quantity=data.get("quantity", 1),
        note=data.get("note"),
    )
    return success_response(data=res, message="Medicine reserved successfully", status_code=201)


@reservations_api.route("/<string:res_id>/<string:action>", methods=["POST"])
@require_auth()
def update_reservation_action(res_id: str, action: str):
    user = get_current_user()
    role = user.get("role", "customer")
    updated = ReservationService.update_reservation_status(
        reservation_id=res_id,
        action=action,
        actor_role=role,
        actor_id=user.get("id"),
    )
    return success_response(data=updated, message=f"Reservation {action} successful")


@reservations_api.route("/my", methods=["GET"])
@require_auth(roles=["customer"])
def get_my_reservations():
    user = get_current_user()
    reservations = ReservationService.get_customer_reservations(user.get("id"))
    return success_response(data=reservations, message="Customer reservations")


@reservations_api.route("/pharmacy/<string:shop_id>", methods=["GET"])
@require_auth(roles=["pharmacist", "admin"])
def get_pharmacy_reservations(shop_id: str):
    reservations = ReservationService.get_pharmacy_reservations(shop_id)
    return success_response(data=reservations, message="Pharmacy reservations")

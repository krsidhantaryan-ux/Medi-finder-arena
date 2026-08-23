"""
Pharmacies REST API endpoints.
"""
from flask import Blueprint, request
from backend.src.core.responses import success_response
from backend.src.core.security import require_auth, get_current_user
from backend.src.services.pharmacy_service import PharmacyService

pharmacies_api = Blueprint("pharmacies_api", __name__, url_prefix="/pharmacies")


@pharmacies_api.route("/nearby", methods=["GET"])
def get_nearby_pharmacies():
    lat = request.args.get("lat", default=25.6110, type=float)
    lng = request.args.get("lng", default=85.1430, type=float)
    radius = request.args.get("radius", default=15.0, type=float)
    only_24h = request.args.get("open_24h", "false").lower() in ("true", "1", "yes")
    delivery = request.args.get("delivery", "false").lower() in ("true", "1", "yes")

    shops = PharmacyService.get_nearby_pharmacies(
        user_lat=lat,
        user_lng=lng,
        radius_km=radius,
        only_24h=only_24h,
        only_delivery=delivery
    )
    return success_response(data=shops, message="Nearby pharmacies retrieved")


@pharmacies_api.route("/<string:shop_id>", methods=["GET"])
def get_pharmacy_details(shop_id: str):
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    details = PharmacyService.get_pharmacy_details(shop_id, user_lat=lat, user_lng=lng)
    return success_response(data=details, message="Pharmacy details retrieved")


@pharmacies_api.route("/<string:shop_id>/inventory", methods=["POST"])
@require_auth(roles=["pharmacist", "admin"])
def add_inventory(shop_id: str):
    data = request.get_json(silent=True) or {}
    user = get_current_user()
    if user.get("role") == "pharmacist" and user.get("shop_id") != shop_id:
        from backend.src.core.exceptions import ForbiddenError
        raise ForbiddenError("You cannot modify another store's inventory.")

    item = PharmacyService.add_inventory_item(shop_id, data)
    return success_response(data=item, message="Medicine added to inventory", status_code=201)


@pharmacies_api.route("/<string:shop_id>/inventory/<string:item_id>", methods=["PUT", "PATCH"])
@require_auth(roles=["pharmacist", "admin"])
def update_inventory(shop_id: str, item_id: str):
    data = request.get_json(silent=True) or {}
    user = get_current_user()
    if user.get("role") == "pharmacist" and user.get("shop_id") != shop_id:
        from backend.src.core.exceptions import ForbiddenError
        raise ForbiddenError("You cannot modify another store's inventory.")

    updated = PharmacyService.update_inventory_item(shop_id, item_id, data)
    return success_response(data=updated, message="Inventory updated")


@pharmacies_api.route("/<string:shop_id>/inventory/<string:item_id>", methods=["DELETE"])
@require_auth(roles=["pharmacist", "admin"])
def delete_inventory(shop_id: str, item_id: str):
    user = get_current_user()
    if user.get("role") == "pharmacist" and user.get("shop_id") != shop_id:
        from backend.src.core.exceptions import ForbiddenError
        raise ForbiddenError("You cannot delete another store's inventory.")

    PharmacyService.delete_inventory_item(shop_id, item_id)
    return success_response(data={"id": item_id}, message="Inventory item removed")

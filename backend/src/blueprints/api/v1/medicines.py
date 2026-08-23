"""
Medicines REST API endpoints.
"""
from flask import Blueprint, request
from backend.src.core.responses import success_response
from backend.src.services.medicine_service import MedicineService

medicines_api = Blueprint("medicines_api", __name__, url_prefix="/medicines")


@medicines_api.route("/search", methods=["GET"])
def search_medicines():
    q = request.args.get("q", "")
    salt = request.args.get("salt", "")
    category = request.args.get("category", "")
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    radius = request.args.get("radius", default=25.0, type=float)
    in_stock = request.args.get("in_stock", "false").lower() in ("true", "1", "yes")
    open_24h = request.args.get("open_24h", "false").lower() in ("true", "1", "yes")
    delivery = request.args.get("delivery", "false").lower() in ("true", "1", "yes")
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=50, type=int)

    results = MedicineService.search_medicines(
        query=q,
        salt=salt,
        category_slug=category,
        user_lat=lat,
        user_lng=lng,
        max_distance_km=radius,
        in_stock_only=in_stock,
        open_24h=open_24h,
        delivery=delivery,
        page=page,
        limit=limit,
    )
    return success_response(
        data=results["results"],
        message="Search completed successfully",
        meta={
            "total": results["total"],
            "page": results["page"],
            "limit": results["limit"],
            "substitutes": results["substitutes"],
        }
    )


@medicines_api.route("/autocomplete", methods=["GET"])
def autocomplete():
    term = request.args.get("q", "")
    suggestions = MedicineService.get_autocomplete(term)
    return success_response(data=suggestions, message="Autocomplete suggestions")


@medicines_api.route("/<string:item_id>", methods=["GET"])
def get_medicine_detail(item_id: str):
    item = MedicineService.get_medicine_by_id(item_id)
    return success_response(data=item, message="Medicine item details")

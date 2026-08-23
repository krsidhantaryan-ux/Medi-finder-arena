"""
Public Web Portal Routes:
- Homepage with search bar, quick stats, category grid, top pharmacies
- Search explorer with interactive Leaflet map, distance sorting, in-stock filters, salt matching
- Pharmacy profile with inventory search, opening hours, directions, reviews
"""
from flask import Blueprint, render_template, request
from backend.src.config import settings
from backend.src.core.database import get_db
from backend.src.core.utils import serialize_doc, haversine_distance
from backend.src.models.category import CATEGORIES
from backend.src.services.medicine_service import MedicineService
from backend.src.services.pharmacy_service import PharmacyService

public_web = Blueprint("public_web", __name__)


@public_web.route("/")
def index():
    """Render public homepage."""
    db = get_db()
    total_medicines = db.inventory.count_documents({"is_active": True})
    total_shops = db.pharmacies.count_documents({"status": "Approved"})
    total_cities = len(db.pharmacies.distinct("city", {"status": "Approved"})) or 1

    # Fetch top approved pharmacies
    top_shops = list(db.pharmacies.find({"status": "Approved"}).limit(6))
    top_shops_serialized = []
    for s in top_shops:
        doc = serialize_doc(s)
        reviews = list(db.reviews.find({"pharmacy_id": doc["id"]}))
        doc["rating"] = round(sum(r.get("rating", 5) for r in reviews) / len(reviews), 1) if reviews else 5.0
        doc["review_count"] = len(reviews)
        top_shops_serialized.append(doc)

    return render_template(
        "index.html",
        stats={
            "medicines": total_medicines,
            "shops": total_shops,
            "cities": total_cities,
        },
        top_shops=top_shops_serialized,
        categories=CATEGORIES,
    )


@public_web.route("/search")
def search_page():
    """Interactive search page with map view."""
    query = request.args.get("q", "").strip()
    salt = request.args.get("salt", "").strip()
    category = request.args.get("category", "").strip()

    return render_template(
        "search.html",
        initial_q=query,
        initial_salt=salt,
        initial_cat=category,
        categories=CATEGORIES,
        default_center=[settings.DEFAULT_LAT, settings.DEFAULT_LNG],
    )


@public_web.route("/pharmacy/<string:shop_id>")
def pharmacy_profile(shop_id: str):
    """Public pharmacy profile with live inventory."""
    user_lat = request.args.get("lat", type=float)
    user_lng = request.args.get("lng", type=float)

    shop = PharmacyService.get_pharmacy_details(shop_id, user_lat=user_lat, user_lng=user_lng)
    return render_template(
        "shop_profile.html",
        shop=shop,
        inventory=shop.get("inventory", []),
        reviews=shop.get("reviews", []),
        is_owner=False,
    )

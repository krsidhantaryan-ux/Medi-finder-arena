"""
Reviews REST API endpoints.
"""
from flask import Blueprint, request
from backend.src.core.responses import success_response
from backend.src.core.security import require_auth, get_current_user
from backend.src.services.review_service import ReviewService

reviews_api = Blueprint("reviews_api", __name__, url_prefix="/reviews")


@reviews_api.route("/<string:shop_id>", methods=["POST"])
def post_review(shop_id: str):
    data = request.get_json(silent=True) or {}
    user = get_current_user()

    customer_id = user.get("id") if user and user.get("role") == "customer" else None
    customer_name = data.get("customer_name") or (user.get("customer_name") if user else "Verified Customer")

    review = ReviewService.add_review(
        pharmacy_id=shop_id,
        rating=int(data.get("rating", 5)),
        comment=data.get("comment", ""),
        customer_id=customer_id,
        customer_name=customer_name,
    )
    return success_response(data=review, message="Review submitted successfully", status_code=201)


@reviews_api.route("/<string:shop_id>", methods=["GET"])
def get_reviews(shop_id: str):
    reviews = ReviewService.get_pharmacy_reviews(shop_id)
    return success_response(data=reviews, message="Pharmacy reviews retrieved")

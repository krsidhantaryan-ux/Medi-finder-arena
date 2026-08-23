"""
Customer Review & Rating Service.
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from bson import ObjectId

from backend.src.core.database import get_db
from backend.src.core.exceptions import ValidationError, NotFoundError
from backend.src.core.utils import serialize_doc, to_object_id


class ReviewService:
    @staticmethod
    def add_review(
        pharmacy_id: str,
        rating: int,
        comment: str = "",
        customer_id: Optional[str] = None,
        customer_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit a rating and review for a pharmacy."""
        db = get_db()
        if rating < 1 or rating > 5:
            raise ValidationError("Rating must be between 1 and 5.")

        shop = db.pharmacies.find_one({"$or": [{"_id": to_object_id(pharmacy_id)}, {"_id": pharmacy_id}]})
        if not shop:
            raise NotFoundError("Pharmacy not found.")

        review_doc = {
            "pharmacy_id": str(shop["_id"]),
            "customer_id": str(customer_id) if customer_id else None,
            "customer_name": customer_name or "Verified Customer",
            "rating": int(rating),
            "comment": (comment or "").strip(),
            "created_at": datetime.now(timezone.utc),
        }

        res = db.reviews.insert_one(review_doc)
        review_doc["_id"] = str(res.inserted_id)
        return serialize_doc(review_doc)

    @staticmethod
    def get_pharmacy_reviews(pharmacy_id: str) -> List[Dict[str, Any]]:
        db = get_db()
        reviews = list(db.reviews.find({"pharmacy_id": str(pharmacy_id)}).sort("created_at", -1))
        return serialize_doc(reviews)

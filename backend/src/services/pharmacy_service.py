"""
Pharmacy and Pharmacist Management Service.
Handles store onboarding, geo-location nearby searches, public store profile,
and pharmacist inventory management.
"""
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from bson import ObjectId

from backend.src.core.database import get_db
from backend.src.core.exceptions import NotFoundError, ForbiddenError, ValidationError
from backend.src.core.utils import serialize_doc, haversine_distance, to_object_id, to_geojson_point


class PharmacyService:
    @staticmethod
    def get_nearby_pharmacies(
        user_lat: float,
        user_lng: float,
        radius_km: float = 15.0,
        only_24h: bool = False,
        only_delivery: bool = False,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Find approved pharmacies within a radius sorted by distance."""
        db = get_db()
        query: Dict[str, Any] = {"status": "Approved"}
        if only_24h:
            query["is_open_24h"] = True
        if only_delivery:
            query["delivery"] = True

        pharmacies = list(db.pharmacies.find(query))
        results = []
        for p in pharmacies:
            p_lat = p.get("lat")
            p_lng = p.get("lng")
            dist = haversine_distance(user_lat, user_lng, p_lat, p_lng)
            if dist is not None and dist <= radius_km:
                serialized = serialize_doc(p)
                serialized["distance_km"] = dist

                # Calculate average rating
                reviews = list(db.reviews.find({"pharmacy_id": serialized["id"]}))
                if reviews:
                    avg_rating = round(sum(r.get("rating", 5) for r in reviews) / len(reviews), 1)
                    serialized["rating"] = avg_rating
                    serialized["total_reviews"] = len(reviews)
                else:
                    serialized["rating"] = None
                    serialized["total_reviews"] = 0

                results.append(serialized)

        results.sort(key=lambda x: x.get("distance_km", 9999.0))
        return results[:limit]

    @staticmethod
    def get_pharmacy_details(shop_id: str, user_lat: Optional[float] = None, user_lng: Optional[float] = None) -> Dict[str, Any]:
        """Fetch comprehensive pharmacy details including inventory and reviews."""
        db = get_db()
        shop = db.pharmacies.find_one({"$or": [{"_id": to_object_id(shop_id)}, {"_id": shop_id}]})
        if not shop:
            raise NotFoundError("Pharmacy not found.")

        shop_data = serialize_doc(shop)
        shop_data["distance_km"] = haversine_distance(
            user_lat, user_lng, shop.get("lat"), shop.get("lng")
        )

        # Inventory
        inventory = list(db.inventory.find({"pharmacy_id": shop_data["id"], "is_active": True}))
        shop_data["inventory"] = serialize_doc(inventory)

        # Reviews
        reviews = list(db.reviews.find({"pharmacy_id": shop_data["id"]}).sort("created_at", -1))
        shop_data["reviews"] = serialize_doc(reviews)
        if reviews:
            shop_data["rating"] = round(sum(r.get("rating", 5) for r in reviews) / len(reviews), 1)
            shop_data["total_reviews"] = len(reviews)
        else:
            shop_data["rating"] = None
            shop_data["total_reviews"] = 0

        return shop_data

    @staticmethod
    def add_inventory_item(shop_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new medicine to pharmacy inventory."""
        db = get_db()
        med_name = payload.get("med_name", "").strip()
        if not med_name:
            raise ValidationError("Medicine name is required.")

        price = float(payload.get("price", 0))
        mrp = float(payload.get("mrp", price))
        stock_quantity = int(payload.get("stock_quantity", 0))

        item_doc = {
            "pharmacy_id": str(shop_id),
            "med_name": med_name,
            "salt_composition": payload.get("salt_composition", "").strip(),
            "category_slug": payload.get("category_slug", "tablets").strip(),
            "manufacturer": payload.get("manufacturer", "").strip(),
            "batch_no": payload.get("batch_no", "").strip(),
            "expiry_date": payload.get("expiry_date"),
            "price": price,
            "mrp": mrp,
            "stock_quantity": stock_quantity,
            "dosage": payload.get("dosage", "").strip(),
            "prescription": bool(payload.get("prescription", False)),
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        res = db.inventory.insert_one(item_doc)
        item_doc["_id"] = str(res.inserted_id)
        return serialize_doc(item_doc)

    @staticmethod
    def update_inventory_item(shop_id: str, item_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing inventory item."""
        db = get_db()
        item = db.inventory.find_one({"$or": [{"_id": to_object_id(item_id)}, {"_id": item_id}]})
        if not item:
            raise NotFoundError("Inventory item not found.")

        if str(item.get("pharmacy_id")) != str(shop_id):
            raise ForbiddenError("You cannot modify inventory from another pharmacy.")

        update_fields = {}
        for key in [
            "med_name", "salt_composition", "category_slug", "manufacturer",
            "batch_no", "expiry_date", "dosage", "prescription", "is_active"
        ]:
            if key in payload:
                update_fields[key] = payload[key]

        if "price" in payload and payload["price"] is not None:
            update_fields["price"] = float(payload["price"])
        if "mrp" in payload and payload["mrp"] is not None:
            update_fields["mrp"] = float(payload["mrp"])
        if "stock_quantity" in payload and payload["stock_quantity"] is not None:
            update_fields["stock_quantity"] = int(payload["stock_quantity"])

        update_fields["updated_at"] = datetime.now(timezone.utc)

        db.inventory.update_one(
            {"$or": [{"_id": to_object_id(item_id)}, {"_id": item_id}]},
            {"$set": update_fields}
        )

        updated = db.inventory.find_one({"$or": [{"_id": to_object_id(item_id)}, {"_id": item_id}]})
        return serialize_doc(updated)

    @staticmethod
    def delete_inventory_item(shop_id: str, item_id: str) -> bool:
        """Remove or deactivate an inventory item."""
        db = get_db()
        item = db.inventory.find_one({"$or": [{"_id": to_object_id(item_id)}, {"_id": item_id}]})
        if not item:
            raise NotFoundError("Inventory item not found.")

        if str(item.get("pharmacy_id")) != str(shop_id):
            raise ForbiddenError("You cannot delete inventory from another pharmacy.")

        db.inventory.delete_one({"$or": [{"_id": to_object_id(item_id)}, {"_id": item_id}]})
        return True

    @staticmethod
    def update_pharmacy_profile(shop_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update pharmacy operating details."""
        db = get_db()
        shop = db.pharmacies.find_one({"$or": [{"_id": to_object_id(shop_id)}, {"_id": shop_id}]})
        if not shop:
            raise NotFoundError("Pharmacy not found.")

        update_fields = {}
        for key in ["phone", "owner_name", "license_number", "description", "address", "city", "state", "pincode", "open_time", "close_time"]:
            if key in payload:
                update_fields[key] = payload[key]

        if "is_open_24h" in payload:
            update_fields["is_open_24h"] = bool(payload["is_open_24h"])
        if "delivery" in payload:
            update_fields["delivery"] = bool(payload["delivery"])

        if "lat" in payload and "lng" in payload:
            lat = float(payload["lat"])
            lng = float(payload["lng"])
            update_fields["lat"] = lat
            update_fields["lng"] = lng
            update_fields["location"] = to_geojson_point(lat, lng)

        update_fields["updated_at"] = datetime.now(timezone.utc)

        db.pharmacies.update_one(
            {"$or": [{"_id": to_object_id(shop_id)}, {"_id": shop_id}]},
            {"$set": update_fields}
        )
        updated = db.pharmacies.find_one({"$or": [{"_id": to_object_id(shop_id)}, {"_id": shop_id}]})
        return serialize_doc(updated)

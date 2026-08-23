"""
Medicine and Inventory Business Service.
Provides high-performance search, fuzzy/text matching, salt substitute finder,
autocomplete suggestions, and inventory management.
"""
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from bson import ObjectId

from backend.src.core.database import get_db
from backend.src.core.exceptions import NotFoundError, ValidationError
from backend.src.core.utils import serialize_doc, haversine_distance, to_object_id


class MedicineService:
    @staticmethod
    def search_medicines(
        query: str = "",
        salt: str = "",
        category_slug: str = "",
        user_lat: Optional[float] = None,
        user_lng: Optional[float] = None,
        max_distance_km: float = 25.0,
        in_stock_only: bool = False,
        open_24h: bool = False,
        delivery: bool = False,
        page: int = 1,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Search medicines across pharmacies with proximity sorting,
        salt matching, and pharmacy status filters.
        """
        db = get_db()
        query = query.strip()
        salt = salt.strip()

        # Step 1: Find active and approved pharmacies
        shop_filter: Dict[str, Any] = {"status": "Approved"}
        if open_24h:
            shop_filter["is_open_24h"] = True
        if delivery:
            shop_filter["delivery"] = True

        pharmacies = list(db.pharmacies.find(shop_filter))
        pharmacy_map = {}
        for p in pharmacies:
            pid = str(p["_id"])
            p_lat = p.get("lat")
            p_lng = p.get("lng")
            dist = haversine_distance(user_lat, user_lng, p_lat, p_lng) if user_lat and user_lng else None
            if dist is not None and dist > max_distance_km:
                continue  # Out of range
            p["distance_km"] = dist
            pharmacy_map[pid] = p

        if not pharmacy_map:
            return {"results": [], "total": 0, "page": page, "limit": limit, "substitutes": []}

        # Step 2: Build inventory query
        inv_filter: Dict[str, Any] = {
            "pharmacy_id": {"$in": list(pharmacy_map.keys())},
            "is_active": True,
        }

        if in_stock_only:
            inv_filter["stock_quantity"] = {"$gt": 0}

        if category_slug:
            inv_filter["category_slug"] = category_slug

        regex_clauses = []
        if query:
            q_pattern = re.compile(re.escape(query), re.IGNORECASE)
            regex_clauses.append({"med_name": q_pattern})
            regex_clauses.append({"salt_composition": q_pattern})
            regex_clauses.append({"manufacturer": q_pattern})

        if salt:
            s_pattern = re.compile(re.escape(salt), re.IGNORECASE)
            regex_clauses.append({"salt_composition": s_pattern})

        if regex_clauses:
            inv_filter["$or"] = regex_clauses

        # Execute query
        inventory_items = list(db.inventory.find(inv_filter))

        # Join pharmacy data and compute exact distance
        results = []
        matched_salts = set()
        for item in inventory_items:
            pid = item.get("pharmacy_id")
            pharmacy = pharmacy_map.get(pid)
            if not pharmacy:
                continue

            serialized_item = serialize_doc(item)
            serialized_item["pharmacy_name"] = pharmacy.get("name")
            serialized_item["pharmacy_address"] = pharmacy.get("address")
            serialized_item["pharmacy_city"] = pharmacy.get("city")
            serialized_item["pharmacy_phone"] = pharmacy.get("phone")
            serialized_item["pharmacy_lat"] = pharmacy.get("lat")
            serialized_item["pharmacy_lng"] = pharmacy.get("lng")
            serialized_item["pharmacy_open_24h"] = pharmacy.get("is_open_24h", False)
            serialized_item["pharmacy_delivery"] = pharmacy.get("delivery", False)
            serialized_item["distance_km"] = pharmacy.get("distance_km")

            if item.get("salt_composition"):
                matched_salts.add(item.get("salt_composition").strip())

            results.append(serialized_item)

        # Sort: in-stock first, then nearest distance, then lowest price
        results.sort(
            key=lambda x: (
                0 if (x.get("stock_quantity") or 0) > 0 else 1,
                x.get("distance_km") if x.get("distance_km") is not None else 9999.0,
                x.get("price", 0),
            )
        )

        # Find salt substitutes if query was specific
        substitutes = []
        if matched_salts and query:
            sub_filter = {
                "salt_composition": {"$in": list(matched_salts)},
                "pharmacy_id": {"$in": list(pharmacy_map.keys())},
                "stock_quantity": {"$gt": 0},
                "is_active": True,
            }
            all_sub_items = list(db.inventory.find(sub_filter).limit(20))
            q_lower = query.lower()
            for s in all_sub_items:
                # Exclude if same medicine name
                if q_lower in s.get("med_name", "").lower():
                    continue
                pid = s.get("pharmacy_id")
                pharmacy = pharmacy_map.get(pid)
                if pharmacy:
                    sub_doc = serialize_doc(s)
                    sub_doc["pharmacy_name"] = pharmacy.get("name")
                    sub_doc["distance_km"] = pharmacy.get("distance_km")
                    substitutes.append(sub_doc)
                if len(substitutes) >= 6:
                    break

        total = len(results)
        paginated_results = results[(page - 1) * limit : page * limit]

        return {
            "results": paginated_results,
            "total": total,
            "page": page,
            "limit": limit,
            "substitutes": substitutes,
        }

    @staticmethod
    def get_autocomplete(term: str, limit: int = 8) -> List[Dict[str, str]]:
        """Fast autocomplete for search bar."""
        if not term or len(term.strip()) < 2:
            return []
        db = get_db()
        pattern = re.compile(re.escape(term.strip()), re.IGNORECASE)

        items = list(
            db.inventory.find(
                {
                    "$or": [
                        {"med_name": pattern},
                        {"salt_composition": pattern},
                    ],
                    "is_active": True,
                },
                {"med_name": 1, "salt_composition": 1, "dosage": 1}
            ).limit(limit)
        )

        seen = set()
        suggestions = []
        for item in items:
            name = item.get("med_name", "").strip()
            salt = item.get("salt_composition", "").strip()
            key = f"{name}:{salt}"
            if key not in seen:
                seen.add(key)
                suggestions.append({
                    "name": name,
                    "salt": salt,
                    "dosage": item.get("dosage", ""),
                })
        return suggestions

    @staticmethod
    def get_medicine_by_id(item_id: str) -> Dict[str, Any]:
        """Fetch single medicine inventory record."""
        db = get_db()
        item = db.inventory.find_one({"$or": [{"_id": to_object_id(item_id)}, {"_id": item_id}]})
        if not item:
            raise NotFoundError("Medicine item not found.")
        return serialize_doc(item)

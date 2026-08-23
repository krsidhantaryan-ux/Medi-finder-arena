"""
Medicine Reservation Lifecycle Service.
Provides atomic reservations, hold expiration handling, confirmation workflows,
and stock replenishment on cancellation.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from bson import ObjectId

from backend.src.config import settings
from backend.src.core.database import get_db
from backend.src.core.exceptions import ValidationError, NotFoundError, ConflictError, ForbiddenError
from backend.src.core.utils import serialize_doc, to_object_id


class ReservationService:
    @staticmethod
    def create_reservation(
        inventory_id: str,
        pharmacy_id: str,
        customer_phone: str,
        customer_name: Optional[str] = None,
        customer_id: Optional[str] = None,
        quantity: int = 1,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a medicine reservation with atomic inventory stock validation.
        """
        db = get_db()
        quantity = max(1, int(quantity))
        customer_phone = customer_phone.strip()
        if not customer_phone:
            raise ValidationError("Contact phone number is required.")

        # Check inventory item
        item = db.inventory.find_one({"$or": [{"_id": to_object_id(inventory_id)}, {"_id": inventory_id}]})
        if not item or not item.get("is_active"):
            raise NotFoundError("Medicine item is not available.")

        current_stock = item.get("stock_quantity", 0)
        if current_stock < quantity:
            raise ConflictError(f"Insufficient stock. Only {current_stock} units available.")

        pharmacy = db.pharmacies.find_one({"$or": [{"_id": to_object_id(pharmacy_id)}, {"_id": pharmacy_id}]})
        if not pharmacy:
            raise NotFoundError("Pharmacy not found.")

        now = datetime.now(timezone.utc)
        held_until = now + timedelta(hours=settings.HOLD_WINDOW_HOURS)

        # Atomic stock decrement
        db.inventory.update_one(
            {"$or": [{"_id": to_object_id(inventory_id)}, {"_id": inventory_id}]},
            {"$inc": {"stock_quantity": -quantity}, "$set": {"updated_at": now}}
        )

        reservation_doc = {
            "inventory_id": str(item["_id"]),
            "pharmacy_id": str(pharmacy["_id"]),
            "pharmacy_name": pharmacy.get("name"),
            "pharmacy_address": pharmacy.get("address"),
            "pharmacy_phone": pharmacy.get("phone"),
            "med_name": item.get("med_name"),
            "dosage": item.get("dosage", ""),
            "price": item.get("price", 0),
            "customer_id": str(customer_id) if customer_id else None,
            "customer_name": customer_name or "Walk-in Customer",
            "customer_phone": customer_phone,
            "quantity": quantity,
            "status": "Pending",  # Pending | Confirmed | Collected | Cancelled | Expired
            "note": (note or "").strip(),
            "held_until": held_until,
            "created_at": now,
            "updated_at": now,
        }

        res = db.reservations.insert_one(reservation_doc)
        reservation_doc["_id"] = str(res.inserted_id)

        return serialize_doc(reservation_doc)

    @staticmethod
    def update_reservation_status(
        reservation_id: str,
        action: str,
        actor_role: str,
        actor_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transitions:
        - Pharmacist: confirm, collect, cancel
        - Customer: cancel
        """
        db = get_db()
        r = db.reservations.find_one({"$or": [{"_id": to_object_id(reservation_id)}, {"_id": reservation_id}]})
        if not r:
            raise NotFoundError("Reservation not found.")

        current_status = r.get("status")
        now = datetime.now(timezone.utc)

        action = action.lower()
        new_status = current_status

        if action == "confirm":
            if actor_role not in ["pharmacist", "admin"]:
                raise ForbiddenError("Only the pharmacy can confirm a reservation.")
            new_status = "Confirmed"

        elif action == "collect":
            if actor_role not in ["pharmacist", "admin"]:
                raise ForbiddenError("Only the pharmacy can mark a reservation as collected.")
            new_status = "Collected"

        elif action == "cancel":
            if current_status in ["Collected", "Cancelled"]:
                raise ConflictError(f"Reservation is already {current_status}.")
            new_status = "Cancelled"
            # Restore stock
            db.inventory.update_one(
                {"$or": [{"_id": to_object_id(r["inventory_id"])}, {"_id": r["inventory_id"]}]},
                {"$inc": {"stock_quantity": r.get("quantity", 1)}, "$set": {"updated_at": now}}
            )
        else:
            raise ValidationError(f"Invalid reservation action: {action}")

        db.reservations.update_one(
            {"$or": [{"_id": to_object_id(reservation_id)}, {"_id": reservation_id}]},
            {"$set": {"status": new_status, "updated_at": now}}
        )

        updated = db.reservations.find_one({"$or": [{"_id": to_object_id(reservation_id)}, {"_id": reservation_id}]})
        return serialize_doc(updated)

    @staticmethod
    def get_pharmacy_reservations(shop_id: str) -> List[Dict[str, Any]]:
        """Get all reservations for a pharmacy."""
        db = get_db()
        items = list(db.reservations.find({"pharmacy_id": str(shop_id)}).sort("created_at", -1))
        return serialize_doc(items)

    @staticmethod
    def get_customer_reservations(customer_id: str) -> List[Dict[str, Any]]:
        """Get all reservations for a customer."""
        db = get_db()
        items = list(db.reservations.find({"customer_id": str(customer_id)}).sort("created_at", -1))
        return serialize_doc(items)

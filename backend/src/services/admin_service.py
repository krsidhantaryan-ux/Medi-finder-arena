"""
System Administration Service.
Handles pharmacy verification workflows, system-wide analytics, and audit logs.
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from bson import ObjectId

from backend.src.core.database import get_db
from backend.src.core.exceptions import NotFoundError, ValidationError
from backend.src.core.utils import serialize_doc, to_object_id


class AdminService:
    @staticmethod
    def get_dashboard_metrics() -> Dict[str, Any]:
        """Aggregate system-wide statistics for the admin dashboard."""
        db = get_db()
        total_shops = db.pharmacies.count_documents({})
        approved_shops = db.pharmacies.count_documents({"status": "Approved"})
        pending_shops = db.pharmacies.count_documents({"status": "Pending"})
        rejected_shops = db.pharmacies.count_documents({"status": "Rejected"})

        total_inventory = db.inventory.count_documents({})
        total_reservations = db.reservations.count_documents({})
        pending_reservations = db.reservations.count_documents({"status": "Pending"})
        total_customers = db.users.count_documents({"role": "customer"})

        recent_shops = list(db.pharmacies.find().sort("created_at", -1).limit(20))
        recent_logs = list(db.audit_logs.find().sort("created_at", -1).limit(30))

        return {
            "counts": {
                "total_shops": total_shops,
                "approved_shops": approved_shops,
                "pending_shops": pending_shops,
                "rejected_shops": rejected_shops,
                "total_inventory": total_inventory,
                "total_reservations": total_reservations,
                "pending_reservations": pending_reservations,
                "total_customers": total_customers,
            },
            "recent_shops": serialize_doc(recent_shops),
            "audit_logs": serialize_doc(recent_logs),
        }

    @staticmethod
    def set_pharmacy_status(shop_id: str, action: str, note: Optional[str] = None) -> Dict[str, Any]:
        """Approve or reject a registered pharmacy."""
        db = get_db()
        shop = db.pharmacies.find_one({"$or": [{"_id": to_object_id(shop_id)}, {"_id": shop_id}]})
        if not shop:
            raise NotFoundError("Pharmacy not found.")

        action = action.lower()
        now = datetime.now(timezone.utc)

        if action == "approve":
            new_status = "Approved"
            rejection_note = None
        elif action == "reject":
            new_status = "Rejected"
            rejection_note = note or "Application does not meet pharmacy verification criteria."
        elif action == "reset":
            new_status = "Pending"
            rejection_note = None
        else:
            raise ValidationError(f"Invalid status action: {action}")

        db.pharmacies.update_one(
            {"$or": [{"_id": to_object_id(shop_id)}, {"_id": shop_id}]},
            {"$set": {"status": new_status, "rejection_note": rejection_note, "updated_at": now}}
        )

        # Log admin audit event
        db.audit_logs.insert_one({
            "actor_type": "admin",
            "action": f"pharmacy_{action}",
            "detail": f"Pharmacy '{shop.get('name')}' marked as {new_status}. Note: {rejection_note or 'None'}",
            "created_at": now,
        })

        updated = db.pharmacies.find_one({"$or": [{"_id": to_object_id(shop_id)}, {"_id": shop_id}]})
        return serialize_doc(updated)

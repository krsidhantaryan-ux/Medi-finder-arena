"""
Authentication and Authorization Service.
Handles registration, login, token issuance, and password security for
Customers, Pharmacists, and System Admins.
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from bson import ObjectId

from backend.src.config import settings
from backend.src.core.database import get_db
from backend.src.core.exceptions import ConflictError, UnauthorizedError, NotFoundError, ValidationError
from backend.src.core.security import hash_password, check_password, create_access_token, create_refresh_token
from backend.src.core.utils import serialize_doc, to_geojson_point


class AuthService:
    @staticmethod
    def register_customer(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new customer account."""
        db = get_db()
        email = payload.get("email", "").strip().lower()
        if not email or "@" not in email:
            raise ValidationError("Valid email address is required.")

        existing = db.users.find_one({"email": email})
        if existing:
            raise ConflictError("An account with this email already exists.")

        password = payload.get("password", "")
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters long.")

        user_doc = {
            "name": payload.get("name", "").strip(),
            "email": email,
            "phone": payload.get("phone", "").strip(),
            "password_hash": hash_password(password),
            "role": "customer",
            "city": payload.get("city", "Patna"),
            "lat": payload.get("lat"),
            "lng": payload.get("lng"),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        result = db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)
        user_doc["_id"] = user_id

        # Generate JWT tokens
        access_token = create_access_token(user_id=user_id, role="customer", email=email, extra={"name": user_doc["name"]})
        refresh_token = create_refresh_token(user_id=user_id, role="customer")

        return {
            "user": serialize_doc(user_doc),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @staticmethod
    def login_customer(email: str, password: str) -> Dict[str, Any]:
        """Authenticate customer credentials and issue tokens."""
        db = get_db()
        email = email.strip().lower()
        user = db.users.find_one({"email": email, "role": "customer"})
        if not user or not check_password(password, user.get("password_hash", "")):
            raise UnauthorizedError("Invalid email or password.")

        user_id = str(user["_id"])
        access_token = create_access_token(
            user_id=user_id,
            role="customer",
            email=email,
            extra={"name": user.get("name")}
        )
        refresh_token = create_refresh_token(user_id=user_id, role="customer")

        return {
            "user": serialize_doc(user),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @staticmethod
    def login_admin(username: str, password: str) -> Dict[str, Any]:
        """Authenticate system admin."""
        if username != settings.ADMIN_USER or password != settings.ADMIN_PASS:
            raise UnauthorizedError("Invalid admin credentials.")

        access_token = create_access_token(
            user_id="admin",
            role="admin",
            email=settings.ADMIN_USER,
            extra={"name": "System Administrator"}
        )
        refresh_token = create_refresh_token(user_id="admin", role="admin")

        return {
            "user": {
                "id": "admin",
                "name": "System Administrator",
                "email": settings.ADMIN_USER,
                "role": "admin",
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @staticmethod
    def register_pharmacy(payload: Dict[str, Any], files: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Register a new pharmacy / chemist store with license documentation."""
        db = get_db()
        email = payload.get("email", "").strip().lower()
        if not email:
            raise ValidationError("Pharmacy email is required.")

        name = payload.get("name", "").strip()
        if not name:
            raise ValidationError("Pharmacy name is required.")

        existing = db.pharmacies.find_one({"$or": [{"email": email}, {"name": name}]})
        if existing:
            raise ConflictError("A pharmacy with this name or email is already registered.")

        password = payload.get("password", "")
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters.")

        lat = float(payload.get("lat", settings.DEFAULT_LAT))
        lng = float(payload.get("lng", settings.DEFAULT_LNG))

        files = files or {}
        pharmacy_doc = {
            "name": name,
            "email": email,
            "phone": payload.get("phone", "").strip(),
            "password_hash": hash_password(password),
            "owner_name": payload.get("owner_name", "").strip(),
            "license_number": payload.get("license_number", "").strip(),
            "license_image": files.get("license_image"),
            "gst_certificate": files.get("gst_certificate"),
            "shop_photo": files.get("shop_photo"),
            "description": payload.get("description", "").strip(),
            "address": payload.get("address", "").strip(),
            "city": payload.get("city", "Patna").strip(),
            "state": payload.get("state", "Bihar").strip(),
            "pincode": payload.get("pincode", "").strip(),
            "location": to_geojson_point(lat, lng),
            "lat": lat,
            "lng": lng,
            "open_time": payload.get("open_time", "08:00"),
            "close_time": payload.get("close_time", "22:00"),
            "is_open_24h": bool(payload.get("is_open_24h", False)),
            "delivery": bool(payload.get("delivery", False)),
            "status": "Pending",  # Requires Admin Approval
            "rejection_note": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        res = db.pharmacies.insert_one(pharmacy_doc)
        shop_id = str(res.inserted_id)
        pharmacy_doc["_id"] = shop_id

        # Create user record for pharmacist
        db.users.insert_one({
            "name": pharmacy_doc["owner_name"] or name,
            "email": email,
            "role": "pharmacist",
            "shop_id": shop_id,
            "password_hash": pharmacy_doc["password_hash"],
            "created_at": datetime.now(timezone.utc),
        })

        return serialize_doc(pharmacy_doc)

    @staticmethod
    def login_pharmacy(email: str, password: str) -> Dict[str, Any]:
        """Authenticate pharmacy / chemist store."""
        db = get_db()
        email = email.strip().lower()
        shop = db.pharmacies.find_one({"email": email})
        if not shop or not check_password(password, shop.get("password_hash", "")):
            raise UnauthorizedError("Invalid pharmacy email or password.")

        shop_id = str(shop["_id"])
        access_token = create_access_token(
            user_id=shop_id,
            role="pharmacist",
            email=email,
            extra={"shop_id": shop_id, "shop_name": shop.get("name")}
        )
        refresh_token = create_refresh_token(user_id=shop_id, role="pharmacist")

        return {
            "pharmacy": serialize_doc(shop),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

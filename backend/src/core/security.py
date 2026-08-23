"""
Authentication & Security Utilities:
- Password hashing using bcrypt
- JWT Access and Refresh token generation/verification
- Role-Based Access Control (RBAC) decorators
"""
import datetime
from functools import wraps
from typing import Optional, List, Dict, Any

import bcrypt
import jwt
from flask import request, session, g

from backend.src.config import settings
from backend.src.core.exceptions import UnauthorizedError, ForbiddenError


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    if not password or not hashed:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_access_token(
    user_id: str,
    role: str,
    email: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
) -> str:
    """Generate a signed JWT access token."""
    payload = {
        "sub": str(user_id),
        "role": role,
        "email": email or "",
        "type": "access",
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def create_refresh_token(user_id: str, role: str) -> str:
    """Generate a signed JWT refresh token."""
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "refresh",
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRES_DAYS),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token."""
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token has expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid authentication token.")


def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Extract authenticated user identity from either Bearer JWT header or Flask session.
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        payload = decode_token(token)
        return {
            "id": payload.get("sub"),
            "role": payload.get("role"),
            "email": payload.get("email"),
            "shop_id": payload.get("shop_id"),
            "shop_name": payload.get("shop_name"),
            "customer_name": payload.get("customer_name"),
        }

    # Fallback to session
    if session.get("admin_logged_in"):
        return {"id": "admin", "role": "admin", "email": settings.ADMIN_USER}
    if session.get("shop_id"):
        return {
            "id": str(session["shop_id"]),
            "shop_id": str(session["shop_id"]),
            "shop_name": session.get("shop_name"),
            "role": "pharmacist",
        }
    if session.get("customer_id"):
        return {
            "id": str(session["customer_id"]),
            "role": "customer",
            "email": session.get("customer_email"),
            "customer_name": session.get("customer_name"),
        }

    return None


def require_auth(roles: Optional[List[str]] = None):
    """
    Decorator to protect routes requiring authentication and optional role checking.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                raise UnauthorizedError("Authentication required to access this resource.")
            if roles and user.get("role") not in roles:
                raise ForbiddenError(f"Access denied. Requires one of roles: {', '.join(roles)}")
            g.current_user = user
            return fn(*args, **kwargs)
        return wrapper
    return decorator

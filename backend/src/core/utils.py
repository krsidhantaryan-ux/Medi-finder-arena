"""
Utility functions for Geo calculations, file storage validation,
JSON/BSON serialization, and activity logging.
"""
import math
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Union
from werkzeug.utils import secure_filename
from bson import ObjectId

from backend.src.config import settings


def haversine_distance(
    lat1: Optional[float],
    lng1: Optional[float],
    lat2: Optional[float],
    lng2: Optional[float]
) -> Optional[float]:
    """
    Calculate great-circle distance in kilometres between two coordinates.
    Returns distance rounded to 2 decimal places, or None if coordinates are missing.
    """
    if lat1 is None or lng1 is None or lat2 is None or lng2 is None:
        return None
    try:
        r = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlng / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(r * c, 2)
    except Exception:
        return None


def to_geojson_point(lat: float, lng: float) -> Dict[str, Any]:
    """Convert lat/lng to GeoJSON Point format [lng, lat] for 2dsphere index."""
    return {
        "type": "Point",
        "coordinates": [float(lng), float(lat)]
    }


def parse_geojson_coords(location: Optional[Dict[str, Any]]) -> (Optional[float], Optional[float]):
    """Extract (lat, lng) tuple from GeoJSON dict or return (None, None)."""
    if not location or not isinstance(location, dict):
        return None, None
    coords = location.get("coordinates")
    if coords and len(coords) >= 2:
        return coords[1], coords[0]  # GeoJSON is [lng, lat]
    return None, None


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def save_uploaded_file(file_storage, allowed_extensions: set = None) -> Optional[str]:
    """
    Save uploaded file securely with a collision-free timestamp prefix.
    Returns the relative filename or None if invalid.
    """
    if not file_storage or not file_storage.filename:
        return None

    if allowed_extensions is None:
        allowed_extensions = settings.ALLOWED_IMAGE_EXTENSIONS

    if not allowed_file(file_storage.filename, allowed_extensions):
        return None

    name = secure_filename(file_storage.filename)
    unique_name = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}_{name}"
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    destination = os.path.join(settings.UPLOAD_FOLDER, unique_name)
    file_storage.save(destination)
    return unique_name


def serialize_doc(doc: Any) -> Any:
    """
    Recursively serialize MongoDB BSON documents into JSON-safe dictionaries.
    Converts ObjectId to string and datetime to ISO format.
    """
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        result = {}
        for k, v in doc.items():
            if k == "_id":
                result["id"] = str(v)
            elif isinstance(v, ObjectId):
                result[k] = str(v)
            elif isinstance(v, datetime):
                result[k] = v.isoformat()
            elif isinstance(v, dict) or isinstance(v, list):
                result[k] = serialize_doc(v)
            else:
                result[k] = v
        return result
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, datetime):
        return doc.isoformat()
    return doc


def to_object_id(val: Union[str, ObjectId, int]) -> ObjectId:
    """Safely convert string or id to ObjectId."""
    if isinstance(val, ObjectId):
        return val
    try:
        return ObjectId(str(val))
    except Exception:
        # Fallback for integer/mock IDs
        return str(val)  # type: ignore

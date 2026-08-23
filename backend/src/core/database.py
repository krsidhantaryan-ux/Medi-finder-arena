"""
MediFinder — Scalable MongoDB Database Manager.
Supports production MongoDB clusters (Atlas, Replica Sets, Docker) with connection pooling,
spatial 2dsphere indexing, text search indexes, and automatic fallback for zero-config local runs.
"""
import logging
from typing import Optional
from pymongo import MongoClient, ASCENDING, TEXT, GEOSPHERE
from pymongo.database import Database
import mongomock

from backend.src.config import settings

logger = logging.getLogger("medifinder.database")

_client: Optional[MongoClient] = None
_db: Optional[Database] = None
_is_mock: bool = False


def init_database() -> Database:
    """Initialize MongoDB connection with pooling and indexes."""
    global _client, _db, _is_mock

    if _db is not None:
        return _db

    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URI}...")
        client = MongoClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
            maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
            minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
        )
        # Verify connection
        client.admin.command("ping")
        _client = client
        _db = client[settings.MONGODB_DB_NAME]
        _is_mock = False
        logger.info("Successfully connected to live MongoDB server.")
    except Exception as exc:
        logger.warning(
            f"Could not connect to live MongoDB ({exc}). Falling back to resilient in-memory MongoDB engine."
        )
        _client = mongomock.MongoClient()
        _db = _client[settings.MONGODB_DB_NAME]
        _is_mock = True

    _create_indexes(_db)
    return _db


def _create_indexes(db: Database):
    """Ensure all required performance, spatial, and unique indexes exist."""
    try:
        # Users collection
        db.users.create_index([("email", ASCENDING)], unique=True, sparse=True)
        db.users.create_index([("role", ASCENDING)])

        # Pharmacies collection
        db.pharmacies.create_index([("email", ASCENDING)], unique=True, sparse=True)
        db.pharmacies.create_index([("status", ASCENDING)])
        db.pharmacies.create_index([("location", GEOSPHERE)])
        db.pharmacies.create_index([("city", ASCENDING)])

        # Inventory collection
        try:
            db.inventory.create_index([
                ("med_name", TEXT),
                ("salt_composition", TEXT),
                ("manufacturer", TEXT)
            ])
        except Exception:
            # Fallback for mock engines that do not implement full text index
            db.inventory.create_index([("med_name", ASCENDING)])
            db.inventory.create_index([("salt_composition", ASCENDING)])

        db.inventory.create_index([("pharmacy_id", ASCENDING), ("med_name", ASCENDING)])
        db.inventory.create_index([("is_active", ASCENDING), ("stock_quantity", ASCENDING)])
        db.inventory.create_index([("category_slug", ASCENDING)])

        # Reservations collection
        db.reservations.create_index([("pharmacy_id", ASCENDING), ("status", ASCENDING)])
        db.reservations.create_index([("customer_id", ASCENDING)])
        db.reservations.create_index([("held_until", ASCENDING)])

        # Reviews collection
        db.reviews.create_index([("pharmacy_id", ASCENDING)])

        # Favourites collection
        db.favourites.create_index(
            [("user_id", ASCENDING), ("med_name", ASCENDING), ("salt", ASCENDING)],
            unique=True
        )

        # Categories
        db.categories.create_index([("slug", ASCENDING)], unique=True)

        # Audit log
        db.audit_logs.create_index([("created_at", ASCENDING)])
        logger.info("MongoDB indexes verified.")
    except Exception as e:
        logger.warning(f"Index creation notice: {e}")


def get_db() -> Database:
    """Get or initialize active database handle."""
    global _db
    if _db is None:
        return init_database()
    return _db


def is_mock_db() -> bool:
    """Check if in-memory database mock is active."""
    return _is_mock


def close_database():
    """Close MongoDB connection gracefully."""
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None

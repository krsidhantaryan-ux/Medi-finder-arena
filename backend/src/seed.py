"""
MediFinder — Demo Database Seeding Script.
Populates the MongoDB database with realistic pharmacies, diverse medicine inventories,
salts, categories, reviews, and test accounts.
"""
import logging
from datetime import datetime, timezone, timedelta
from bson import ObjectId

from backend.src.core.database import get_db
from backend.src.core.security import hash_password
from backend.src.core.utils import to_geojson_point
from backend.src.models.category import CATEGORIES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("medifinder.seed")

DEMO_PHARMACIES = [
    {
        "name": "Apollo Pharmacy — Frazer Road",
        "email": "apollo@medifinder.demo",
        "phone": "+91 98000 11111",
        "owner_name": "Rajeev Mehta",
        "license_number": "DL-PT-20-BRD-00451",
        "city": "Patna", "state": "Bihar", "pincode": "800001",
        "address": "Shop 12, Frazer Road, Near Dak Bungalow, Patna",
        "lat": 25.6110, "lng": 85.1430,
        "open_time": "00:00", "close_time": "23:59",
        "is_open_24h": True, "delivery": True,
        "description": "24/7 chain pharmacy with full prescription, surgical, and wellness range.",
        "status": "Approved",
        "inventory": [
            ("Dolo 650", "Paracetamol", "tablets", "Micro Labs", "650mg, 15 tablets", 32.00, 30.50, 120, False),
            ("Azithral 500", "Azithromycin", "tablets", "Alembic", "500mg, 5 tablets", 119.00, 95.00, 40, True),
            ("Augmentin 625 Duo", "Amoxicillin+Clavulanic Acid", "tablets", "GSK", "625mg, 10 tablets", 410.00, 356.00, 18, True),
            ("Crocin Advance", "Paracetamol", "tablets", "GSK", "500mg, 15 tablets", 30.00, 27.50, 200, False),
            ("Glycomet 500", "Metformin", "diabetes", "USV", "500mg, 20 tablets", 86.00, 74.00, 55, True),
            ("Telma 40", "Telmisartan", "cardiac", "Glenmark", "40mg, 15 tablets", 145.00, 121.00, 33, True),
            ("Ascoril LS", "Ambroxol+Levosalbutamol", "cough-cold", "Glenmark", "100ml syrup", 135.00, 118.00, 26, False),
            ("Volini Gel", "Diclofenac", "topicals", "Sun Pharma", "30g tube", 115.00, 99.00, 64, False),
            ("Becosules Z", "B-Complex+Vitamin C", "vitamins", "Pfizer", "20 capsules", 38.00, 33.00, 300, False),
            ("Accu-Chek Strips", "Blood Glucose Test Strips", "devices", "Roche", "Pack of 50", 1190.00, 999.00, 12, False),
        ],
    },
    {
        "name": "Wellness Forever Chemist — Boring Road",
        "email": "wellness@medifinder.demo",
        "phone": "+91 98000 22222",
        "owner_name": "Priya Singh",
        "license_number": "DL-PT-20-BRD-00782",
        "city": "Patna", "state": "Bihar", "pincode": "800014",
        "address": "Ground Floor, Boring Road, Srikrishnapuri, Patna",
        "lat": 25.6148, "lng": 85.1125,
        "open_time": "08:00", "close_time": "23:00",
        "is_open_24h": False, "delivery": True,
        "description": "Neighbourhood chemist with free same-day delivery within 5 km.",
        "status": "Approved",
        "inventory": [
            ("Paracetamol 500", "Paracetamol", "tablets", "Cipla", "500mg, 10 tablets", 22.00, 18.50, 500, False),
            ("Dolo 650", "Paracetamol", "tablets", "Micro Labs", "650mg, 15 tablets", 32.00, 28.00, 80, False),
            ("Cetzine 10", "Cetirizine", "cough-cold", "Cipla", "10mg, 10 tablets", 28.00, 22.00, 240, False),
            ("Pan-D", "Pantoprazole+Domperidone", "tablets", "Alkem", "40mg/30mg, 15 capsules", 199.00, 168.00, 60, True),
            ("Montair LC", "Montelukast+Levocetirizine", "cough-cold", "Cipla", "10mg/5mg, 10 tablets", 192.00, 160.00, 35, True),
            ("Shelcal 500", "Calcium+Vitamin D3", "vitamins", "Torrent", "500mg/250IU, 15 tablets", 131.00, 112.00, 140, False),
            ("Betadine 10%", "Povidone-Iodine", "topicals", "Win-Medicare", "100ml solution", 145.00, 125.00, 45, False),
            ("Omnigel", "Diclofenac", "topicals", "Cipla", "50g tube", 130.00, 110.00, 90, False),
        ],
    },
    {
        "name": "MedPlus Pharmacy — Kankarbagh",
        "email": "medplus@medifinder.demo",
        "phone": "+91 98000 33333",
        "owner_name": "Amitabh Roy",
        "license_number": "DL-PT-20-BRD-00994",
        "city": "Patna", "state": "Bihar", "pincode": "800020",
        "address": "Opposite Colony Park, Main Road, Kankarbagh, Patna",
        "lat": 25.5940, "lng": 85.1550,
        "open_time": "07:30", "close_time": "23:00",
        "is_open_24h": False, "delivery": True,
        "description": "Discount pharmacy store offering flat 15-20% off on all prescription medicines.",
        "status": "Approved",
        "inventory": [
            ("Calpol 650", "Paracetamol", "tablets", "GSK", "650mg, 15 tablets", 31.00, 26.00, 350, False),
            ("Azee 500", "Azithromycin", "tablets", "Cipla", "500mg, 5 tablets", 120.00, 96.00, 75, True),
            ("Moxikind-CV 625", "Amoxicillin+Clavulanic Acid", "tablets", "Mankind", "625mg, 10 tablets", 380.00, 310.00, 40, True),
            ("Zoryl M 2", "Glimepiride+Metformin", "diabetes", "Intas", "2mg/500mg, 15 tablets", 168.00, 138.00, 50, True),
            ("Ecosprin 75", "Aspirin", "cardiac", "USV", "75mg, 14 tablets", 9.50, 7.80, 600, False),
            ("Benadryl Cough Syrup", "Diphenhydramine", "cough-cold", "Johnson & Johnson", "100ml", 125.00, 108.00, 85, False),
            ("Electral Sachet", "Oral Rehydration Salts", "vitamins", "FDC", "21.8g sachet", 22.00, 19.00, 400, False),
        ],
    },
    {
        "name": "Sanjivani Medicos — Bailey Road",
        "email": "sanjivani@medifinder.demo",
        "phone": "+91 98000 44444",
        "owner_name": "Dr. S. K. Verma",
        "license_number": "DL-PT-20-BRD-01123",
        "city": "Patna", "state": "Bihar", "pincode": "800023",
        "address": "Near Jagdeo Path, Bailey Road, Patna",
        "lat": 25.6020, "lng": 85.0870,
        "open_time": "00:00", "close_time": "23:59",
        "is_open_24h": True, "delivery": False,
        "description": "Hospital-adjacent 24/7 chemist. Emergency medicines and rare injections always in stock.",
        "status": "Approved",
        "inventory": [
            ("Dolo 650", "Paracetamol", "tablets", "Micro Labs", "650mg, 15 tablets", 32.00, 32.00, 150, False),
            ("Augmentin 625 Duo", "Amoxicillin+Clavulanic Acid", "tablets", "GSK", "625mg, 10 tablets", 410.00, 395.00, 30, True),
            ("Insulin Lantus Solostar", "Insulin Glargine", "diabetes", "Sanofi", "100IU/ml, 3ml pen", 695.00, 640.00, 15, True),
            ("Dynapar AQ Injection", "Diclofenac", "injections", "Troikaa", "75mg/1ml", 35.00, 30.00, 80, True),
            ("Ondem 4mg", "Ondansetron", "tablets", "Alkem", "4mg, 10 tablets", 52.00, 44.00, 120, False),
            ("Liv 52 DS", "Herbal Liver Formula", "ayurvedic", "Himalaya", "60 tablets", 190.00, 170.00, 95, False),
        ],
    },
    {
        "name": "New City Chemist (Pending Review)",
        "email": "newcity@medifinder.demo",
        "phone": "+91 98000 55555",
        "owner_name": "Ramesh Kumar",
        "license_number": "DL-PT-20-BRD-01999",
        "city": "Patna", "state": "Bihar", "pincode": "800003",
        "address": "Station Road, Patna Junction",
        "lat": 25.6010, "lng": 85.1320,
        "open_time": "09:00", "close_time": "21:00",
        "is_open_24h": False, "delivery": False,
        "description": "Newly opened medicine shop awaiting verification.",
        "status": "Pending",
        "inventory": [
            ("Paracetamol 650", "Paracetamol", "tablets", "Cipla", "650mg, 10 tablets", 30.00, 25.00, 50, False)
        ],
    }
]


def seed_demo_data(force=False):
    """Populate database with rich demo dataset."""
    db = get_db()

    if not force and db.pharmacies.count_documents({}) > 0:
        logger.info("Database already seeded. Skipping.")
        return

    logger.info("Seeding database with demo records...")
    db.users.delete_many({})
    db.pharmacies.delete_many({})
    db.inventory.delete_many({})
    db.reservations.delete_many({})
    db.reviews.delete_many({})
    db.categories.delete_many({})

    # Seed categories
    for name, slug, icon in CATEGORIES:
        db.categories.insert_one({"name": name, "slug": slug, "icon": icon})

    # Seed Demo Customer
    default_pw_hash = hash_password("demo123")
    customer_id = db.users.insert_one({
        "name": "Aarav Sharma",
        "email": "customer@medifinder.demo",
        "phone": "+91 98765 43210",
        "password_hash": default_pw_hash,
        "role": "customer",
        "city": "Patna",
        "lat": 25.6110,
        "lng": 85.1430,
        "created_at": datetime.now(timezone.utc),
    }).inserted_id

    # Seed Pharmacies and Inventory
    for s_idx, shop in enumerate(DEMO_PHARMACIES):
        lat = shop["lat"]
        lng = shop["lng"]
        inventory = shop.pop("inventory", [])

        shop_doc = {
            "name": shop["name"],
            "email": shop["email"],
            "phone": shop["phone"],
            "password_hash": default_pw_hash,
            "owner_name": shop["owner_name"],
            "license_number": shop["license_number"],
            "license_image": None,
            "gst_certificate": None,
            "shop_photo": None,
            "description": shop["description"],
            "address": shop["address"],
            "city": shop["city"],
            "state": shop["state"],
            "pincode": shop["pincode"],
            "location": to_geojson_point(lat, lng),
            "lat": lat,
            "lng": lng,
            "open_time": shop["open_time"],
            "close_time": shop["close_time"],
            "is_open_24h": shop["is_open_24h"],
            "delivery": shop["delivery"],
            "status": shop["status"],
            "rejection_note": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        shop_res = db.pharmacies.insert_one(shop_doc)
        shop_id = str(shop_res.inserted_id)

        # Create Pharmacist user
        db.users.insert_one({
            "name": shop["owner_name"],
            "email": shop["email"],
            "role": "pharmacist",
            "shop_id": shop_id,
            "password_hash": default_pw_hash,
            "created_at": datetime.now(timezone.utc),
        })

        # Add Inventory items
        first_item_id = None
        for item in inventory:
            name, salt, cat, mfr, dosage, mrp, price, stock, rx = item
            inv_res = db.inventory.insert_one({
                "pharmacy_id": shop_id,
                "med_name": name,
                "salt_composition": salt,
                "category_slug": cat,
                "manufacturer": mfr,
                "batch_no": f"BT-{202600 + s_idx * 10}",
                "expiry_date": "2027-12-31",
                "price": price,
                "mrp": mrp,
                "stock_quantity": stock,
                "dosage": dosage,
                "prescription": rx,
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            })
            if not first_item_id:
                first_item_id = str(inv_res.inserted_id)

        # Add Reviews
        if shop["status"] == "Approved":
            db.reviews.insert_one({
                "pharmacy_id": shop_id,
                "customer_id": str(customer_id),
                "customer_name": "Aarav Sharma",
                "rating": 5,
                "comment": "Super quick response! All medicines were in stock and properly sealed.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
            })

            # Add sample reservation for demo customer
            if first_item_id:
                db.reservations.insert_one({
                    "inventory_id": first_item_id,
                    "pharmacy_id": shop_id,
                    "pharmacy_name": shop["name"],
                    "pharmacy_address": shop["address"],
                    "pharmacy_phone": shop["phone"],
                    "med_name": inventory[0][0],
                    "dosage": inventory[0][4],
                    "price": inventory[0][6],
                    "customer_id": str(customer_id),
                    "customer_name": "Aarav Sharma",
                    "customer_phone": "+91 98765 43210",
                    "quantity": 2,
                    "status": "Confirmed" if s_idx == 0 else "Pending",
                    "note": "Urgent requirement for fever.",
                    "held_until": datetime.now(timezone.utc) + timedelta(hours=2),
                    "created_at": datetime.now(timezone.utc) - timedelta(minutes=25),
                    "updated_at": datetime.now(timezone.utc),
                })

    logger.info("Demo database seeded successfully!")


if __name__ == "__main__":
    seed_demo_data(force=True)

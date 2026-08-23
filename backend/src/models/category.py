"""
Medicine Categories taxonomy.
"""
from typing import List, Dict, Tuple

CATEGORIES: List[Tuple[str, str, str]] = [
    ("Tablets & Capsules", "tablets", "bi-capsule"),
    ("Syrups & Liquids", "syrups", "bi-droplet"),
    ("Injections", "injections", "bi-eyedropper"),
    ("Topicals & Creams", "topicals", "bi-bandaid"),
    ("Cough & Cold", "cough-cold", "bi-thermometer"),
    ("Diabetes Care", "diabetes", "bi-activity"),
    ("Cardiac", "cardiac", "bi-heart-pulse"),
    ("Vitamins & Supplements", "vitamins", "bi-capsule-pill"),
    ("Ayurvedic & Herbal", "ayurvedic", "bi-flower1"),
    ("Baby & Maternity", "baby", "bi-emoji-smile"),
    ("Medical Devices", "devices", "bi-broadcast"),
    ("Personal Care", "personal-care", "bi-heart"),
]


def get_category_by_slug(slug: str) -> Dict[str, str]:
    for name, s, icon in CATEGORIES:
        if s == slug:
            return {"name": name, "slug": s, "icon": icon}
    return {"name": "General", "slug": "general", "icon": "bi-capsule"}

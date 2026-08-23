#!/usr/bin/env python3
"""
MediFinder — Main Server Entry Point.
"""
import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.src.app import create_app
from backend.src.config import settings
from backend.src.seed import seed_demo_data

app = create_app()

if __name__ == "__main__":
    # Automatically seed initial demo data if database is fresh
    with app.app_context():
        seed_demo_data()

    print("=" * 60)
    print(" MediFinder 2.0 — Geospatial Medicine & Pharmacy Engine")
    print(f" Environment : {settings.ENVIRONMENT}")
    print(f" Database    : {settings.MONGODB_URI}")
    print(f" REST API    : http://{settings.HOST}:{settings.PORT}/api/v1")
    print(f" Swagger Docs: http://{settings.HOST}:{settings.PORT}/api/v1/docs")
    print(f" Web Portal  : http://{settings.HOST}:{settings.PORT}/")
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=settings.PORT,
        debug=settings.DEBUG,
    )

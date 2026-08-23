# 🏥 MediFinder 2.0 — Geospatial Medicine & Pharmacy Availability Platform

[![CI/CD Pipeline](https://github.com/krsidhantaryan-ux/Medi-finder-arena/actions/workflows/ci.yml/badge.svg)](https://github.com/krsidhantaryan-ux/Medi-finder-arena/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Database: MongoDB](https://img.shields.io/badge/database-MongoDB%207.0-green.svg)](https://www.mongodb.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

An enterprise-grade, scalable platform for real-time medicine availability search, geo-proximity pharmacy location with **MongoDB 2dsphere spatial indexing**, generic salt substitute discovery, and atomic medicine reservation workflows.

---

## 🌟 Key Architecture & Scalability Highlights

* **Scalable NoSQL Engine (MongoDB 7.0)**:
  * **2dsphere Spatial Indexing**: Sub-millisecond geographic proximity queries (`$nearSphere`, `$geoWithin`) across thousands of pharmacies.
  * **Fuzzy & Text Search Indexing**: Instant typo-tolerant medicine brand & generic salt matching.
  * **Atomic Inventory Decrements**: Prevents race conditions and overselling using atomic update pipelines and guaranteed 2-hour hold reservation timers.
  * **Connection Pooling**: PyMongo client pool supporting high concurrent write and read traffic.
  * **Zero-Config Resilient Adapter**: Automatically falls back to an embedded in-memory MongoDB store if run locally without a MongoDB daemon, ensuring 100% test reproducibility.
* **Layered Clean Architecture**:
  * Strict separation between **API Controllers (Blueprints)**, **Business Services**, and **Domain Data Models (Pydantic)**.
  * Uniform API envelope standard (`{ success, status_code, message, data, meta }`).
* **Interactive OpenAPI 3.0 & Swagger UI**:
  * Real-time interactive documentation available out of the box at `/api/v1/docs`.
* **Containerized Deployment**:
  * Multi-stage `Dockerfile` and production-ready `docker-compose.yml` with health checks and volume persistence.

---

## 📂 Professional Repository Structure

```
Medi-finder-arena/
├── .github/
│   └── workflows/
│       └── ci.yml                 # Automated CI/CD test and linting pipeline
├── backend/
│   ├── src/
│   │   ├── config.py              # Pydantic Settings & environment variables
│   │   ├── app.py                 # Application Factory (create_app)
│   │   ├── seed.py                # Database seed generator with realistic datasets
│   │   ├── core/                  # Core infrastructure
│   │   │   ├── database.py        # MongoDB connection manager & 2dsphere indexing
│   │   │   ├── security.py        # bcrypt hashing, JWT access/refresh tokens, RBAC decorators
│   │   │   ├── exceptions.py      # Structured exception hierarchy
│   │   │   ├── responses.py       # Consistent JSON response envelope
│   │   │   └── utils.py           # GeoJSON coordinates, haversine distance & upload handlers
│   │   ├── models/                # Domain models & Pydantic validation schemas
│   │   │   ├── user.py            # Customer, Pharmacist, Admin models
│   │   │   ├── pharmacy.py        # Pharmacy entity with GeoJSON Point & status
│   │   │   ├── inventory.py       # Medicine catalog with stock, pricing, salt, dosage
│   │   │   ├── reservation.py     # Atomic reservation lifecycle model
│   │   │   ├── review.py          # Customer ratings & reviews model
│   │   │   ├── category.py        # Healthcare category taxonomy
│   │   │   └── audit_log.py       # Governance audit logging schema
│   │   ├── services/              # Pure Business Logic Layer
│   │   │   ├── auth_service.py    # Authentication, JWT issuance, password security
│   │   │   ├── medicine_service.py# Search, fuzzy matching, salt substitute engine
│   │   │   ├── pharmacy_service.py# Geo-nearby pharmacy locator & inventory CRUD
│   │   │   ├── reservation_service.py # Atomic reservations & stock release pipeline
│   │   │   ├── review_service.py  # Review submissions & store rating aggregator
│   │   │   └── admin_service.py   # Pharmacy verification & platform metrics
│   │   ├── blueprints/            # Route Controllers
│   │   │   ├── api/v1/            # Versioned RESTful API
│   │   │   │   ├── auth.py        # POST /api/v1/auth/*
│   │   │   │   ├── medicines.py   # GET /api/v1/medicines/*
│   │   │   │   ├── pharmacies.py  # GET, POST, PUT, DELETE /api/v1/pharmacies/*
│   │   │   │   ├── reservations.py# POST /api/v1/reservations/*
│   │   │   │   ├── reviews.py     # POST, GET /api/v1/reviews/*
│   │   │   │   ├── admin.py       # POST, GET /api/v1/admin/*
│   │   │   │   └── docs.py        # GET /api/v1/docs (Swagger UI)
│   │   │   └── web/               # Server-Rendered Web Portals
│   │   │       ├── public.py      # Homepage, search map, pharmacy profiles
│   │   │       ├── customer.py    # Patient reservations & account portal
│   │   │       ├── pharmacy.py    # Pharmacist inventory dashboard & stock pipeline
│   │   │       └── admin.py       # Admin verification dashboard & audit logs
│   │   ├── static/                # Design system CSS, JS & Leaflet assets
│   │   └── templates/             # Modular Jinja2 web templates
│   ├── tests/                     # Automated Pytest Suite
│   ├── requirements.txt           # Production dependencies
│   └── requirements-dev.txt       # Development & testing dependencies
├── docker-compose.yml              # Multi-container MongoDB + Backend stack
├── Dockerfile                      # Production multi-stage Docker build
├── Makefile                        # Ergonomic developer CLI
├── pytest.ini                      # Test runner configuration
├── run.py                          # Application entry point
├── .env.example                    # Environment template
└── README.md                       # Documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
* Python 3.11+
* (Optional) Docker & Docker Compose
* (Optional) MongoDB 7.0 instance or MongoDB Atlas cluster

### 2. Local Installation

```bash
# Clone the repository
git clone https://github.com/krsidhantaryan-ux/Medi-finder-arena.git
cd Medi-finder-arena

# Install dependencies
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt

# Copy environment variables
cp .env.example .env

# Run automated tests
pytest backend/tests -v

# Start the server
python3 run.py
```

Open your browser at:
* **Web Portal:** [http://localhost:5000](http://localhost:5000)
* **Interactive Swagger UI:** [http://localhost:5000/api/v1/docs](http://localhost:5000/api/v1/docs)
* **Health Check:** [http://localhost:5000/api/v1/health](http://localhost:5000/api/v1/health)

---

## 🐳 Docker Deployment

To launch the full containerized stack (MongoDB 7.0 Database + MediFinder Backend):

```bash
docker-compose up --build -d
```

---

## 🧪 Automated Testing

MediFinder comes with a comprehensive test suite covering authentication, geospatial search, inventory CRUD, atomic reservations, and admin verification:

```bash
# Run pytest with verbose summary
pytest backend/tests -v --tb=short
```

---

## 🔑 Default Demo Accounts

| Role | Username / Email | Password | Access Area |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin` | `Admin@MediFinder2026!` | `/admin` |
| **Pharmacy Partner** | `apollo@medifinder.demo` | `demo123` | `/pharmacy/login` |
| **Patient / Customer** | `customer@medifinder.demo` | `demo123` | `/account/login` |

---

## 📡 REST API Documentation

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register/customer` | Register patient account | No |
| `POST` | `/api/v1/auth/login/customer` | Patient JWT login | No |
| `POST` | `/api/v1/auth/login/pharmacy` | Pharmacy JWT login | No |
| `POST` | `/api/v1/auth/login/admin` | Admin JWT login | No |
| `GET` | `/api/v1/medicines/search` | Proximity & salt medicine search | No |
| `GET` | `/api/v1/medicines/autocomplete` | Live search suggestions | No |
| `GET` | `/api/v1/pharmacies/nearby` | Geospatial nearby pharmacy search | No |
| `GET` | `/api/v1/pharmacies/<id>` | Pharmacy profile & stock catalog | No |
| `POST` | `/api/v1/pharmacies/<id>/inventory` | Add medicine to inventory | Pharmacist / Admin |
| `PUT` | `/api/v1/pharmacies/<id>/inventory/<item_id>` | Update stock or price | Pharmacist / Admin |
| `DELETE` | `/api/v1/pharmacies/<id>/inventory/<item_id>` | Remove inventory item | Pharmacist / Admin |
| `POST` | `/api/v1/reservations` | Create atomic 2-hour reservation | No / Customer |
| `POST` | `/api/v1/reservations/<id>/<action>` | Confirm, Collect, or Cancel | Dynamic RBAC |
| `POST` | `/api/v1/reviews/<shop_id>` | Submit pharmacy rating & review | No / Customer |
| `GET` | `/api/v1/admin/metrics` | System statistics & counts | Admin |
| `POST` | `/api/v1/admin/pharmacy/<id>/<action>` | Approve or reject pharmacy | Admin |

---

## 🛡️ License

This project is licensed under the MIT License.

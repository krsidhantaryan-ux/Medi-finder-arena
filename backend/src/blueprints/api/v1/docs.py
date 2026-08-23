"""
Interactive Swagger UI and OpenAPI 3.0 Documentation.
"""
from flask import Blueprint, jsonify, render_template_string

docs_api = Blueprint("docs_api", __name__)

OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "MediFinder RESTful API",
        "description": "Scalable Geospatial Medicine Availability and Pharmacy Inventory System powered by MongoDB.",
        "version": "2.0.0",
        "contact": {
            "name": "MediFinder Engineering",
            "url": "https://github.com/krsidhantaryan-ux/Medi-finder-arena"
        }
    },
    "servers": [
        {"url": "/api/v1", "description": "Current API Server"}
    ],
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    },
    "paths": {
        "/auth/register/customer": {
            "post": {
                "summary": "Register a new customer",
                "tags": ["Authentication"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["name", "email", "password"],
                                "properties": {
                                    "name": {"type": "string", "example": "Aarav Sharma"},
                                    "email": {"type": "string", "example": "aarav@example.com"},
                                    "password": {"type": "string", "example": "secret123"},
                                    "phone": {"type": "string", "example": "+91 9876543210"}
                                }
                            }
                        }
                    }
                },
                "responses": {"201": {"description": "Customer registered"}}
            }
        },
        "/auth/login/customer": {
            "post": {
                "summary": "Login customer",
                "tags": ["Authentication"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["email", "password"],
                                "properties": {
                                    "email": {"type": "string", "example": "customer@medifinder.demo"},
                                    "password": {"type": "string", "example": "customer123"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "JWT tokens issued"}}
            }
        },
        "/medicines/search": {
            "get": {
                "summary": "Search medicines by query, salt, location, and filters",
                "tags": ["Medicines"],
                "parameters": [
                    {"name": "q", "in": "query", "schema": {"type": "string"}},
                    {"name": "salt", "in": "query", "schema": {"type": "string"}},
                    {"name": "lat", "in": "query", "schema": {"type": "number", "example": 25.6110}},
                    {"name": "lng", "in": "query", "schema": {"type": "number", "example": 85.1430}},
                    {"name": "radius", "in": "query", "schema": {"type": "number", "example": 15.0}},
                    {"name": "in_stock", "in": "query", "schema": {"type": "boolean"}},
                    {"name": "open_24h", "in": "query", "schema": {"type": "boolean"}},
                    {"name": "delivery", "in": "query", "schema": {"type": "boolean"}}
                ],
                "responses": {"200": {"description": "Matching medicines with distance and stock"}}
            }
        },
        "/medicines/autocomplete": {
            "get": {
                "summary": "Live autocomplete suggestions",
                "tags": ["Medicines"],
                "parameters": [
                    {"name": "q", "in": "query", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "List of suggestions"}}
            }
        },
        "/pharmacies/nearby": {
            "get": {
                "summary": "Find nearby pharmacies sorted by distance",
                "tags": ["Pharmacies"],
                "parameters": [
                    {"name": "lat", "in": "query", "schema": {"type": "number", "example": 25.6110}},
                    {"name": "lng", "in": "query", "schema": {"type": "number", "example": 85.1430}},
                    {"name": "radius", "in": "query", "schema": {"type": "number", "example": 15.0}}
                ],
                "responses": {"200": {"description": "List of pharmacies"}}
            }
        },
        "/reservations": {
            "post": {
                "summary": "Create atomic medicine reservation with 2-hour hold",
                "tags": ["Reservations"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["inventory_id", "pharmacy_id", "customer_phone"],
                                "properties": {
                                    "inventory_id": {"type": "string"},
                                    "pharmacy_id": {"type": "string"},
                                    "customer_phone": {"type": "string", "example": "+91 98000 11111"},
                                    "quantity": {"type": "integer", "example": 1}
                                }
                            }
                        }
                    }
                },
                "responses": {"201": {"description": "Reservation confirmed and stock reserved"}}
            }
        }
    }
}

SWAGGER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MediFinder API Docs</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    <link rel="icon" type="image/svg+xml" href="/static/img/favicon.svg">
    <style>
        body { margin: 0; background: #0f172a; }
        .swagger-ui .topbar { display: none; }
        .swagger-ui { background: #fff; padding: 20px; border-radius: 12px; margin: 20px auto; max-width: 1200px; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
        window.onload = function() {
            SwaggerUIBundle({
                url: "/api/v1/openapi.json",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ]
            });
        };
    </script>
</body>
</html>
"""


@docs_api.route("/docs")
def swagger_ui():
    return render_template_string(SWAGGER_HTML)


@docs_api.route("/openapi.json")
def openapi_json():
    return jsonify(OPENAPI_SPEC)

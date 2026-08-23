"""
Pytest configuration and test fixtures for MediFinder.
"""
import pytest
from backend.src.app import create_app
from backend.src.core.database import get_db
from backend.src.seed import seed_demo_data


@pytest.fixture(scope="session")
def app():
    """Create test application."""
    test_app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-12345",
        "JWT_SECRET_KEY": "test-jwt-secret-key-12345",
    })
    with test_app.app_context():
        seed_demo_data(force=True)
    return test_app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Database instance for tests."""
    with app.app_context():
        return get_db()

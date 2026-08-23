"""
Unit & Integration tests for Authentication API and Services.
"""
def test_customer_registration_and_login(client):
    # 1. Register customer
    reg_res = client.post("/api/v1/auth/register/customer", json={
        "name": "Test Customer",
        "email": "testcust@example.com",
        "phone": "+91 9123456789",
        "password": "password123",
        "city": "Patna",
    })
    assert reg_res.status_code == 201
    reg_json = reg_res.get_json()
    assert reg_json["success"] is True
    assert "access_token" in reg_json["data"]

    # 2. Login with valid credentials
    login_res = client.post("/api/v1/auth/login/customer", json={
        "email": "testcust@example.com",
        "password": "password123",
    })
    assert login_res.status_code == 200
    login_json = login_res.get_json()
    assert login_json["success"] is True
    token = login_json["data"]["access_token"]

    # 3. Access authenticated me endpoint
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.get_json()["data"]["role"] == "customer"


def test_admin_login(client):
    res = client.post("/api/v1/auth/login/admin", json={
        "username": "admin",
        "password": "Admin@MediFinder2026!",
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["user"]["role"] == "admin"

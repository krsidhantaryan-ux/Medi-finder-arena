"""
Unit & Integration tests for Atomic Reservations and Stock Lifecycle.
"""
def test_create_and_manage_reservation(client, db):
    shop = db.pharmacies.find_one({"status": "Approved"})
    assert shop is not None
    shop_id = str(shop["_id"])

    item = db.inventory.find_one({"pharmacy_id": shop_id, "stock_quantity": {"$gt": 5}})
    assert item is not None
    item_id = str(item["_id"])
    initial_stock = item["stock_quantity"]

    # 1. Create reservation
    res = client.post("/api/v1/reservations", json={
        "inventory_id": item_id,
        "pharmacy_id": shop_id,
        "customer_phone": "+91 99999 88888",
        "customer_name": "Test Reserver",
        "quantity": 2,
        "note": "Urgent hold",
    })
    assert res.status_code == 201
    res_data = res.get_json()["data"]
    reservation_id = res_data["id"]
    assert res_data["status"] == "Pending"

    # Verify stock decremented
    updated_item = db.inventory.find_one({"_id": item["_id"]})
    assert updated_item["stock_quantity"] == initial_stock - 2

    # 2. Cancel reservation and verify stock replenished
    admin_login = client.post("/api/v1/auth/login/admin", json={
        "username": "admin",
        "password": "Admin@MediFinder2026!",
    }).get_json()
    admin_token = admin_login["data"]["access_token"]

    cancel_res = client.post(
        f"/api/v1/reservations/{reservation_id}/cancel",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert cancel_res.status_code == 200

    replenished_item = db.inventory.find_one({"_id": item["_id"]})
    assert replenished_item["stock_quantity"] == initial_stock

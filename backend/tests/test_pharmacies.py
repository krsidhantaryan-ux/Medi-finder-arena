"""
Unit & Integration tests for Pharmacy Nearby, Profile & Inventory Management.
"""
def test_nearby_pharmacies(client):
    res = client.get("/api/v1/pharmacies/nearby?lat=25.6110&lng=85.1430&radius=20")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["data"]) > 0


def test_pharmacy_details_and_inventory(client, db):
    shop = db.pharmacies.find_one({"status": "Approved"})
    assert shop is not None
    shop_id = str(shop["_id"])

    res = client.get(f"/api/v1/pharmacies/{shop_id}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == shop["name"]
    assert "inventory" in data["data"]

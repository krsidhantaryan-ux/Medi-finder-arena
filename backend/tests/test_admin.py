"""
Unit & Integration tests for Admin Governance & Metrics.
"""
def test_admin_metrics_and_approval(client, db):
    # Admin login
    admin_login = client.post("/api/v1/auth/login/admin", json={
        "username": "admin",
        "password": "Admin@MediFinder2026!",
    }).get_json()
    token = admin_login["data"]["access_token"]

    # 1. Fetch dashboard metrics
    metrics_res = client.get("/api/v1/admin/metrics", headers={"Authorization": f"Bearer {token}"})
    assert metrics_res.status_code == 200
    metrics_data = metrics_res.get_json()["data"]
    assert "counts" in metrics_data
    assert metrics_data["counts"]["total_shops"] > 0

    # 2. Approve/reject pharmacy
    pending_shop = db.pharmacies.find_one({"status": "Pending"})
    if pending_shop:
        shop_id = str(pending_shop["_id"])
        approve_res = client.post(
            f"/api/v1/admin/pharmacy/{shop_id}/approve",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert approve_res.status_code == 200
        assert approve_res.get_json()["data"]["status"] == "Approved"

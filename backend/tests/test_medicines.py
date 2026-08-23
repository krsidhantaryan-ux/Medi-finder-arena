"""
Unit & Integration tests for Medicine Search, Salt Matching & Autocomplete.
"""
def test_search_medicines(client):
    res = client.get("/api/v1/medicines/search?q=Dolo")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["data"]) > 0
    assert any("Dolo" in m["med_name"] for m in data["data"])


def test_autocomplete_suggestions(client):
    res = client.get("/api/v1/medicines/autocomplete?q=Par")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["data"]) > 0

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_list_items():
    res = client.get("/api/items/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 2


def test_get_item():
    res = client.get("/api/items/1")
    assert res.status_code == 200
    assert res.json()["id"] == 1


def test_get_item_not_found():
    res = client.get("/api/items/9999")
    assert res.status_code == 404


def test_create_item():
    res = client.post("/api/items/", json={"name": "Test Item", "description": "Created in test"})
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Test Item"
    assert "id" in data


def test_delete_item():
    create_res = client.post("/api/items/", json={"name": "To Delete", "description": ""})
    item_id = create_res.json()["id"]
    del_res = client.delete(f"/api/items/{item_id}")
    assert del_res.status_code == 204
    get_res = client.get(f"/api/items/{item_id}")
    assert get_res.status_code == 404


def test_stats():
    res = client.get("/api/items/stats/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_items" in data
    assert "items_with_description" in data
    assert "items_without_description" in data
    assert data["total_items"] == data["items_with_description"] + data["items_without_description"]

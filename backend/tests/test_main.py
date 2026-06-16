import pytest
import fakeredis
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models import Item
import app.cache as cache_module

SQLITE_URL = "sqlite:///./test_run.db"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db(monkeypatch):
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add_all([
        Item(name="Item One", description="First sample item"),
        Item(name="Item Two", description="Second sample item"),
    ])
    db.commit()
    db.close()
    app.dependency_overrides[get_db] = override_get_db

    fake_redis = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(cache_module, "_client", fake_redis)

    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


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


def test_list_items_cached():
    client.get("/api/items/")
    res = client.get("/api/items/")
    assert res.status_code == 200
    assert len(res.json()) >= 2


def test_get_item():
    items = client.get("/api/items/").json()
    item_id = items[0]["id"]
    res = client.get(f"/api/items/{item_id}")
    assert res.status_code == 200
    assert res.json()["id"] == item_id


def test_get_item_not_found():
    res = client.get("/api/items/9999")
    assert res.status_code == 404


def test_create_item():
    res = client.post("/api/items/", json={"name": "Test Item", "description": "Created in test"})
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Test Item"
    assert "id" in data


def test_create_invalidates_cache():
    client.get("/api/items/")
    client.post("/api/items/", json={"name": "New Item", "description": "fresh"})
    res = client.get("/api/items/")
    names = [i["name"] for i in res.json()]
    assert "New Item" in names


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

import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"

def test_get_products(client):
    resp = client.get("/api/products")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "products" in data
    assert data["count"] == 8

def test_get_product_detail(client):
    resp = client.get("/api/products/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Laptop"

def test_add_to_cart(client):
    resp = client.post("/api/cart", json={"session_id": "test1", "product_id": "1", "qty": 2})
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["cart"]) == 1
    assert data["cart"][0]["qty"] == 2

def test_remove_from_cart(client):
    client.post("/api/cart", json={"session_id": "test2", "product_id": "2", "qty": 1})
    resp = client.delete("/api/cart/2?session_id=test2")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["cart"]) == 0

def test_create_order(client):
    client.post("/api/cart", json={"session_id": "test3", "product_id": "3", "qty": 1})
    resp = client.post("/api/orders", json={"session_id": "test3", "shipping_address": "123 Main St"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "pending"
    assert data["total"] == 149.99

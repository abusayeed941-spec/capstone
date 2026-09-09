"""
E-Commerce Platform — Flask REST API Backend
Endpoints: /api/products, /api/cart, /api/orders, /api/admin/products
"""

import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- Configuration from environment ---
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", 3306))
DB_USER = os.environ.get("DB_USER", "ecommerce")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "secret")
DB_NAME = os.environ.get("DB_NAME", "ecommerce_db")

# --- In-memory "database" (for demo; replace with MySQL in production) ---
# In production, use pymysql or SQLAlchemy with the MySQL connection above.
products_db = {
    "products": [
        {"id": "1", "name": "Laptop", "price": 999.99, "category": "Electronics", "stock": 50, "image": "laptop.jpg"},
        {"id": "2", "name": "Smartphone", "price": 699.99, "category": "Electronics", "stock": 100, "image": "phone.jpg"},
        {"id": "3", "name": "Headphones", "price": 149.99, "category": "Electronics", "stock": 200, "image": "headphones.jpg"},
        {"id": "4", "name": "Desk Chair", "price": 299.99, "category": "Furniture", "stock": 30, "image": "chair.jpg"},
        {"id": "5", "name": "Desk Lamp", "price": 49.99, "category": "Furniture", "stock": 150, "image": "lamp.jpg"},
        {"id": "6", "name": "Coffee Maker", "price": 89.99, "category": "Appliances", "stock": 75, "image": "coffee.jpg"},
        {"id": "7", "name": "Notebook", "price": 12.99, "category": "Office", "stock": 500, "image": "notebook.jpg"},
        {"id": "8", "name": "Wireless Mouse", "price": 29.99, "category": "Electronics", "stock": 300, "image": "mouse.jpg"},
    ]
}

# Simulated cart + orders (replace with DB in production)
carts = {}  # session_id → list of items
orders = {}  # order_id → order details

# --- Helper ---
def get_next_id():
    return str(uuid.uuid4())[:8]

# --- Routes ---
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()}), 200

@app.route("/api/products", methods=["GET"])
def get_products():
    category = request.args.get("category")
    if category:
        items = [p for p in products_db["products"] if p["category"] == category]
    else:
        items = products_db["products"]
    return jsonify({"products": items, "count": len(items)}), 200

@app.route("/api/products/<product_id>", methods=["GET"])
def get_product(product_id):
    for p in products_db["products"]:
        if p["id"] == product_id:
            return jsonify(p), 200
    return jsonify({"error": "Product not found"}), 404

@app.route("/api/cart", methods=["GET"])
def get_cart():
    session_id = request.args.get("session_id", "default")
    cart = carts.get(session_id, [])
    return jsonify({"cart": cart, "total": sum(item["price"] * item["qty"] for item in cart)}), 200

@app.route("/api/cart", methods=["POST"])
def add_to_cart():
    data = request.get_json()
    session_id = data.get("session_id", "default")
    product_id = data.get("product_id")
    qty = data.get("qty", 1)

    product = None
    for p in products_db["products"]:
        if p["id"] == product_id:
            product = p
            break
    if not product:
        return jsonify({"error": "Product not found"}), 404
    if product["stock"] < qty:
        return jsonify({"error": "Insufficient stock"}), 400

    cart = carts.get(session_id, [])
    # Update quantity if already in cart
    for item in cart:
        if item["id"] == product_id:
            item["qty"] += qty
            break
    else:
        cart.append({"id": product["id"], "name": product["name"], "price": product["price"], "qty": qty, "image": product["image"]})

    carts[session_id] = cart
    return jsonify({"cart": cart, "total": sum(item["price"] * item["qty"] for item in cart)}), 200

@app.route("/api/cart/<product_id>", methods=["DELETE"])
def remove_from_cart(product_id):
    session_id = request.args.get("session_id", "default")
    cart = carts.get(session_id, [])
    carts[session_id] = [item for item in cart if item["id"] != product_id]
    return jsonify({"cart": carts[session_id], "total": sum(item["price"] * item["qty"] for item in carts[session_id])}), 200

@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    session_id = data.get("session_id", "default")
    cart = carts.get(session_id, [])
    if not cart:
        return jsonify({"error": "Cart is empty"}), 400

    order_id = get_next_id()
    order = {
        "order_id": order_id,
        "session_id": session_id,
        "items": cart,
        "total": sum(item["price"] * item["qty"] for item in cart),
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "shipping_address": data.get("shipping_address", ""),
    }
    orders[order_id] = order
    carts[session_id] = []  # clear cart
    return jsonify(order), 201

@app.route("/api/orders/<order_id>", methods=["GET"])
def get_order(order_id):
    order = orders.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order), 200

@app.route("/api/admin/products", methods=["POST"])
def admin_add_product():
    """Admin: add a new product (in production, protect with auth)"""
    data = request.get_json()
    new_product = {
        "id": get_next_id(),
        "name": data.get("name"),
        "price": float(data.get("price", 0)),
        "category": data.get("category", "General"),
        "stock": int(data.get("stock", 0)),
        "image": data.get("image", "default.jpg"),
    }
    products_db["products"].append(new_product)
    return jsonify(new_product), 201

@app.route("/api/admin/products", methods=["GET"])
def admin_list_products():
    return jsonify(products_db), 200

# --- Run ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

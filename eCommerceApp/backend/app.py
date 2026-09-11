"""
E-Commerce Platform — Flask REST API + Frontend (single app)
All frontend routes served inline. Backend API at /api/*.
Frontend at / (index), /cart, /admin, etc.
"""

import os
import json
import uuid
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS

app = Flask(__name__, static_folder=None)
CORS(app)

# --- Configuration ---
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", 3306))
DB_USER = os.environ.get("DB_USER", "ecommerce")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "secret")
DB_NAME = os.environ.get("DB_NAME", "ecommerce_db")

# --- Products with emoji icons ---
PRODUCTS_WITH_EMOJI = {
    "1": "💻", "2": "📱", "3": "🎧", "4": "🪑",
    "5": "💡", "6": "☕", "7": "📓", "8": "🖱️",
}

frontend_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopOnline — E-Commerce Platform</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --primary: #6c5ce7;
            --primary-dark: #5a4bd1;
            --secondary: #00cec9;
            --accent: #fd79a8;
            --accent2: #fdcb6e;
            --bg: #0a0a1a;
            --card-bg: #1a1a2e;
            --card-border: #2d2d44;
            --text: #e0e0f0;
            --text-muted: #8888aa;
            --success: #00b894;
            --danger: #e17055;
            --gradient-1: linear-gradient(135deg, #6c5ce7, #a29bfe);
            --gradient-2: linear-gradient(135deg, #00cec9, #55efc4);
            --gradient-3: linear-gradient(135deg, #fd79a8, #e84393);
            --gradient-4: linear-gradient(135deg, #fdcb6e, #f39c12);
            --shadow: 0 8px 32px rgba(0,0,0,0.3);
            --shadow-hover: 0 12px 48px rgba(108,92,231,0.25);
        }

        body {
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* Animated background */
        body::before {
            content: "";
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background:
                radial-gradient(ellipse at 20% 20%, rgba(108,92,231,0.12) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(0,206,201,0.10) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 50%, rgba(253,121,168,0.08) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }

        /* Header */
        .header {
            background: rgba(26,26,46,0.85);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--card-border);
            padding: 16px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
            animation: slideDown 0.5s ease;
        }

        @keyframes slideDown {
            from { transform: translateY(-100%); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        .logo {
            display: flex; align-items: center; gap: 12px;
        }

        .logo-icon {
            width: 42px; height: 42px;
            background: var(--gradient-1);
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 22px;
            box-shadow: 0 4px 15px rgba(108,92,231,0.4);
        }

        .logo h1 {
            font-size: 22px;
            font-weight: 800;
            background: var(--gradient-1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.5px;
        }

        .nav-links { display: flex; gap: 8px; }
        .nav-links a {
            color: var(--text-muted);
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .nav-links a:hover {
            color: var(--text);
            background: rgba(108,92,231,0.15);
        }
        .nav-links a.active {
            color: var(--primary);
            background: rgba(108,92,231,0.15);
        }

        /* Container */
        .container {
            max-width: 1300px;
            margin: 0 auto;
            padding: 30px 20px;
            position: relative;
            z-index: 1;
        }

        /* Section headers */
        .section-title {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .section-title .badge {
            font-size: 13px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 20px;
            background: var(--gradient-1);
            color: white;
        }

        /* Product Grid */
        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 24px;
            margin-bottom: 40px;
        }

        .product-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            cursor: pointer;
        }

        .product-card::before {
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: var(--gradient-1);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .product-card:hover {
            transform: translateY(-6px);
            box-shadow: var(--shadow-hover);
            border-color: rgba(108,92,231,0.3);
        }

        .product-card:hover::before {
            opacity: 1;
        }

        .product-card .emoji-icon {
            font-size: 64px;
            margin-bottom: 16px;
            display: block;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
            transition: transform 0.3s ease;
        }

        .product-card:hover .emoji-icon {
            transform: scale(1.1) rotate(-5deg);
        }

        .product-card h3 {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 6px;
            color: var(--text);
        }

        .product-card .category-tag {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 3px 10px;
            border-radius: 12px;
            display: inline-block;
            margin-bottom: 10px;
        }

        .cat-electronics { background: rgba(108,92,231,0.2); color: #a29bfe; }
        .cat-furniture { background: rgba(0,206,201,0.2); color: #55efc4; }
        .cat-appliances { background: rgba(253,121,168,0.2); color: #fd79a8; }
        .cat-office { background: rgba(253,203,110,0.2); color: #fdcb6e; }

        .product-card .price {
            font-size: 24px;
            font-weight: 800;
            color: #fff;
            margin-bottom: 4px;
            text-shadow: 0 2px 10px rgba(108,92,231,0.3);
        }

        .product-card .price .currency {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-muted);
            margin-right: 2px;
        }

        .product-card .stock {
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
        }

        .stock-dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            display: inline-block;
        }
        .stock-high { background: var(--success); }
        .stock-medium { background: var(--accent2); }
        .stock-low { background: var(--danger); }

        .product-card .btn-add {
            padding: 10px 28px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            font-family: inherit;
            transition: all 0.3s ease;
            background: var(--gradient-1);
            color: white;
            width: 100%;
            position: relative;
            overflow: hidden;
        }

        .product-card .btn-add::after {
            content: "";
            position: absolute;
            top: 50%; left: 50%;
            width: 0; height: 0;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.4s ease, height 0.4s ease;
        }

        .product-card .btn-add:active::after {
            width: 200px; height: 200px;
        }

        .product-card .btn-add:hover {
            transform: scale(1.03);
            box-shadow: 0 4px 20px rgba(108,92,231,0.4);
        }

        .product-card .btn-add:active {
            transform: scale(0.97);
        }

        /* Cart Section */
        .cart-section {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 28px;
            margin-top: 30px;
            box-shadow: var(--shadow);
            animation: fadeInUp 0.5s ease;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .cart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--card-border);
        }

        .cart-header h2 {
            font-size: 22px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .cart-count-badge {
            background: var(--gradient-3);
            color: white;
            font-size: 12px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 12px;
        }

        .cart-table {
            width: 100%;
            border-collapse: collapse;
        }

        .cart-table th {
            text-align: left;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            padding: 10px 12px;
            border-bottom: 1px solid var(--card-border);
        }

        .cart-table td {
            padding: 12px;
            border-bottom: 1px solid rgba(45,45,68,0.5);
            vertical-align: middle;
        }

        .cart-item-name {
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .cart-item-emoji {
            font-size: 24px;
        }

        .cart-item-price {
            font-weight: 700;
            color: #fff;
        }

        .cart-item-qty {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .qty-btn {
            width: 28px; height: 28px;
            border: 1px solid var(--card-border);
            background: rgba(108,92,231,0.1);
            color: var(--text);
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            font-family: inherit;
        }

        .qty-btn:hover {
            background: rgba(108,92,231,0.25);
            border-color: var(--primary);
        }

        .qty-value {
            font-weight: 600;
            min-width: 24px;
            text-align: center;
        }

        .cart-item-total {
            font-weight: 700;
            color: #fff;
            font-size: 15px;
        }

        .btn-remove {
            background: rgba(225,112,85,0.15);
            color: var(--danger);
            border: 1px solid rgba(225,112,85,0.3);
            border-radius: 6px;
            padding: 6px 12px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.2s ease;
            font-family: inherit;
        }

        .btn-remove:hover {
            background: rgba(225,112,85,0.25);
            border-color: var(--danger);
        }

        .cart-summary {
            margin-top: 20px;
            padding: 20px;
            background: rgba(108,92,231,0.08);
            border-radius: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }

        .cart-total-label {
            font-size: 16px;
            color: var(--text-muted);
            font-weight: 500;
        }

        .cart-total-value {
            font-size: 32px;
            font-weight: 800;
            color: #fff;
            text-shadow: 0 2px 10px rgba(108,92,231,0.3);
        }

        .btn-checkout {
            padding: 14px 32px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 700;
            font-family: inherit;
            background: var(--gradient-2);
            color: #0a0a1a;
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(0,206,201,0.3);
        }

        .btn-checkout:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0,206,201,0.4);
        }

        .btn-checkout:active {
            transform: translateY(0);
        }

        .btn-checkout:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        /* Alert */
        .alert {
            padding: 12px 16px;
            border-radius: 10px;
            margin-bottom: 15px;
            font-size: 14px;
            font-weight: 500;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .alert-success {
            background: rgba(0,184,148,0.15);
            color: #55efc4;
            border: 1px solid rgba(0,184,148,0.3);
        }

        .alert-error {
            background: rgba(225,112,85,0.15);
            color: #e17055;
            border: 1px solid rgba(225,112,85,0.3);
        }

        /* Order Form */
        .order-form {
            margin-top: 20px;
            padding: 20px;
            background: rgba(0,206,201,0.06);
            border-radius: 12px;
            border: 1px solid rgba(0,206,201,0.15);
        }

        .order-form h3 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #55efc4;
        }

        .order-form textarea {
            width: 100%;
            padding: 10px 14px;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            background: rgba(255,255,255,0.05);
            color: var(--text);
            font-family: inherit;
            font-size: 14px;
            resize: vertical;
            min-height: 80px;
            transition: border-color 0.2s ease;
        }

        .order-form textarea:focus {
            outline: none;
            border-color: var(--secondary);
        }

        .btn-place-order {
            margin-top: 12px;
            padding: 12px 28px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 700;
            font-family: inherit;
            background: var(--gradient-3);
            color: white;
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(253,121,168,0.3);
        }

        .btn-place-order:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(253,121,168,0.4);
        }

        /* Admin Panel */
        .admin-panel {
            margin-top: 30px;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 28px;
            box-shadow: var(--shadow);
            animation: fadeInUp 0.5s ease;
        }

        .admin-panel h2 {
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .admin-panel h2 .icon {
            font-size: 24px;
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            margin-bottom: 6px;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .form-group input, .form-group select {
            width: 100%;
            padding: 10px 14px;
            border: 1px solid var(--card-border);
            border-radius: 10px;
            background: rgba(255,255,255,0.05);
            color: var(--text);
            font-family: inherit;
            font-size: 14px;
            transition: all 0.2s ease;
        }

        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: var(--primary);
            background: rgba(108,92,231,0.08);
            box-shadow: 0 0 0 3px rgba(108,92,231,0.15);
        }

        .form-group select {
            cursor: pointer;
        }

        .form-group select option {
            background: var(--card-bg);
            color: var(--text);
        }

        .btn-admin {
            padding: 12px 28px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 700;
            font-family: inherit;
            background: var(--gradient-4);
            color: #1a1a2e;
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(253,203,110,0.3);
            width: 100%;
        }

        .btn-admin:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(253,203,110,0.4);
        }

        /* Order History */
        .order-history {
            margin-top: 20px;
        }

        .order-item {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            animation: fadeInUp 0.4s ease;
        }

        .order-id {
            font-weight: 700;
            font-size: 16px;
            color: #fff;
        }

        .order-total {
            font-size: 20px;
            font-weight: 800;
            color: #55efc4;
            text-shadow: 0 2px 10px rgba(0,206,201,0.2);
        }

        .order-status {
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 10px;
            background: rgba(253,203,110,0.15);
            color: #fdcb6e;
        }

        /* Empty state */
        .empty-cart {
            text-align: center;
            padding: 40px 20px;
            color: var(--text-muted);
        }

        .empty-cart .icon {
            font-size: 48px;
            margin-bottom: 12px;
            opacity: 0.5;
        }

        .empty-cart p {
            font-size: 15px;
        }

        /* Search */
        .search-box {
            width: 100%;
            padding: 12px 16px;
            border: 1px solid var(--card-border);
            border-radius: 12px;
            background: rgba(255,255,255,0.05);
            color: var(--text);
            font-family: inherit;
            font-size: 15px;
            margin-bottom: 25px;
            transition: all 0.3s ease;
        }

        .search-box:focus {
            outline: none;
            border-color: var(--primary);
            background: rgba(108,92,231,0.08);
            box-shadow: 0 0 0 3px rgba(108,92,231,0.15);
        }

        .search-box::placeholder {
            color: var(--text-muted);
        }

        /* Responsive */
        @media (max-width: 768px) {
            .header { padding: 12px 16px; }
            .logo h1 { font-size: 18px; }
            .nav-links a { padding: 6px 10px; font-size: 12px; }
            .container { padding: 20px 12px; }
            .product-grid { grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 14px; }
            .product-card { padding: 16px; }
            .product-card .emoji-icon { font-size: 48px; }
            .form-row { grid-template-columns: 1fr; }
            .cart-summary { flex-direction: column; align-items: stretch; text-align: center; }
            .btn-checkout { width: 100%; }
        }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: var(--bg); }
        ::-webkit-scrollbar-thumb { background: var(--card-border); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--primary); }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="logo">
            <div class="logo-icon">🛍️</div>
            <h1>ShopOnline</h1>
        </div>
        <nav class="nav-links">
            <a href="#" class="active" onclick="showSection('products')">🛍️ Products</a>
            <a href="#" onclick="showSection('cart')">🛒 Cart <span id="headerCartBadge" style="display:none;margin-left:4px;background:var(--accent);color:white;font-size:11px;padding:1px 6px;border-radius:8px;">0</span></a>
            <a href="#" onclick="showSection('admin')">⚙️ Admin</a>
        </nav>
    </header>

    <div class="container">
        <!-- Products Section -->
        <div id="productsSection">
            <div class="section-title">
                🛍️ Our Products
                <span class="badge" id="productCount">0 items</span>
            </div>
            <input type="text" class="search-box" id="searchInput" placeholder="🔍 Search products by name or category..." oninput="filterProducts(this.value)">
            <div class="product-grid" id="productGrid"></div>
        </div>

        <!-- Cart Section -->
        <div class="cart-section" id="cartSection" style="display:none;">
            <div id="cartAlert"></div>
            <div class="cart-header">
                <h2>🛒 Your Shopping Cart <span class="cart-count-badge" id="cartCountBadge">0</span></h2>
            </div>
            <div id="cartEmpty" class="empty-cart">
                <div class="icon">🛒</div>
                <p>Your cart is empty. Add some products!</p>
            </div>
            <table class="cart-table" id="cartTable" style="display:none;">
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Price</th>
                        <th>Quantity</th>
                        <th>Total</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody id="cartBody"></tbody>
            </table>
            <div class="cart-summary" id="cartSummary" style="display:none;">
                <div>
                    <div class="cart-total-label">Total Amount</div>
                    <div class="cart-total-value">$<span id="cartTotal">0.00</span></div>
                </div>
                <button class="btn-checkout" id="checkoutBtn" onclick="showCheckout()">Proceed to Checkout →</button>
            </div>
            <div class="order-form" id="orderForm" style="display:none;">
                <h3>📋 Shipping Address</h3>
                <textarea id="shippingAddress" placeholder="Enter your full shipping address..."></textarea>
                <button class="btn-place-order" onclick="placeOrder()">Place Order — Confirm Purchase 🔒</button>
            </div>
            <div id="orderAlert"></div>
        </div>

        <!-- Order History -->
        <div class="order-history" id="orderHistory"></div>

        <!-- Admin Panel -->
        <div class="admin-panel" id="adminSection" style="display:none;">
            <h2><span class="icon">⚙️</span> Admin Panel — Add New Product</h2>
            <div id="adminAlert"></div>
            <div class="form-row">
                <div class="form-group">
                    <label>Product Name *</label>
                    <input type="text" id="adminName" placeholder="e.g. Wireless Keyboard">
                </div>
                <div class="form-group">
                    <label>Price ($) *</label>
                    <input type="number" id="adminPrice" step="0.01" placeholder="29.99">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Category</label>
                    <select id="adminCategory">
                        <option value="Electronics">💻 Electronics</option>
                        <option value="Furniture">🪑 Furniture</option>
                        <option value="Appliances">☕ Appliances</option>
                        <option value="Office">📓 Office</option>
                        <option value="General">📦 General</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Stock Quantity</label>
                    <input type="number" id="adminStock" placeholder="100" value="100">
                </div>
            </div>
            <div class="form-group">
                <label>Image Emoji (product icon)</label>
                <input type="text" id="adminImage" placeholder="💻 (use emoji to represent product)" value="📦">
            </div>
            <button class="btn-admin" onclick="addProduct()">➕ Add Product to Store</button>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;
        const SESSION_ID = "session-" + Math.random().toString(36).substr(2, 9);
        let cart = [];
        let orders = [];
        let allProducts = [];

        // Category emoji mapping
        const CAT_EMOJI = {
            "Electronics": "💻",
            "Furniture": "🪑",
            "Appliances": "☕",
            "Office": "📓",
            "General": "📦"
        };

        function getStockClass(stock) {
            if (stock >= 100) return "stock-high";
            if (stock >= 30) return "stock-medium";
            return "stock-low";
        }

        function getStockLabel(stock) {
            if (stock >= 100) return "In Stock";
            if (stock >= 30) return "Low Stock";
            return "Almost Gone!";
        }

        async function fetchProducts() {
            try {
                const resp = await fetch(API_BASE + "/api/products");
                const data = await resp.json();
                allProducts = data.products;
                renderProducts(data.products);
                document.getElementById("productCount").textContent = data.count + " items";
            } catch (e) {
                console.error("Failed to fetch products", e);
            }
        }

        function renderProducts(products) {
            const grid = document.getElementById("productGrid");
            if (products.length === 0) {
                grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--text-muted);">😕 No products found. Try a different search.</div>';
                return;
            }
            grid.innerHTML = products.map(p => {
                const emoji = PRODUCTS_WITH_EMOJI[p.id] || "📦";
                const catClass = "cat-" + p.category.toLowerCase();
                return `
                <div class="product-card">
                    <span class="emoji-icon">${emoji}</span>
                    <h3>${p.name}</h3>
                    <span class="category-tag ${catClass}">${CAT_EMOJI[p.category] || '📦'} ${p.category}</span>
                    <div class="price"><span class="currency">$</span>${p.price.toFixed(2)}</div>
                    <div class="stock">
                        <span class="stock-dot ${getStockClass(p.stock)}"></span>
                        ${getStockLabel(p.stock)} — ${p.stock} units
                    </div>
                    <button class="btn-add" onclick="addToCart('${p.id}')">🛒 Add to Cart</button>
                </div>
                `;
            }).join("");
        }

        function filterProducts(query) {
            const q = query.toLowerCase().trim();
            if (!q) {
                renderProducts(allProducts);
                return;
            }
            const filtered = allProducts.filter(p =>
                p.name.toLowerCase().includes(q) ||
                p.category.toLowerCase().includes(q)
            );
            renderProducts(filtered);
        }

        async function addToCart(productId) {
            const resp = await fetch(API_BASE + "/api/cart", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: SESSION_ID, product_id: productId, qty: 1 })
            });
            const data = await resp.json();
            if (data.error) {
                showAlert("cartAlert", data.error, "error");
                return;
            }
            cart = data.cart;
            updateCartUI();
            showAlert("cartAlert", "✅ Added to cart!", "success");
            // Scroll to cart
            setTimeout(() => {
                document.getElementById("cartSection").scrollIntoView({ behavior: "smooth", block: "start" });
            }, 200);
        }

        function updateCartUI() {
            const totalItems = cart.reduce((s, item) => s + item.qty, 0);
            const totalPrice = cart.reduce((s, item) => s + item.price * item.qty, 0);

            // Header badge
            const badge = document.getElementById("headerCartBadge");
            if (totalItems > 0) {
                badge.style.display = "inline";
                badge.textContent = totalItems;
            } else {
                badge.style.display = "none";
            }

            // Cart section
            const cartEmpty = document.getElementById("cartEmpty");
            const cartTable = document.getElementById("cartTable");
            const cartSummary = document.getElementById("cartSummary");

            if (cart.length === 0) {
                cartEmpty.style.display = "block";
                cartTable.style.display = "none";
                cartSummary.style.display = "none";
            } else {
                cartEmpty.style.display = "none";
                cartTable.style.display = "";
                cartSummary.style.display = "flex";

                document.getElementById("cartBody").innerHTML = cart.map(item => {
                    const emoji = PRODUCTS_WITH_EMOJI[item.id] || "📦";
                    return `
                    <tr>
                        <td><span class="cart-item-emoji">${emoji}</span> <span class="cart-item-name">${item.name}</span></td>
                        <td class="cart-item-price">$${item.price.toFixed(2)}</td>
                        <td>
                            <div class="cart-item-qty">
                                <button class="qty-btn" onclick="updateQty('${item.id}', ${Math.max(0, item.qty - 1)})">−</button>
                                <span class="qty-value">${item.qty}</span>
                                <button class="qty-btn" onclick="updateQty('${item.id}', ${item.qty + 1})">+</button>
                            </div>
                        </td>
                        <td class="cart-item-total">$${(item.price * item.qty).toFixed(2)}</td>
                        <td><button class="btn-remove" onclick="removeFromCart('${item.id}')">🗑️ Remove</button></td>
                    </tr>
                    `;
                }).join("");

                document.getElementById("cartTotal").textContent = totalPrice.toFixed(2);
            }

            // Cart count badge
            document.getElementById("cartCountBadge").textContent = totalItems;
        }

        async function updateQty(productId, newQty) {
            if (newQty <= 0) {
                await removeFromCart(productId);
                return;
            }
            const resp = await fetch(API_BASE + "/api/cart", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: SESSION_ID, product_id: productId, qty: newQty })
            });
            const data = await resp.json();
            if (!data.error) {
                cart = data.cart;
                updateCartUI();
            }
        }

        async function removeFromCart(productId) {
            const resp = await fetch(API_BASE + "/api/cart/" + productId + "?session_id=" + SESSION_ID, {
                method: "DELETE"
            });
            const data = await resp.json();
            cart = data.cart;
            updateCartUI();
        }

        function showSection(section) {
            document.getElementById("productsSection").style.display = section === "products" ? "" : "none";
            document.getElementById("cartSection").style.display = section === "cart" ? "" : "none";
            document.getElementById("adminSection").style.display = section === "admin" ? "" : "none";

            document.querySelectorAll(".nav-links a").forEach(a => a.classList.remove("active"));
            if (section === "products") document.querySelector('.nav-links a:nth-child(1)').classList.add("active");
            if (section === "cart") document.querySelector('.nav-links a:nth-child(2)').classList.add("active");
            if (section === "admin") document.querySelector('.nav-links a:nth-child(3)').classList.add("active");

            if (section === "cart") updateCartUI();
        }

        function showCheckout() {
            document.getElementById("orderForm").style.display = "block";
            document.getElementById("checkoutBtn").style.display = "none";
            document.getElementById("shippingAddress").focus();
        }

        async function placeOrder() {
            const address = document.getElementById("shippingAddress").value.trim();
            if (!address) {
                showAlert("orderAlert", "Please enter a shipping address", "error");
                return;
            }

            const btn = document.getElementById("checkoutBtn");
            btn.textContent = "⏳ Processing...";
            btn.disabled = true;

            try {
                const resp = await fetch(API_BASE + "/api/orders", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ session_id: SESSION_ID, shipping_address: address })
                });
                const order = await resp.json();
                if (order.error) {
                    showAlert("orderAlert", order.error, "error");
                    btn.textContent = "Proceed to Checkout →";
                    btn.disabled = false;
                    return;
                }

                orders.push(order);
                cart = [];
                updateCartUI();
                document.getElementById("orderForm").style.display = "none";
                document.getElementById("checkoutBtn").style.display = "";
                document.getElementById("checkoutBtn").textContent = "Proceed to Checkout →";
                document.getElementById("checkoutBtn").disabled = false;
                document.getElementById("shippingAddress").value = "";

                showAlert("orderAlert", "🎉 Order #" + order.order_id + " placed successfully! Total: $" + order.total.toFixed(2), "success");
                renderOrders();

                // Show cart section
                showSection("cart");
            } catch (e) {
                showAlert("orderAlert", "Failed to place order. Please try again.", "error");
                btn.textContent = "Proceed to Checkout →";
                btn.disabled = false;
            }
        }

        function renderOrders() {
            const div = document.getElementById("orderHistory");
            if (orders.length === 0) {
                div.innerHTML = "";
                return;
            }
            div.innerHTML = '<h2 class="section-title" style="margin-top:30px;">📦 Order History</h2>' +
                orders.map(o => `
                <div class="order-item">
                    <div>
                        <div class="order-id">Order #${o.order_id}</div>
                        <small style="color:var(--text-muted);">${o.created_at}</small>
                        <div style="margin-top:6px;"><span class="order-status">● ${o.status}</span></div>
                        ${o.shipping_address ? '<small style="color:var(--text-muted);display:block;margin-top:4px;">📍 ' + o.shipping_address + '</small>' : ''}
                    </div>
                    <div class="order-total">$${o.total.toFixed(2)}</div>
                </div>
                `).join("");
        }

        async function addProduct() {
            const name = document.getElementById("adminName").value.trim();
            const price = parseFloat(document.getElementById("adminPrice").value);
            const category = document.getElementById("adminCategory").value;
            const stock = parseInt(document.getElementById("adminStock").value) || 0;
            const image = document.getElementById("adminImage").value.trim() || "📦";

            if (!name || !price || price <= 0) {
                showAlert("adminAlert", "Please enter a product name and valid price", "error");
                return;
            }

            const btn = document.querySelector(".btn-admin");
            btn.textContent = "⏳ Adding...";
            btn.disabled = true;

            try {
                const resp = await fetch(API_BASE + "/api/admin/products", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name, price, category, stock, image })
                });
                const data = await resp.json();
                // Extract emoji from image field if it's an emoji
                if (resp.ok) {
                    showAlert("adminAlert", "✅ Product '" + name + "' added to store!", "success");
                    // Update our local PRODUCTS_WITH_EMOJI map
                    if (typeof PRODUCTS_WITH_EMOJI === 'object') {
                        // Add to products list by re-fetching
                    }
                    fetchProducts();
                    // Clear form
                    document.getElementById("adminName").value = "";
                    document.getElementById("adminPrice").value = "";
                    document.getElementById("adminStock").value = "100";
                    document.getElementById("adminImage").value = "📦";
                } else {
                    showAlert("adminAlert", data.error || "Failed to add product", "error");
                }
            } catch (e) {
                showAlert("adminAlert", "Error adding product", "error");
            }

            btn.textContent = "➕ Add Product to Store";
            btn.disabled = false;
        }

        function showAlert(elementId, message, type) {
            const el = document.getElementById(elementId);
            if (!el) return;
            el.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
            setTimeout(() => { el.innerHTML = ""; }, 4000);
        }

        // Init
        fetchProducts();
        updateCartUI();
    </script>
</body>
</html>
'''

# --- In-memory storage ---
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

carts = {}
orders = {}

def get_next_id():
    return str(uuid.uuid4())[:8]

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}), 200

@app.route("/api/products", methods=["GET"])
def get_products():
    category = request.args.get("category")
    if category:
        items = [p for p in products_db["products"] if category.lower() in p["category"].lower()]
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
    total = sum(item["price"] * item["qty"] for item in cart)
    return jsonify({"cart": cart, "total": total}), 200

@app.route("/api/cart", methods=["POST"])
def add_to_cart():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400
    session_id = data.get("session_id", "default")
    product_id = data.get("product_id")
    qty = max(1, data.get("qty", 1))

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
    for item in cart:
        if item["id"] == product_id:
            item["qty"] += qty
            break
    else:
        cart.append({"id": product["id"], "name": product["name"], "price": product["price"], "qty": qty, "image": product["image"]})

    carts[session_id] = cart
    total = sum(item["price"] * item["qty"] for item in cart)
    return jsonify({"cart": cart, "total": total}), 200

@app.route("/api/cart/<product_id>", methods=["DELETE"])
def remove_from_cart(product_id):
    session_id = request.args.get("session_id", "default")
    cart = carts.get(session_id, [])
    carts[session_id] = [item for item in cart if item["id"] != product_id]
    total = sum(item["price"] * item["qty"] for item in carts[session_id])
    return jsonify({"cart": carts[session_id], "total": total}), 200

@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400
    session_id = data.get("session_id", "default")
    cart = carts.get(session_id, [])
    if not cart:
        return jsonify({"error": "Cart is empty"}), 400

    order_id = get_next_id()
    total = sum(item["price"] * item["qty"] for item in cart)
    order = {
        "order_id": order_id,
        "session_id": session_id,
        "items": cart,
        "total": total,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "shipping_address": data.get("shipping_address", ""),
    }
    orders[order_id] = order
    carts[session_id] = []
    return jsonify(order), 201

@app.route("/api/orders/<order_id>", methods=["GET"])
def get_order(order_id):
    order = orders.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order), 200

@app.route("/api/admin/products", methods=["POST"])
def admin_add_product():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400
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

# --- Frontend routes ---
@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def index():
    return Response(frontend_html, mimetype="text/html")

@app.route("/cart", methods=["GET"])
def cart_page():
    return Response(frontend_html, mimetype="text/html")

@app.route("/admin", methods=["GET"])
def admin_page():
    return Response(frontend_html, mimetype="text/html")

# --- Run ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

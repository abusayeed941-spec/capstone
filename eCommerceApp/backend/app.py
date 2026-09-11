import os, json, uuid, datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__, static_folder=None)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecommerce_data")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
CARTS_FILE = os.path.join(DATA_DIR, "carts.json")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")

DEFAULT_PRODUCTS = [
    {"id": 1, "name": "Gaming Laptop", "category": "Electronics", "price": 1200.00, "stock": 10, "description": "High-performance gaming laptop with RTX 4070", "image": "💻", "rating": 4.8, "sku": "ELEC-001"},
    {"id": 2, "name": "Wireless Earbuds", "category": "Electronics", "price": 89.99, "stock": 25, "description": "Noise-cancelling Bluetooth earbuds with 24h battery", "image": "🎧", "rating": 4.5, "sku": "ELEC-002"},
    {"id": 3, "name": "Mechanical Keyboard", "category": "Electronics", "price": 149.99, "stock": 12, "description": "RGB backlit mechanical keyboard with hot-swappable switches", "image": "⌨️", "rating": 4.7, "sku": "ELEC-003"},
    {"id": 4, "name": "Desk Lamp", "category": "Home & Office", "price": 39.99, "stock": 20, "description": "LED desk lamp with adjustable brightness and color temperature", "image": "💡", "rating": 4.3, "sku": "HOME-001"},
    {"id": 5, "name": "Ergonomic Chair", "category": "Home & Office", "price": 450.00, "stock": 5, "description": "Premium ergonomic office chair with lumbar support", "image": "🪑", "rating": 4.9, "sku": "HOME-002"},
    {"id": 6, "name": "Smartphone", "category": "Electronics", "price": 799.99, "stock": 8, "description": "Latest flagship smartphone with 120Hz display", "image": "📱", "rating": 4.6, "sku": "ELEC-004"},
    {"id": 7, "name": "Coffee Maker", "category": "Home & Office", "price": 129.99, "stock": 15, "description": "Automatic drip coffee maker with timer", "image": "☕", "rating": 4.4, "sku": "HOME-003"},
    {"id": 8, "name": "Notebook Set", "category": "Home & Office", "price": 24.99, "stock": 30, "description": "Premium leather-bound notebook set (5 pack)", "image": "📓", "rating": 4.1, "sku": "HOME-004"},
    {"id": 9, "name": "USB Mouse", "category": "Electronics", "price": 29.99, "stock": 50, "description": "Ergonomic wireless USB mouse with silent clicks", "image": "🖱️", "rating": 4.2, "sku": "ELEC-005"},
    {"id": 10, "name": "Desk Organizer", "category": "Home & Office", "price": 49.99, "stock": 18, "description": "Bamboo desk organizer with compartments for pens and supplies", "image": "📦", "rating": 4.0, "sku": "HOME-005"},
]

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
if not os.path.exists(PRODUCTS_FILE):
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(DEFAULT_PRODUCTS, f, indent=2)
if not os.path.exists(CARTS_FILE):
    with open(CARTS_FILE, "w") as f:
        json.dump({}, f)
if not os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "w") as f:
        json.dump([], f)

def load_json(filename):
    try:
        with open(filename) as f:
            return json.load(f)
    except:
        if "cart" in filename:
            return {}
        if "orders" in filename:
            return []
        return []

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/api/health")
def health():
    return jsonify({"status": "healthy", "service": "ecommerce-api", "timestamp": datetime.datetime.utcnow().isoformat()})

@app.route("/api/products")
def get_products():
    products = load_json(PRODUCTS_FILE)
    category = request.args.get("category")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    in_stock = request.args.get("in_stock")
    search = request.args.get("search")
    if category:
        products = [p for p in products if p.get("category") == category]
    if min_price:
        products = [p for p in products if float(p.get("price", 0)) >= float(min_price)]
    if max_price:
        products = [p for p in products if float(p.get("price", 0)) <= float(max_price)]
    if in_stock == "true":
        products = [p for p in products if p.get("stock", 0) > 0]
    if search:
        s = search.lower()
        products = [p for p in products if s in p.get("name", "").lower() or s in p.get("description", "").lower()]
    return jsonify(products)

@app.route("/api/products/<int:product_id>")
def get_product(product_id):
    products = load_json(PRODUCTS_FILE)
    for p in products:
        if p["id"] == product_id:
            return jsonify(p)
    return jsonify({"error": "Product not found"}), 404

@app.route("/api/categories")
def get_categories():
    products = load_json(PRODUCTS_FILE)
    cats = {}
    for p in products:
        cat = p.get("category", "Uncategorized")
        if cat not in cats:
            cats[cat] = {"name": cat, "count": 0, "products": []}
        cats[cat]["count"] += 1
        cats[cat]["products"].append(p)
    return jsonify(list(cats.values()))

@app.route("/api/cart", methods=["GET", "POST"])
def cart():
    if request.method == "GET":
        cid = request.args.get("cart_id", "default")
        carts = load_json(CARTS_FILE)
        return jsonify(carts.get(cid, {"items": [], "total": 0.0}))
    data = request.get_json()
    cid = data.get("cart_id", str(uuid.uuid4())[:8])
    carts = load_json(CARTS_FILE)
    if cid not in carts:
        carts[cid] = {"items": [], "total": 0.0}
    existing_items = {i["product_id"]: i for i in carts[cid]["items"]}
    for item in data.get("items", []):
        if item["product_id"] in existing_items:
            existing_items[item["product_id"]]["quantity"] = item.get("quantity", 1)
        else:
            existing_items[item["product_id"]] = item
    carts[cid]["items"] = list(existing_items.values())
    carts[cid]["total"] = sum(i.get("price", 0) * i.get("quantity", 1) for i in carts[cid]["items"])
    save_json(CARTS_FILE, carts)
    return jsonify({"cart_id": cid, "cart": carts[cid]})

@app.route("/api/checkout", methods=["POST"])
def checkout():
    data = request.get_json()
    cid = data.get("cart_id")
    carts = load_json(CARTS_FILE)
    cart = carts.get(cid, {"items": [], "total": 0.0})
    if not cart["items"]:
        return jsonify({"error": "Cart is empty"}), 400
    products = load_json(PRODUCTS_FILE)
    order = {
        "order_id": str(uuid.uuid4())[:12].upper(),
        "items": cart["items"],
        "total": cart["total"],
        "customer_email": data.get("customer_email", ""),
        "shipping_address": data.get("shipping_address", ""),
        "status": "confirmed",
        "created_at": datetime.datetime.utcnow().isoformat(),
    }
    orders = load_json(ORDERS_FILE)
    orders.append(order)
    for item in order["items"]:
        for p in products:
            if p["id"] == item["product_id"]:
                p["stock"] = max(0, p["stock"] - item.get("quantity", 1))
    save_json(PRODUCTS_FILE, products)
    save_json(ORDERS_FILE, orders)
    carts[cid] = {"items": [], "total": 0.0}
    save_json(CARTS_FILE, carts)
    return jsonify({"success": True, "order": order})

@app.route("/api/orders")
def get_orders():
    return jsonify(load_json(ORDERS_FILE))

@app.route("/api/admin/products", methods=["GET", "POST", "PUT", "DELETE"])
def admin_products():
    if request.method == "GET":
        return jsonify(load_json(PRODUCTS_FILE))
    elif request.method == "POST":
        data = request.get_json()
        products = load_json(PRODUCTS_FILE)
        max_id = max((p["id"] for p in products), default=0)
        new_product = {**data, "id": max_id + 1}
        products.append(new_product)
        save_json(PRODUCTS_FILE, products)
        return jsonify(new_product), 201
    elif request.method == "PUT":
        data = request.get_json()
        products = load_json(PRODUCTS_FILE)
        for i, p in enumerate(products):
            if p["id"] == data.get("id"):
                products[i] = {**p, **data}
                save_json(PRODUCTS_FILE, products)
                return jsonify(products[i])
        return jsonify({"error": "Product not found"}), 404
    elif request.method == "DELETE":
        pid = request.args.get("id")
        products = load_json(PRODUCTS_FILE)
        filtered = [p for p in products if str(p["id"]) != str(pid)]
        if len(filtered) < len(products):
            save_json(PRODUCTS_FILE, filtered)
            return jsonify({"success": True, "deleted_id": pid})
        return jsonify({"error": "Product not found"}), 404

@app.route("/")
def index():
    return """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PSR E-Commerce</title>
<style>
:root{--bg1:#0d0d1a;--bg2:#1a1a2e;--bgc:#252540;--ac:#00d4ff;--ac3:#7c3aed;--tp:#e8e8f0;--ts:#a0a0b8;--sc:#10b981;--dc:#ef4444;--bd:#2a2a45}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Segoe UI",Arial,sans-serif;background:var(--bg1);color:var(--tp);min-height:100vh;display:flex;flex-direction:column}
.hero{background:linear-gradient(135deg,#1a1a2e,#252540,#1a1a2e);padding:2.5rem 2rem;text-align:center;border-bottom:1px solid var(--bd);position:relative;overflow:hidden}
.hero::before{content:"";position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:radial-gradient(circle at 30% 50%,rgba(0,212,255,.08) 0%,transparent 60%),radial-gradient(circle at 70% 50%,rgba(124,58,237,.06) 0%,transparent 60%);animation:hg 8s ease-in-out infinite alternate}
@keyframes hg{0%{transform:translate(0,0)}100%{transform:translate(2%,-2%)}}
.hero h1{font-size:2.2rem;margin-bottom:.4rem;background:linear-gradient(90deg,var(--ac),var(--ac3));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero p{color:var(--ts);font-size:1rem}
.hb{display:inline-block;background:rgba(124,58,237,.2);border:1px solid rgba(124,58,237,.4);padding:.25rem .9rem;border-radius:20px;color:var(--ac3);font-size:.8rem;margin-bottom:.8rem}
.c{max-width:1200px;margin:0 auto;padding:1.5rem;flex:1}
.hd{display:flex;justify-content:space-between;align-items:center;padding:.8rem 1.5rem;background:var(--bg2);border-bottom:1px solid var(--bd);position:sticky;top:0;z-index:100}
.lg{font-size:1.3rem;font-weight:700;color:var(--ac);display:flex;align-items:center;gap:.4rem}
.lg span{background:linear-gradient(90deg,var(--ac),#ff6b35);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.ha{display:flex;gap:.6rem;align-items:center}
.sb{background:var(--bgc);border:1px solid var(--bd);border-radius:6px;padding:.4rem .8rem;color:var(--tp);width:200px;font-size:.85rem;outline:none}
.sb:focus{border-color:var(--ac)}
.cb{background:var(--bgc);border:1px solid var(--ac);color:var(--ac);padding:.4rem .8rem;border-radius:6px;cursor:pointer;font-size:.85rem;display:flex;align-items:center;gap:.4rem}
.cb:hover{background:var(--ac);color:var(--bg1)}
.pg{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:1rem;margin-top:1rem}
.pc{background:var(--bgc);border:1px solid var(--bd);border-radius:10px;overflow:hidden;transition:all .3s;cursor:pointer}
.pc:hover{transform:translateY(-3px);box-shadow:0 6px 20px rgba(0,212,255,.12);border-color:var(--ac)}
.pi{height:100px;background:linear-gradient(135deg,var(--bg2),var(--bgc));display:flex;align-items:center;justify-content:center;font-size:2.5rem}
.pii{padding:.8rem}
.pcat{font-size:.7rem;color:var(--ac3);text-transform:uppercase;letter-spacing:.5px;margin-bottom:.2rem;font-weight:600}
.pn{font-size:.9rem;font-weight:600;margin-bottom:.2rem}
.pp{font-size:1.1rem;font-weight:700;color:var(--ac)}
.ps{font-size:.75rem;margin-top:.2rem}
.si{color:var(--sc)}.sl{color:#f59e0b}.so{color:var(--dc)}
.pa{display:flex;gap:.4rem;margin-top:.5rem}
.b{padding:.4rem .8rem;border-radius:6px;border:none;cursor:pointer;font-size:.8rem;font-weight:500}
.bp{background:linear-gradient(135deg,var(--ac),var(--ac3));color:#fff}
.bp:hover{transform:scale(1.02)}
.cp{position:fixed;top:0;right:0;width:350px;height:100vh;background:var(--bg2);border-left:1px solid var(--ac);transform:translateX(100%);transition:transform .3s;z-index:200;box-shadow:-4px 0 20px rgba(0,0,0,.4)}
.cp.open{transform:translateX(0)}
.ch{padding:.8rem 1.2rem;border-bottom:1px solid var(--bd);display:flex;justify-content:space-between;align-items:center}
.ch h3{color:var(--ac)}
.cc{background:none;border:none;color:var(--ts);font-size:1.3rem;cursor:pointer}
.cc:hover{color:var(--dc)}
.ci{padding:.8rem;max-height:65vh;overflow-y:auto}
.citem{display:flex;gap:.6rem;padding:.5rem 0;border-bottom:1px solid var(--bd);align-items:center}
.cii{width:35px;height:35px;background:var(--bgc);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:1.2rem}
.cn{font-size:.8rem;font-weight:500}
.cp2{font-size:.75rem;color:var(--ac)}
.cq{display:flex;gap:.2rem}
.qb{width:20px;height:20px;border-radius:3px;border:1px solid var(--bd);background:var(--bgc);color:var(--tp);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:.8rem}
.qb:hover{border-color:var(--ac);color:var(--ac)}
.cf{padding:.8rem 1.2rem;border-top:1px solid var(--bd);background:var(--bg1);position:absolute;bottom:0;left:0;right:0}
.ct{display:flex;justify-content:space-between;margin-bottom:.5rem;font-size:1rem}
.ct span:first-child{color:var(--ts)}
.ct span:last-child{color:var(--ac);font-weight:700}
.ce{text-align:center;padding:1.5rem;color:var(--ts)}
.ts{display:flex;gap:.4rem;margin-bottom:1rem}
.tb{background:var(--bgc);border:1px solid var(--bd);padding:.5rem 1.2rem;border-radius:6px;cursor:pointer;color:var(--ts);font-size:.85rem}
.tb:hover{border-color:var(--ac);color:var(--ac)}
.tb.active{background:var(--ac);color:var(--bg1);border-color:var(--ac)}
.tc{display:none}
.tc.active{display:block}
.cs{margin-top:1.5rem;padding:1.2rem;background:var(--bgc);border:1px solid var(--bd);border-radius:10px}
.cs h3{color:var(--ac);margin-bottom:.8rem;font-size:1rem}
.cr{display:flex;gap:.8rem;margin-bottom:.8rem}
.cr label{min-width:80px;color:var(--ts);font-size:.85rem}
.cr input{flex:1;background:var(--bg2);border:1px solid var(--bd);border-radius:5px;padding:.4rem .6rem;color:var(--tp);font-size:.85rem;outline:none}
.cr input:focus{border-color:var(--ac)}
.cs2{display:flex;justify-content:space-between;padding:.8rem;background:var(--bg2);border-radius:6px;margin-top:.8rem}
.cs2 .t{font-size:1.1rem;color:var(--ac);font-weight:700}
.oc{background:var(--bgc);border:1px solid var(--bd);border-radius:10px;padding:1rem;margin-bottom:.8rem}
.oid{font-size:1rem;font-weight:600;color:var(--ac)}
.oi{margin-top:.5rem}
.oii{display:flex;justify-content:space-between;padding:.2rem 0;font-size:.8rem}
.ot{margin-top:.5rem;padding-top:.5rem;border-top:1px solid var(--bd);text-align:right}
.st{display:inline-block;padding:.15rem .6rem;border-radius:10px;font-size:.7rem;font-weight:500;margin-top:.4rem}
.sconf{background:rgba(16,185,129,.2);color:var(--sc)}
.toast{position:fixed;bottom:1.5rem;right:1.5rem;background:var(--sc);color:#fff;padding:.5rem 1rem;border-radius:6px;font-size:.8rem;z-index:300;opacity:0;transform:translateY(15px);transition:all .3s}
.toast.show{opacity:1;transform:translateY(0)}
.toast.err{background:var(--dc)}
@media(max-width:768px){.hero h1{font-size:1.6rem}.pg{grid-template-columns:repeat(auto-fill,minmax(140px,1fr))}.sb{width:130px}.cp{width:100%}}
::-webkit-scrollbar{width:5px}.::-webkit-scrollbar-track{background:var(--bg1)}.::-webkit-scrollbar-thumb{background:var(--bd);border-radius:2px}
</style></head><body>
<div class="hero"><div class="hb">🔥 Summer Sale - Up to 30% Off</div><h1>PSR E-Commerce Store</h1><p>Premium products for work, play, and everything in between</p></div>
<div class="c"><div class="hd"><div class="lg"><span>PSR</span> Solutions</div><div class="ha"><input type="text" class="sb" placeholder="Search products..." id="si" oninput="loadProducts()"><button class="cb" onclick="toggleCart()">🛒 Cart <span id="cc">0</span></button></div></div>
<div class="ts"><button class="tb active" onclick="switchTab('products')">Products</button><button class="tb" onclick="switchTab('cart')">Cart</button><button class="tb" onclick="switchTab('checkout')">Checkout</button><button class="tb" onclick="switchTab('orders')">Orders</button></div>
<div class="tc active" id="pt"><div id="filters"></div><div class="pg" id="pg"><div class="ce">Loading...</div></div></div>
<div class="tc" id="ct"><div class="cs"><h3>🛒 Your Cart</h3><div id="cv"><div class="ce">Your cart is empty.</div></div><div class="cs2" id="cs2" style="display:none"><div>Cart Summary</div><div class="t" id="ctd">$0.00</div></div></div></div>
<div class="tc" id="ckt"><div class="cs"><h3>💳 Checkout</h3><div id="ckf"><div class="cr"><label>Email</label><input type="email" id="ce" placeholder="you@example.com"></div><div class="cr"><label>Address</label><input type="text" id="ca" placeholder="123 Main St, City, State"></div><div class="cs2"><span>Total</span><span class="t" id="ckt2">$0.00</span></div><button class="b bp" style="width:100%;margin-top:.8rem" onclick="checkout()">Place Order</button></div><div id="cks" style="display:none"><div class="ce"><h3 style="color:var(--sc);margin-top:.8rem">✅ Order Placed!</h3><p style="margin-top:.4rem;color:var(--ts)">Redirecting...</p></div></div></div></div>
<div class="tc" id="ot"><div class="cs"><h3>📦 Your Orders</h3><div id="ol"><div class="ce">Loading...</div></div></div></div></div>
<div class="cp" id="cp"><div class="ch"><h3>🛒 Cart</h3><button class="cc" onclick="toggleCart()">✕</button></div><div class="ci" id="civ"><div class="ce">Your cart is empty.</div></div><div class="cf"><div class="ct"><span>Total</span><span id="ctp">$0.00</span></div><button class="b bp" style="width:100%" onclick="toggleCart();switchTab('checkout')">Proceed to Checkout</button></div></div>
<div class="toast" id="toast"></div>
<script>
let cart={items:[],total:0},cid=localStorage.getItem("psr_cid")||"default",cat="all",srch=""
async function api(e,m="GET",b=null){const o={method:m,headers:{"Content-Type":"application/json"}};if(b)o.body=JSON.stringify(b);return(await fetch("/api"+e,o)).json()}
async function loadProducts(){const g=document.getElementById("pg");g.innerHTML='<div class="ce">Loading...</div>';let ep="/products?";if(cat!=="all")ep+="category="+cat+"&";if(srch)ep+="search="+encodeURIComponent(srch)+"&";ep+="in_stock=false";try{const p=await api(ep);const cs=await api("/categories");const fb=document.getElementById("filters");fb.innerHTML='<button class="tb active" onclick="setCat(\'all\',this)">All</button>';cs.forEach(c=>{const b=document.createElement("button");b.className="tb"+(cat===c.name?" active":"");b.textContent=c.name+" ("+c.count+")";b.onclick=()=>setCat(c.name,b);fb.appendChild(b)});if(!p.length){g.innerHTML='<div class="ce">No products.</div>';return}g.innerHTML=p.map(p=>{const sc=p.stock>0?(p.stock<5?"sl":"si"):"so";const st=p.stock>0?(p.stock<5?"Only "+p.stock+" left!":p.stock+" in stock"):"Out of stock";return `<div class="pc"><div class="pi">${p.image}</div><div class="pii"><div class="pcat">${p.category}</div><div class="pn">${p.name}</div><div class="pp">$${p.price.toFixed(2)}</div><div class="ps ${sc}">${st}</div><div style="margin-top:.4rem;color:var(--ts)">⭐ ${p.rating}/5.0</div><div class="pa"><button class="b bp" onclick="addToCart(${p.id})">🛒 Add to Cart</button></div></div></div>`}).join("")}catch(e){g.innerHTML='<div class="ce" style="color:var(--dc)">Error.</div>'}}
async function setCat(c,b){cat=c;document.querySelectorAll(".tb").forEach(x=>x.classList.remove("active"));if(b)b.classList.add("active");await loadProducts()}
async function addToCart(id){const p=await api("/products/"+id);const ex=cart.items.find(i=>i.product_id===id);if(ex)ex.quantity+=1;else cart.items.push({product_id:id,name:p.name,price:p.price,quantity:1,image:p.image});cart.total=cart.items.reduce((s,i)=>s+i.price*i.quantity,0);await api("/cart","POST",{cart_id:cid,items:cart.items});document.getElementById("cc").textContent=cart.items.reduce((s,i)=>s+i.quantity,0);renderCart();showToast("✅ "+p.name+" added!")}
async function renderCart(){const iv=document.getElementById("civ"),tp=document.getElementById("ctp"),cs2=document.getElementById("cs2"),ctd=document.getElementById("ctd");if(!cart.items.length){iv.innerHTML='<div class="ce">Your cart is empty.</div>';tp.textContent="$0.00";cs2.style.display="none";return}iv.innerHTML=cart.items.map(i=>`<div class="citem"><div class="cii">${i.image}</div><div class="cn">${i.name}</div><div class="cp2">$${i.price.toFixed(2)} × ${i.quantity}</div><div class="cq"><button class="qb" onclick="chgQty(${i.product_id},-1)">-</button><span style="min-width:18px;text-align:center">${i.quantity}</span><button class="qb" onclick="chgQty(${i.product_id},1)">+</button></div></div>`).join("");tp.textContent="$"+cart.total.toFixed(2);ctd.textContent="$"+cart.total.toFixed(2);cs2.style.display="flex"}
async function chgQty(id,d){const i=cart.items.find(x=>x.product_id===id);if(!i)return;i.quantity+=d;if(i.quantity<=0)cart.items=cart.items.filter(x=>x.product_id!==id);cart.total=cart.items.reduce((s,x)=>s+x.price*x.quantity,0);await api("/cart","POST",{cart_id:cid,items:cart.items});document.getElementById("cc").textContent=cart.items.reduce((s,x)=>s+x.quantity,0);renderCart()}
async function checkout(){const e=document.getElementById("ce").value,a=document.getElementById("ca").value;if(!e||!a){showToast("Please fill in email and address",true);return}document.getElementById("ckf").style.display="none";document.getElementById("cks").style.display="block";const r=await api("/checkout","POST",{cart_id:cid,customer_email:e,shipping_address:a});if(r.success){setTimeout(()=>{switchTab("orders");showToast("🎉 Order "+r.order.order_id+" placed! $"+r.order.total.toFixed(2))},1200)}else{document.getElementById("ckf").style.display="block";document.getElementById("cks").style.display="none";showToast("Error: "+(r.error||"Failed"),true)}}
async function loadOrders(){const l=document.getElementById("ol");l.innerHTML='<div class="ce">Loading...</div>';try{const o=await api("/orders");if(!o.length){l.innerHTML='<div class="ce">No orders yet.</div>';return}l.innerHTML=o.slice().reverse().map(o=>`<div class="oc"><div class="oid">Order #${o.order_id}</div><div style="font-size:.75rem;color:var(--ts)">${new Date(o.created_at).toLocaleDateString()}</div><div class="oi">${o.items.map(i=>`<div class="oii"><span>${i.image} ${i.name} × ${i.quantity}</span><span>$${(i.price*i.quantity).toFixed(2)}</span></div>`).join("")}</div><div class="ot"><div>Total</div><div style="font-size:1.1rem;color:var(--ac);font-weight:700">$${o.total.toFixed(2)}</div></div><span class="st sconf">${o.status}</span></div>`).join("")}catch(e){l.innerHTML='<div class="ce" style="color:var(--dc)">Error.</div>'}}
function toggleCart(){document.getElementById("cp").classList.toggle("open");renderCart()}
function switchTab(t){document.querySelectorAll(".tb").forEach(x=>x.classList.remove("active"));document.querySelectorAll(".tc").forEach(x=>x.classList.remove("active"));document.querySelector('.tb[onclick*="'+t+'"]').classList.add("active");document.getElementById(t+"t").classList.add("active");if(t==="products")loadProducts();if(t==="cart")renderCart();if(t==="checkout"){document.getElementById("ckt2").textContent="$"+cart.total.toFixed(2);if(!cart.total){showToast("Cart is empty!",true);switchTab("products")}}if(t==="orders")loadOrders()}
function showToast(msg,err){const t=document.getElementById("toast");t.textContent=msg;t.className="toast"+(err?" err":"");t.classList.add("show");setTimeout(()=>t.classList.remove("show"),2500)}
loadProducts();renderCart();
</script></body></html>"""

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    ssl_cert = os.environ.get("SSL_CERT", "/etc/ssl/ecommerce/server.crt")
    ssl_key = os.environ.get("SSL_KEY", "/etc/ssl/ecommerce/server.key")
    context = (ssl_cert, ssl_key) if os.path.exists(ssl_cert) and os.path.exists(ssl_key) else None
    app.run(host="0.0.0.0", port=port, ssl_context=context, threaded=True)


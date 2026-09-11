import sys
import subprocess
import time
import json
import urllib.request
import urllib.error
import os

# Ensure deps
try:
    import flask
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'flask', 'flask-cors', '-q'])
    import flask

base_url = 'http://localhost:5000'

# Kill any existing process on port 5000
subprocess.run('taskkill /F /IM python.exe 2>NUL || true', shell=True)
time.sleep(1)

# Start Flask
proc = subprocess.Popen([sys.executable, 'app.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)
print(f'Flask PID: {proc.pid}, alive: {proc.poll() is None}')
if proc.poll() is not None:
    print('Flask FAILED to start')
    sys.exit(1)

def get(path, exp=200):
    with urllib.request.urlopen(f'{base_url}{path}', timeout=5) as r:
        body = json.loads(r.read())
        assert r.status == exp, f'{path}: expected {exp}, got {r.status}'
        return body, r.status

def post(path, data, exp=200):
    req = urllib.request.Request(f'{base_url}{path}', data=json.dumps(data).encode(),
        headers={'Content-Type':'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=5) as r:
        body = json.loads(r.read())
        assert r.status == exp, f'{path}: expected {exp}, got {r.status}'
        return body, r.status

def delete(path, exp=200):
    req = urllib.request.Request(f'{base_url}{path}', method='DELETE')
    with urllib.request.urlopen(req, timeout=5) as r:
        body = json.loads(r.read())
        assert r.status == exp, f'{path}: expected {exp}, got {r.status}'
        return body, r.status

results = []
def check(name, ok):
    results.append((name, 'PASS' if ok else 'FAIL'))
    print(f'  [{"PASS" if ok else "FAIL"}] {name}')

# 1. Health
body, _ = get('/api/health')
check('Health endpoint', body.get('status') == 'healthy')

# 2. Products list
body, _ = get('/api/products')
check('Products list (8 products)', body.get('count') == 8)

# 3. Product detail
body, _ = get('/api/products/1')
check('Product detail (Laptop)', body.get('name') == 'Laptop')

# 4. Filter Electronics
body, _ = get('/api/products?category=Electronics')
check('Filter Electronics', all('Electronics' in p.get('category','') for p in body.get('products',[])))

# 5. Add to cart
body, _ = post('/api/cart', {'session_id':'u1','product_id':'2','qty':2})
check('Add Smartphone x2 to cart', body.get('cart',[{}])[0].get('qty') == 2)

# 6. Add more
body, _ = post('/api/cart', {'session_id':'u1','product_id':'3','qty':1})
check('Add Headphones to cart', len(body.get('cart',[])) == 2)

# 7. View cart
body, _ = get('/api/cart?session_id=u1')
check('View cart (2 items)', len(body.get('cart',[])) == 2)

# 8. Remove
body, _ = delete('/api/cart/3?session_id=u1')
check('Remove item (1 left)', len(body.get('cart',[])) == 1)

# 9. Create order (expect 201)
body, code = post('/api/orders', {'session_id':'u1','shipping_address':'123 Main St'}, exp=201)
order_id = body.get('order_id', '???')
check(f'Create order #{order_id} (201, pending)', code == 201 and body.get('status') == 'pending' and body.get('total',0) > 0)

# 10. View order
body, _ = get(f'/api/orders/{order_id}')
check(f'View order #{order_id}', body.get('order_id') == order_id)

# 11. Cart cleared
body, _ = get('/api/cart?session_id=u1')
check('Cart cleared after order', len(body.get('cart',[])) == 0)

# 12. Admin add product (expect 201)
body, code = post('/api/admin/products', {'name':'Wireless Mouse','price':39.99,'category':'Electronics','stock':100}, exp=201)
check(f'Admin add: {body.get("name")} (201)', code == 201 and body.get('name') == 'Wireless Mouse')

# 13. Admin list (should have 9 now)
body, _ = get('/api/admin/products')
check(f'Admin list: {body.get("count")} products (9)', body.get('count') == 9)

# 14. 404
try:
    get('/api/products/999')
    check('404 unknown product', False)
except urllib.error.HTTPError as e:
    body = json.loads(e.read())
    check(f'404 unknown product (code={e.code})', e.code == 404 and 'error' in body)

# 15. Stock validation (expect 400)
try:
    post('/api/cart', {'session_id':'ux','product_id':'1','qty':99999})
    check('Stock validation', False)
except urllib.error.HTTPError as e:
    body = json.loads(e.read())
    check(f'Stock validation rejected (code={e.code})', e.code == 400 and 'Insufficient stock' in body.get('error',''))

# 16. Default cart
body, _ = get('/api/cart')
check('Default cart empty', len(body.get('cart',[])) == 0)

print()
passed = sum(1 for _,ok in results if ok)
total = len(results)
print(f'END-TO-END: {passed}/{total} passed')
print(f'Flask running at: {base_url}')
print(f'PID: {proc.pid}, running: {proc.poll() is None}')
if passed == total:
    print('STATUS: ALL CHECKS PASSED - FULLY WORKING E-COMMERCE APP')
else:
    print(f'STATUS: {total - passed} FAILURES')

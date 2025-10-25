import os, sys, json
from fastapi.testclient import TestClient

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import app

client = TestClient(app)

# Test products list
r = client.get('/api/products')
print('GET /api/products ->', r.status_code)
print(r.json())

# Pick a product id from the list
data = r.json()
product_id = data['PRODUCTS_LIST'][0]['product_id'] if data.get('PRODUCTS_LIST') else '1'

# Test price endpoint
r2 = client.post('/api/price', json={'product_id': product_id, 'margin_percent': 3.0})
print('POST /api/price ->', r2.status_code)
print(json.dumps(r2.json(), indent=2))

import os, sys
from fastapi.testclient import TestClient

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import app

client = TestClient(app)
resp = client.get("/")
print("STATUS:", resp.status_code)
print("BODY:", resp.text)

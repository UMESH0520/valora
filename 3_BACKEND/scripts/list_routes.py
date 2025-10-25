import os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from app.main import app

for route in app.routes:
    try:
        path = getattr(route, 'path', None)
        methods = getattr(route, 'methods', [])
        name = getattr(route, 'name', '')
        tags = getattr(route, 'tags', None)
        if path:
            print(path, sorted(list(methods)) if methods else None, name, tags)
    except Exception as e:
        print('ERR', e)

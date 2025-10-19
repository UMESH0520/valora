from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.routes import health_route, price_routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('valora.backend')

app = FastAPI(title='VALORA Backend Ready', version='1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173','http://127.0.0.1:5173','http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(health_route.router)
app.include_router(price_routes.router)

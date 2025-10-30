from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .settings import settings
from .pricing import get_display_price, get_prices, get_price_detail, get_price_details

app = FastAPI(title="VALORA Price Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PriceResponse(BaseModel):
    product_id: Optional[str] = None
    price: Optional[float] = None
    currency: str = "INR"
    description: Optional[str] = None
    source: Optional[str] = None
    confidence: Optional[float] = None
    last_updated: datetime


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/price", response_model=PriceResponse)
async def read_price(product_id: Optional[str] = Query(default=None)):
    detail = get_price_detail(product_id)
    detail.update({"last_updated": datetime.now(timezone.utc)})
    return detail

@app.get("/prices")
async def read_prices(ids: Optional[str] = Query(default=None)):
    """Return mapping of id->PriceResponse for comma-separated ids; if none provided, returns empty mapping."""
    id_list = [s for s in (ids.split(",") if ids else []) if s]
    return {
        "currency": "INR",
        "prices": get_price_details(id_list),
        "last_updated": datetime.now(timezone.utc),
    }


@app.websocket("/ws/price")
async def ws_price(websocket: WebSocket):
    await websocket.accept()
    product_id = websocket.query_params.get("product_id")
    last_payload = None
    try:
        while True:
            detail = get_price_detail(product_id)
            payload = {
                **detail,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
            if payload != last_payload:
                await websocket.send_json(payload)
                last_payload = payload
            await asyncio.sleep(settings.POLL_SECONDS)
    except WebSocketDisconnect:
        return

@app.websocket("/ws/prices")
async def ws_prices(websocket: WebSocket):
    await websocket.accept()
    ids_param = websocket.query_params.get("ids") or ""
    id_list = [s for s in ids_param.split(",") if s]
    last_payload = None
    try:
        while True:
            mapping = get_price_details(id_list)
            payload = {
                "currency": "INR",
                "prices": mapping,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
            if payload != last_payload:
                await websocket.send_json(payload)
                last_payload = payload
            await asyncio.sleep(settings.POLL_SECONDS)
    except WebSocketDisconnect:
        return

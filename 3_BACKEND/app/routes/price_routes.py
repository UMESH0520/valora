from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.services.price_service import compute
from app.database import SessionLocal
from app.models import Product, Price
from app.utils.ws_manager import ws_manager

router = APIRouter()


class PriceQuery(BaseModel):
    product_id: str
    margin_percent: float = 3.0


class FetchedItem(BaseModel):
    adapter: Optional[str] = None
    paise: Optional[int] = None
    rupees: Optional[float] = None
    confidence: Optional[float] = None
    raw: Optional[Dict[str, Any]] = None


class ProductInfo(BaseModel):
    product_id: str
    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    category: Optional[str] = None
    last_known_paise: Optional[int] = None
    last_known_price_readable: Optional[str] = None
    display_paise: Optional[int] = None
    display_price_readable: Optional[str] = None
    is_active: Optional[bool] = None


class PriceOutput(BaseModel):
    DISPLAY_PRICE: float
    FETCHED_PRICE: List[FetchedItem]
    PRODUCTS_LIST: List[ProductInfo]


def _product_to_dict(p: Product, latest_display: Optional[int]) -> Dict[str, Any]:
    return {
        "product_id": p.product_id,
        "name": p.name,
        "brand": p.brand,
        "model": p.model,
        "category": p.category,
        "last_known_paise": p.last_known_price,
        "last_known_price_readable": f"₹{(p.last_known_price or 0)/100:.2f}",
        "display_paise": latest_display,
        "display_price_readable": f"₹{(latest_display or 0)/100:.2f}" if latest_display is not None else None,
        "is_active": p.is_active,
    }


@router.post('/api/price', response_model=PriceOutput)
async def price(q: PriceQuery) -> PriceOutput:
    try:
        result = await compute(q.product_id, q.margin_percent)

        display_paise = result.get('display_paise') or result.get('lowest_paise')
        if display_paise is None:
            raise HTTPException(status_code=500, detail='price computation returned no value')
        display_rupees = round(display_paise / 100.0, 2)

        # Build FETCHED_PRICE from all_sources (per-API prices)
        fetched_raw = result.get('all_sources') or []
        fetched_price: List[Dict[str, Any]] = []
        for item in fetched_raw:
            try:
                paise = int(item.get('paise')) if isinstance(item.get('paise'), (int, float)) else None
            except Exception:
                paise = None
            fetched_price.append({
                "adapter": item.get('adapter') or (item.get('raw') or {}).get('adapter'),
                "paise": paise,
                "rupees": round((paise or 0) / 100.0, 2) if paise is not None else None,
                "confidence": item.get('confidence'),
                "raw": item.get('raw'),
            })

        # Build PRODUCT_DETAILS (all active products)
        db = SessionLocal()
        try:
            # Build latest display map in one query
            from sqlalchemy import func, and_
            from app.models import Price as PriceModel
            subq = (
                db.query(PriceModel.product_id, func.max(PriceModel.created_at).label("max_created"))
                .group_by(PriceModel.product_id)
                .subquery()
            )
            latest_rows = (
                db.query(PriceModel)
                .join(subq, and_(PriceModel.product_id == subq.c.product_id, PriceModel.created_at == subq.c.max_created))
                .all()
            )
            latest_map = {r.product_id: r.display_paise for r in latest_rows}

            products = db.query(Product).filter(Product.is_active == True).all()
            product_details = [_product_to_dict(p, latest_map.get(p.product_id)) for p in products]
        finally:
            db.close()

        return PriceOutput(
            DISPLAY_PRICE=display_rupees,
            FETCHED_PRICE=[FetchedItem(**i) for i in fetched_price],
            PRODUCTS_LIST=[ProductInfo(**d) for d in product_details],
        )
    except KeyError:
        raise HTTPException(status_code=404, detail='product not found')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/api/price/{product_id}', response_model=PriceOutput)
async def latest_price(product_id: str, margin_percent: float = 3.0) -> PriceOutput:
    db = SessionLocal()
    try:
        # Latest computed price
        row = (
            db.query(Price)
            .filter(Price.product_id == product_id)
            .order_by(Price.created_at.desc())
            .first()
        )
        if not row:
            # compute on-demand
            result = await compute(product_id, margin_percent)
            display_rupees = round(result['display_paise'] / 100.0, 2)
            fetched_price = [
                {
                    "adapter": i.get('adapter'),
                    "paise": i.get('paise'),
                    "rupees": round((i.get('paise') or 0) / 100.0, 2) if i.get('paise') is not None else None,
                    "confidence": i.get('confidence'),
                    "raw": i.get('raw'),
                }
                for i in result.get('all_sources') or []
            ]
        else:
            display_rupees = round((row.display_paise or 0) / 100.0, 2)
            fetched_price = []
        # Products list (include latest DISPLAY per product)
        from sqlalchemy import func, and_
        from app.models import Price as PriceModel
        subq = (
            db.query(PriceModel.product_id, func.max(PriceModel.created_at).label('max_created'))
            .group_by(PriceModel.product_id)
            .subquery()
        )
        latest_rows = (
            db.query(PriceModel)
            .join(subq, and_(PriceModel.product_id == subq.c.product_id, PriceModel.created_at == subq.c.max_created))
            .all()
        )
        latest_map = {r.product_id: r.display_paise for r in latest_rows}

        products = db.query(Product).filter(Product.is_active == True).all()
        product_details = [_product_to_dict(p, latest_map.get(p.product_id)) for p in products]
        return PriceOutput(
            DISPLAY_PRICE=display_rupees,
            FETCHED_PRICE=[FetchedItem(**i) for i in fetched_price],
            PRODUCTS_LIST=[ProductInfo(**d) for d in product_details],
        )
    finally:
        db.close()


@router.websocket('/ws/prices/{product_id}')
async def ws_prices(websocket: WebSocket, product_id: str):
    await ws_manager.connect(product_id, websocket)
    try:
        while True:
            # Keep the connection open; receive pings or ignore messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(product_id, websocket)
    except Exception:
        await ws_manager.disconnect(product_id, websocket)

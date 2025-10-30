from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import Product, Price

router = APIRouter()


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


class ProductsListResponse(BaseModel):
    PRODUCTS_LIST: List[ProductInfo]


class DisplayPriceResponse(BaseModel):
    DISPLAY_PRICE: float
    product_id: str
    lowest_paise: int
    margin_percent: float
    supporting_adapters: List[str]
    all_sources: List[Dict[str, Any]]


def build_latest_display_map(db: Session) -> Dict[str, Price]:
    # Latest Price row per product_id
    subq = (
        db.query(Price.product_id, func.max(Price.created_at).label("max_created"))
        .group_by(Price.product_id)
        .subquery()
    )
    latest_rows = (
        db.query(Price)
        .join(subq, and_(Price.product_id == subq.c.product_id, Price.created_at == subq.c.max_created))
        .all()
    )
    return {row.product_id: row for row in latest_rows}


def product_to_dict(p: Product, latest_map: Dict[str, Price]) -> Dict[str, Any]:
    lp = latest_map.get(p.product_id)
    display_paise = lp.display_paise if lp else None
    return {
        "product_id": p.product_id,
        "name": p.name,
        "brand": p.brand,
        "model": p.model,
        "category": p.category,
        "last_known_paise": p.last_known_price,
        "last_known_price_readable": f"₹{(p.last_known_price or 0)/100:.2f}",
        "display_paise": display_paise,
        "display_price_readable": f"₹{(display_paise or 0)/100:.2f}" if display_paise is not None else None,
        "is_active": p.is_active,
    }


@router.get("/api/products", response_model=ProductsListResponse)
def list_products(db: Session = Depends(get_db)) -> ProductsListResponse:
    latest_map = build_latest_display_map(db)
    products = db.query(Product).filter(Product.is_active == True).all()
    product_list = [ProductInfo(**product_to_dict(p, latest_map)) for p in products]
    return ProductsListResponse(PRODUCTS_LIST=product_list)


@router.get("/api/products/{product_id}/price", response_model=DisplayPriceResponse)
def get_price(product_id: str, db: Session = Depends(get_db)) -> DisplayPriceResponse:
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="product not found")

    # Latest price entry if exists
    price = (
        db.query(Price)
        .filter(Price.product_id == product_id)
        .order_by(Price.created_at.desc())
        .first()
    )

    if price:
        display = price.display_paise
        lowest = price.lowest_paise
        margin = price.margin_percent
        support = price.supporting_adapters
        all_sources = price.all_sources
    elif product.last_known_price is not None:
        lowest = product.last_known_price
        display = product.last_known_price
        margin = 0.0
        support = []
        all_sources = []
    else:
        raise HTTPException(status_code=404, detail="no price available for product")

    return DisplayPriceResponse(
        DISPLAY_PRICE=round(display / 100.0, 2),
        product_id=product_id,
        lowest_paise=lowest,
        margin_percent=margin,
        supporting_adapters=support,
        all_sources=all_sources,
    )

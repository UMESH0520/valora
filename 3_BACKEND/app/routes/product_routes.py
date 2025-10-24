from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models import Product, Price

router = APIRouter()


def product_to_dict(p: Product) -> Dict[str, Any]:
    return {
        "product_id": p.product_id,
        "name": p.name,
        "brand": p.brand,
        "model": p.model,
        "category": p.category,
        "last_known_paise": p.last_known_price,
        "last_known_price_readable": f"₹{(p.last_known_price or 0)/100:.2f}",
        "is_active": p.is_active,
    }


@router.get("/api/products")
def list_products(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    products = db.query(Product).filter(Product.is_active == True).all()
    return [product_to_dict(p) for p in products]


@router.get("/api/products/{product_id}/price")
def get_price(product_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
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

    return {
        "product_id": product_id,
        "lowest_paise": lowest,
        "display_paise": display,
        "display_price_readable": f"₹{display/100:.2f}",
        "margin_percent": margin,
        "supporting_adapters": support,
        "all_sources": all_sources,
    }
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import Product, Price

# Seed data derived from frontend components
SEED_PRODUCTS = [
    {"product_id": "1", "name": "Tailored Linen Blazer", "category": "Outerwear", "rupees": 19999},
    {"product_id": "2", "name": "Slim Fit Cotton Shirt", "category": "Shirts", "rupees": 7999},
    {"product_id": "3", "name": "Wool Blend Trousers", "category": "Bottoms", "rupees": 12999},
    {"product_id": "4", "name": "Lightweight Overcoat", "category": "Outerwear", "rupees": 24999},
    {"product_id": "5", "name": "Classic White Tee", "category": "Tops", "rupees": 4999},
    {"product_id": "6", "name": "Selvedge Denim Jeans", "category": "Bottoms", "rupees": 14999},
    {"product_id": "7", "name": "Chelsea Leather Boots", "category": "Footwear", "rupees": 17999},
    {"product_id": "8", "name": "Cashmere Sweater", "category": "Knitwear", "rupees": 18999},
    {"product_id": "pink-high-low-dress", "name": "Elegant High-Low Satin Dress in Blush Pink", "category": "Dresses", "rupees": 1999},
    {"product_id": "burgundy-chiffon-maxi-dress", "name": "Flowing Chiffon Maxi Dress with Sequin Belt in Burgundy", "category": "Dresses", "rupees": 1559},
]

DEFAULT_BRAND = "VALORA"


def seed():
    init_db()
    db: Session = SessionLocal()
    try:
        for item in SEED_PRODUCTS:
            paise = int(item["rupees"]) * 100
            # Upsert product
            p = db.query(Product).filter(Product.product_id == item["product_id"]).first()
            if not p:
                p = Product(
                    product_id=item["product_id"],
                    name=item["name"],
                    brand=DEFAULT_BRAND,
                    model=None,
                    category=item.get("category"),
                    last_known_price=paise,
                    urls={},
                    extra_data={},
                    is_active=True,
                )
                db.add(p)
            else:
                p.name = item["name"]
                p.brand = DEFAULT_BRAND
                p.category = item.get("category")
                p.last_known_price = paise

            # Insert a price row
            price = Price(
                product_id=item["product_id"],
                lowest_paise=paise,
                display_paise=paise,
                margin_percent=0.0,
                supporting_adapters=[],
                all_sources=[],
            )
            db.add(price)
        db.commit()
        print("Seeded demo products and prices.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

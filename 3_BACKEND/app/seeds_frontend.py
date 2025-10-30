from app.database import SessionLocal
from app.models import Product

FRONTEND_PRODUCTS = [
    # Index.tsx - newArrivals
    {
        "product_id": "1",
        "name": "Tailored Linen Blazer",
        "brand": "VALORA",
        "category": "Outerwear",
        "price_inr": 19999,
        "image": "https://images.unsplash.com/photo-1598522337630-9243f3e7bf9f?q=80&w=1974&auto=format&fit=crop",
    },
    {
        "product_id": "2",
        "name": "Slim Fit Cotton Shirt",
        "brand": "VALORA",
        "category": "Shirts",
        "price_inr": 7999,
        "image": "https://images.unsplash.com/photo-1617127365659-c47fa864d8bc?q=80&w=1974&auto=format&fit=crop",
    },
    {
        "product_id": "3",
        "name": "Wool Blend Trousers",
        "brand": "VALORA",
        "category": "Bottoms",
        "price_inr": 12999,
        "image": "https://images.unsplash.com/photo-1509946458702-4378df1e2560?q=80&w=1974&auto=format&fit=crop",
    },
    {
        "product_id": "4",
        "name": "Lightweight Overcoat",
        "brand": "VALORA",
        "category": "Outerwear",
        "price_inr": 24999,
        "image": "https://images.unsplash.com/photo-1541346160430-93fcee38d521?q=80&w=1974&auto=format&fit=crop",
    },
    # Index.tsx - bestSellers
    {
        "product_id": "5",
        "name": "Classic White Tee",
        "brand": "VALORA",
        "category": "Tops",
        "price_inr": 4999,
        "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?q=80&w=1780&auto=format&fit=crop",
    },
    {
        "product_id": "6",
        "name": "Selvedge Denim Jeans",
        "brand": "VALORA",
        "category": "Bottoms",
        "price_inr": 14999,
        "image": "https://images.unsplash.com/photo-1604176424472-17cd740f74e9?q=80&w=1780&auto=format&fit=crop",
    },
    {
        "product_id": "7",
        "name": "Chelsea Leather Boots",
        "brand": "VALORA",
        "category": "Footwear",
        "price_inr": 17999,
        "image": "https://images.unsplash.com/photo-1638247025967-b4e38f787b76?q=80&w=1935&auto=format&fit=crop",
    },
    {
        "product_id": "8",
        "name": "Cashmere Sweater",
        "brand": "VALORA",
        "category": "Knitwear",
        "price_inr": 18999,
        "image": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?q=80&w=1964&auto=format&fit=crop",
    },
    # NewArrivals.tsx - dresses
    {
        "product_id": "burgundy-chiffon-maxi-dress",
        "name": "Flowing Chiffon Maxi Dress with Sequin Belt in Burgundy",
        "brand": "VALORA",
        "category": "Dresses",
        "price_inr": 1559,
        "image": "/lovable-uploads/2699a1f6-cf46-49df-ba58-d8b2d6fcb21a.png",
    },
    {
        "product_id": "pink-high-low-dress",
        "name": "Elegant High-Low Satin Dress in Blush Pink",
        "brand": "VALORA",
        "category": "Dresses",
        "price_inr": 1999,
        "image": "/lovable-uploads/6cdafd3c-63c8-411e-a40c-93b3e5acbf29.png",
    },
    # Blazers page items
    {
        "product_id": "blazer-1",
        "name": "Tailored Linen Blazer",
        "brand": "VALORA",
        "category": "Blazers",
        "price_inr": 5999,
        "image": "https://images.unsplash.com/photo-1592878849125-7d3b0c45b495?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "product_id": "blazer-2",
        "name": "Classic Single-Breasted",
        "brand": "VALORA",
        "category": "Blazers",
        "price_inr": 6499,
        "image": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "product_id": "blazer-3",
        "name": "Modern Slim Fit",
        "brand": "VALORA",
        "category": "Blazers",
        "price_inr": 6299,
        "image": "https://images.unsplash.com/photo-1520975963841-56a1d8e8af1d?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "product_id": "blazer-4",
        "name": "Double-Breasted Wool",
        "brand": "VALORA",
        "category": "Blazers",
        "price_inr": 7499,
        "image": "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?q=80&w=1600&auto=format&fit=crop",
    },
    # Hoodies page items
    {
        "product_id": "hoodie-1",
        "name": "Classic Fleece Hoodie",
        "brand": "VALORA",
        "category": "Hoodies",
        "price_inr": 2999,
        "image": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "product_id": "hoodie-2",
        "name": "Oversized Street Hoodie",
        "brand": "VALORA",
        "category": "Hoodies",
        "price_inr": 3499,
        "image": "https://images.unsplash.com/photo-1503342217505-b0a15cf70489?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "product_id": "hoodie-3",
        "name": "Zip-Up Tech Hoodie",
        "brand": "VALORA",
        "category": "Hoodies",
        "price_inr": 3799,
        "image": "https://images.unsplash.com/photo-1512288094938-363287817259?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "product_id": "hoodie-4",
        "name": "Minimalist Pullover",
        "brand": "VALORA",
        "category": "Hoodies",
        "price_inr": 2899,
        "image": "https://images.unsplash.com/photo-1484515991647-c5760fcecfc7?q=80&w=1600&auto=format&fit=crop",
    },
    # Jeans page items
    {
        "product_id": "jeans-1",
        "name": "Selvedge Denim Jeans",
        "brand": "VALORA",
        "category": "Jeans",
        "price_inr": 4499,
        "image": "https://images.unsplash.com/photo-1562157873-818bc0726f68?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "product_id": "jeans-2",
        "name": "Slim Fit Stretch Jeans",
        "brand": "VALORA",
        "category": "Jeans",
        "price_inr": 3999,
        "image": "https://images.unsplash.com/photo-1516826957135-700dedea698c?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "product_id": "jeans-3",
        "name": "Relaxed Fit Vintage Wash",
        "brand": "VALORA",
        "category": "Jeans",
        "price_inr": 4299,
        "image": "https://images.unsplash.com/photo-1542272604-787c3835535d?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "product_id": "jeans-4",
        "name": "High-Rise Straight",
        "brand": "VALORA",
        "category": "Jeans",
        "price_inr": 4199,
        "image": "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=1600&auto=format&fit=crop",
    },
    # WomenTops page items
    {
        "product_id": "wt-1",
        "name": "Ribbed Knit Top",
        "brand": "VALORA",
        "category": "Women Tops",
        "price_inr": 1999,
        "image": "https://images.unsplash.com/photo-1534187454203-3b61184c6662?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "product_id": "wt-2",
        "name": "Silk Camisole",
        "brand": "VALORA",
        "category": "Women Tops",
        "price_inr": 2499,
        "image": "https://images.unsplash.com/photo-1520975963841-56a1d8e8af1d?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "product_id": "wt-3",
        "name": "Oversized Cotton Shirt",
        "brand": "VALORA",
        "category": "Women Tops",
        "price_inr": 2299,
        "image": "https://images.unsplash.com/photo-1520975916090-3105956dac38?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "product_id": "wt-4",
        "name": "Puff Sleeve Blouse",
        "brand": "VALORA",
        "category": "Women Tops",
        "price_inr": 2199,
        "image": "https://images.unsplash.com/photo-1548142813-c348350df52b?q=80&w=1600&auto=format&fit=crop",
    },
]


def seed_frontend_products() -> None:
    """Insert or update products to mirror the frontend items.
    Prices in frontend are INR; convert to paise for storage.
    """
    db = SessionLocal()
    try:
        for item in FRONTEND_PRODUCTS:
            pid = item["product_id"]
            p = db.query(Product).filter(Product.product_id == pid).first()
            paise = int(item["price_inr"]) * 100
            if p:
                # Update existing
                p.name = item["name"]
                p.brand = item["brand"]
                p.category = item["category"]
                p.last_known_price = paise
                p.is_active = True
                extra = p.extra_data or {}
                extra.update({"image": item.get("image")})
                p.extra_data = extra
            else:
                p = Product(
                    product_id=pid,
                    name=item["name"],
                    brand=item["brand"],
                    model=None,
                    category=item["category"],
                    last_known_price=paise,
                    urls={},
                    extra_data={"image": item.get("image")},
                    is_active=True,
                )
                db.add(p)
        db.commit()
    finally:
        db.close()

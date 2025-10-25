from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from .algorand import get_price as get_onchain_price
from .settings import settings

# Base price table in INR rupees (not paise)
BASE_PRICES: Dict[str, float] = {
    # Hoodies
    "hoodie-1": 2999, "hoodie-2": 3499, "hoodie-3": 3799, "hoodie-4": 2899,
    # Jeans
    "jeans-1": 4499, "jeans-2": 3999, "jeans-3": 4299, "jeans-4": 4199,
    # Blazers
    "blazer-1": 5999, "blazer-2": 6499, "blazer-3": 6299, "blazer-4": 7499,
    # Women Tops
    "wt-1": 1999, "wt-2": 2499, "wt-3": 2299, "wt-4": 2199,
    # Home page numeric IDs
    "1": 19999, "2": 7999, "3": 12999, "4": 24999,
    "5": 4999, "6": 14999, "7": 17999, "8": 18999,
    # New arrivals dresses
    "pink-high-low-dress": 1999,
    "burgundy-chiffon-maxi-dress": 1559,
    # Shop featured
    "shop-1": 3899, "shop-2": 1299, "shop-3": 4999, "shop-4": 5999,
}


def get_display_price(product_id: Optional[str]) -> Optional[float]:
    """Return price in rupees as float. Prefer on-chain, fallback to base table.
    - On-chain values are expected to already be rupees (float or int)."""
    if not product_id:
        # no product specified: try generic 'price'
        onchain = get_onchain_price(None)
        if onchain is not None:
            try:
                return float(onchain)
            except Exception:
                return None
        return None

    onchain = get_onchain_price(product_id)
    if onchain is not None:
        try:
            return float(onchain)
        except Exception:
            pass

    # Fallback to base price table
    if product_id in BASE_PRICES:
        return float(BASE_PRICES[product_id])
    return None


def get_price_detail(product_id: Optional[str]) -> Dict[str, Optional[float]]:
    """Return structured price detail including description and confidence.
    price is rupees float.
    confidence: 0..1 where on-chain is high (0.95), base fallback medium (0.7)."""
    price = None
    source = None
    confidence = None
    description = None

    if product_id:
        oc = get_onchain_price(product_id)
        if oc is not None:
            try:
                price = float(oc)
                source = "onchain"
                confidence = 0.95
                description = f"On-chain price from Algorand APP_ID={settings.APP_ID} for product_id={product_id}"
            except Exception:
                price = None
    else:
        oc = get_onchain_price(None)
        if oc is not None:
            try:
                price = float(oc)
                source = "onchain"
                confidence = 0.95
                description = f"On-chain generic display price from Algorand APP_ID={settings.APP_ID}"
            except Exception:
                price = None

    if price is None and product_id:
        if product_id in BASE_PRICES:
            price = float(BASE_PRICES[product_id])
            source = "catalog_base"
            confidence = 0.7
            description = f"Base catalog price for product_id={product_id}"

    return {
        "product_id": product_id,
        "price": price,
        "currency": "INR",
        "source": source,
        "confidence": confidence,
        "description": description,
    }


def get_prices(product_ids: List[str]) -> Dict[str, Optional[float]]:
    out: Dict[str, Optional[float]] = {}
    for pid in product_ids:
        out[pid] = get_display_price(pid)
    return out


def get_price_details(product_ids: List[str]) -> Dict[str, Dict[str, Optional[float]]]:
    return {pid: get_price_detail(pid) for pid in product_ids}

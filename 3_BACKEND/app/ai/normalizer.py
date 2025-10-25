import math
def to_paise(value: float) -> int:
    return int(math.floor(value * 100))
def normalize_results(raw_results: list) -> list:
    norm = []
    for r in raw_results:
        try:
            price = float(r.get('price'))
        except Exception:
            continue
        shipping = float(r.get('shipping') or 0)
        paise = to_paise(price + shipping)
        conf = float(r.get('confidence', 0.8))
        norm.append({'adapter': r.get('adapter'),'product_id': r.get('product_id'),'paise': paise,'confidence': conf,'raw': r})
    return norm

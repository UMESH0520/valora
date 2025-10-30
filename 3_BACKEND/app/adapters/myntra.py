import logging, re, os
from typing import Optional
from bs4 import BeautifulSoup
from .common import http_get_text, extract_rupee_candidates, pick_price_from_candidates

logger = logging.getLogger('valora.adapters.myntra')


def _extract_price_from_json(data) -> Optional[float]:
    """Best-effort extraction of a numeric price from arbitrary API JSON."""
    candidates = []
    try:
        def walk(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    lk = str(k).lower()
                    if any(p in lk for p in ["price", "amount", "current_price", "selling_price", "mrp", "discounted_price"]):
                        try:
                            if isinstance(v, (int, float)):
                                candidates.append(float(v))
                            elif isinstance(v, str):
                                m = re.search(r"\d[\d,]*\.?\d*", v)
                                if m:
                                    candidates.append(float(m.group(0).replace(',', '')))
                            elif isinstance(v, dict):
                                inner = v.get('value') or v.get('amount')
                                if isinstance(inner, (int, float)):
                                    candidates.append(float(inner))
                        except Exception:
                            pass
                    walk(v)
            elif isinstance(node, list):
                for it in node:
                    walk(it)
        walk(data)
    except Exception:
        return None
    if not candidates:
        return None
    candidates.sort()
    return candidates[len(candidates)//2]


async def _fetch_via_rapidapi(session, product):
    key = os.getenv('MYNTRA_RAPIDAPI_KEY')
    host = os.getenv('MYNTRA_RAPIDAPI_HOST')
    if not key or not host:
        return None
    path = os.getenv('MYNTRA_RAPIDAPI_SEARCH_PATH', '/search')
    query = f"{product['name']} {product['brand']} {product.get('model','')}".strip()
    url = f"https://{host}{path}"
    headers = {
        'X-RapidAPI-Key': key,
        'X-RapidAPI-Host': host,
    }
    params_variants = [
        { 'q': query },
        { 'query': query },
        { 'keyword': query },
        { 'search': query },
    ]
    for params in params_variants:
        try:
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status >= 400:
                    continue
                try:
                    data = await resp.json(content_type=None)
                except Exception:
                    text = await resp.text()
                    m = re.search(r"\d[\d,]*\.?\d*", text)
                    if not m:
                        continue
                    price = float(m.group(0).replace(',', ''))
                    return {'adapter':'myntra','product_id':product['product_id'],'price': price,'shipping':0.0,'confidence':0.9}
                price = _extract_price_from_json(data)
                if price is not None and price > 0:
                    return {'adapter':'myntra','product_id':product['product_id'],'price': price,'shipping':0.0,'confidence':0.92}
        except Exception as e:
            logger.info('myntra rapidapi attempt failed: %s', e)
            continue
    return None


async def fetch(session, product):
    # 1) Try RapidAPI first
    rapid = await _fetch_via_rapidapi(session, product)
    if rapid is not None:
        return rapid

    # 2) Fallback to direct web scraping (previous implementation)
    try:
        url = product.get('urls', {}).get('myntra')
        if url:
            text = await http_get_text(session, url, total_timeout=10.0)
        else:
            query = f"{product['name']} {product['brand']}"
            search_url = f"https://www.myntra.com/{query.replace(' ', '-')}"
            text = await http_get_text(session, search_url, total_timeout=10.0)
        if not text:
            logger.info('myntra: empty response')
            return None

        soup = BeautifulSoup(text, 'lxml')
        tag = soup.select_one('.pdp-price') or soup.select_one('.pdp-price span')
        price = None
        if tag:
            m = re.search(r"\d[\d,]*\.?\d*", tag.get_text())
            if m:
                price = float(m.group(0).replace(',', ''))
        if price is None:
            cands = extract_rupee_candidates(text)
            price = pick_price_from_candidates(cands)
        if price is None:
            logger.info('myntra: price not found after fallbacks')
            return None

        return {
            'adapter': 'myntra',
            'product_id': product['product_id'],
            'price': price,
            'shipping': 0.0,
            'confidence': 0.84 if tag else 0.68,
        }
    except Exception:
        logger.exception('myntra adapter error')
        return None

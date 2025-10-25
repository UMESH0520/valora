import logging, re, os, math
from typing import Optional
from bs4 import BeautifulSoup

logger = logging.getLogger('valora.adapters.amazon')


def _extract_price_from_json(data) -> Optional[float]:
    """Best-effort extraction of a numeric price from arbitrary API JSON."""
    candidates = []
    try:
        def walk(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    lk = str(k).lower()
                    if any(p in lk for p in ["price", "amount", "current_price", "offerprice", "saleprice"]):
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
    key = os.getenv('AMAZON_RAPIDAPI_KEY')
    host = os.getenv('AMAZON_RAPIDAPI_HOST')
    if not key or not host:
        return None
    path = os.getenv('AMAZON_RAPIDAPI_SEARCH_PATH', '/product-search')
    country = os.getenv('AMAZON_COUNTRY', 'IN')
    query = f"{product['name']} {product['brand']} {product.get('model','')}".strip()
    url = f"https://{host}{path}"
    headers = {
        'X-RapidAPI-Key': key,
        'X-RapidAPI-Host': host,
    }
    params_variants = [
        { 'q': query, 'country': country },
        { 'query': query, 'country': country },
        { 'keyword': query, 'country': country },
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
                    return {'adapter':'amazon','product_id':product['product_id'],'price': price,'shipping':0.0,'confidence':0.9}
                price = _extract_price_from_json(data)
                if price is not None and price > 0:
                    return {'adapter':'amazon','product_id':product['product_id'],'price': price,'shipping':0.0,'confidence':0.92}
        except Exception as e:
            logger.info('amazon rapidapi attempt failed: %s', e)
            continue
    return None


async def _fetch_via_webscrapingapi(session, product):
    key = os.getenv('WEBSCRAPINGAPI_ECOM_API_KEY')
    if not key:
        return None
    domain = os.getenv('AMAZON_DOMAIN', 'amazon.in')
    query = f"{product['name']} {product['brand']} {product.get('model','')}".strip()
    url = 'https://ecom.webscrapingapi.com/v1'
    params = {
        'q': query,
        'type': 'search',
        'amazon_domain': domain,
        'engine': 'amazon',
        'api_key': key,
    }
    try:
        async with session.get(url, params=params) as resp:
            if resp.status >= 400:
                return None
            try:
                data = await resp.json(content_type=None)
            except Exception:
                text = await resp.text()
                m = re.search(r"\d[\d,]*\.?\d*", text)
                if not m:
                    return None
                price = float(m.group(0).replace(',', ''))
                return {'adapter':'amazon','product_id':product['product_id'],'price': price,'shipping':0.0,'confidence':0.93}
            # Prefer specific fields if present
            try:
                results = data.get('results') or data.get('data') or []
                if isinstance(results, list) and results:
                    cand_price = _extract_price_from_json(results[0])
                    if not cand_price:
                        # try scan all
                        cand_price = _extract_price_from_json({'results': results[:5]})
                else:
                    cand_price = _extract_price_from_json(data)
            except Exception:
                cand_price = _extract_price_from_json(data)
            if cand_price and cand_price > 0:
                return {'adapter':'amazon','product_id':product['product_id'],'price': float(cand_price),'shipping':0.0,'confidence':0.94}
    except Exception as e:
        logger.info('amazon webscrapingapi attempt failed: %s', e)
    return None


async def fetch(session, product):
    # 1) WebscrapingAPI e-commerce
    ws = await _fetch_via_webscrapingapi(session, product)
    if ws is not None:
        return ws
    # 2) RapidAPI
    rapid = await _fetch_via_rapidapi(session, product)
    if rapid is not None:
        return rapid
    # 3) Fallback to HTML scraping
    try:
        url = product.get('urls', {}).get('amazon')
        if url:
            async with session.get(url, headers={'User-Agent':'VALORA-Bot'}) as resp:
                text = await resp.text()
        else:
            query = f"{product['name']} {product['brand']} {product.get('model','') }"
            search_url = f"https://www.amazon.in/s?k={query.replace(' ','+')}"
            async with session.get(search_url, headers={'User-Agent':'VALORA-Bot'}) as resp:
                text = await resp.text()
        soup = BeautifulSoup(text, 'lxml')
        tag = soup.select_one('.a-price .a-offscreen') or soup.select_one('#priceblock_ourprice')
        if not tag:
            logger.info('amazon: price tag not found')
            return None
        m = re.search(r"\d[\d,]*\.?\d*", tag.get_text())
        if not m:
            return None
        price = float(m.group(0).replace(',',''))
        return {'adapter':'amazon','product_id':product['product_id'],'price': price,'shipping':0.0,'confidence':0.9}
    except Exception as e:
        logger.exception('amazon adapter error: %s', e)
        return None

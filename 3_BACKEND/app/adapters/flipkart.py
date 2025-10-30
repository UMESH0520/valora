import logging, re, os, math
from typing import Optional
from bs4 import BeautifulSoup
from .common import http_get_text
logger = logging.getLogger('valora.adapters.flipkart')


def _extract_price_from_json(data) -> Optional[float]:
    candidates = []
    try:
        def walk(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    lk = str(k).lower()
                    if any(p in lk for p in ["price", "amount", "selling_price", "current_price", "saleprice"]):
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
    host = os.getenv('FLIPKART_RAPIDAPI_HOST')
    key = os.getenv('FLIPKART_RAPIDAPI_KEY') or os.getenv('FLIPKART_API_KEY')
    if not host or not key:
        return None
    query = f"{product['name']} {product['brand']} {product.get('model','')}".strip()
    url = f"https://{host}/product-search"
    headers = {
        'X-RapidAPI-Key': key,
        'X-RapidAPI-Host': host,
    }
    params = { 'q': query, 'page': '1', 'sort_by': 'popularity' }
    try:
        async with session.get(url, headers=headers, params=params) as resp:
            if resp.status >= 400:
                logger.info('flipkart rapidapi failed: %s', resp.status)
                return None
            try:
                data = await resp.json(content_type=None)
            except Exception:
                text = await resp.text()
                m = re.search(r"\d[\d,]*\.?\d*", text)
                if not m:
                    return None
                price = float(m.group(0).replace(',', ''))
                return {'adapter':'flipkart','product_id':product['product_id'],'price': price,'shipping':0.0,'confidence':0.93}
            price = _extract_price_from_json(data)
            if price and price > 0:
                return {'adapter':'flipkart','product_id':product['product_id'],'price': float(price),'shipping':0.0,'confidence':0.95}
    except Exception as e:
        logger.info('flipkart rapidapi error: %s', e)
    return None


async def fetch(session, product):
    # 1) Try RapidAPI first
    rapid = await _fetch_via_rapidapi(session, product)
    if rapid is not None:
        return rapid
    
    # 2) Fallback to web scraping
    try:
        url = product.get('urls', {}).get('flipkart')
        if url:
            text = await http_get_text(session, url)
        else:
            query = f"{product['name']} {product['brand']} {product.get('model','')}"
            search_url = f"https://www.flipkart.com/search?q={query.replace(' ','+')}"
            text = await http_get_text(session, search_url)
        if not text:
            logger.info('flipkart: empty response')
            return None
        soup = BeautifulSoup(text, 'lxml')
        tag = soup.select_one('._30jeq3') or soup.select_one('div._1vC4OE') or soup.select_one('._16Jk6d')
        if not tag:
            # try regex fallback
            m_all = re.findall(r"₹\s*([0-9][0-9,]*\.?[0-9]*)", text)
            if not m_all:
                logger.info('flipkart: price tag not found')
                return None
            try:
                price = float(str(min([float(x.replace(',','')) for x in m_all])))
            except Exception:
                return None
            return {'adapter':'flipkart','product_id':product['product_id'],'price': price,'shipping':0.0,'confidence':0.7}
        m = re.search(r"\d[\d,]*\.?\d*", tag.get_text())
        if not m:
            return None
        price = float(m.group(0).replace(',',''))
        return {'adapter':'flipkart','product_id':product['product_id'],'price': price,'shipping':0.0,'confidence':0.88}
    except Exception:
        logger.exception('flipkart adapter error')
        return None

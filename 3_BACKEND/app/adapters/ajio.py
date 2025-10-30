import logging, re, os
from bs4 import BeautifulSoup
from .common import http_get_text, extract_rupee_candidates, pick_price_from_candidates

logger = logging.getLogger('valora.adapters.ajio')


async def _fetch_via_rapidapi(session, product):
    host = os.getenv('AJIO_RAPIDAPI_HOST')
    key = os.getenv('AJIO_RAPIDAPI_KEY')
    if not host or not key:
        return None
    # If product has an Ajio URL, try to extract slug/id from it
    url = product.get('urls', {}).get('ajio')
    slug = None
    if url:
        m = re.search(r"ajio\.com/[^/]+/([\w-]+)", url)
        if m:
            slug = m.group(1)
    # As a fallback, allow env override for testing
    if not slug:
        slug = os.getenv('AJIO_TEST_SLUG')
    if not slug:
        return None
    api_url = f"https://{host}/product/{slug}"
    headers = {
        'X-RapidAPI-Key': key,
        'X-RapidAPI-Host': host,
    }
    try:
        async with session.get(api_url, headers=headers) as resp:
            if resp.status >= 400:
                return None
            try:
                data = await resp.json(content_type=None)
            except Exception:
                text = await resp.text()
                m2 = re.search(r"\d[\d,]*\.?\d*", text)
                if not m2:
                    return None
                price = float(m2.group(0).replace(',', ''))
                return {'adapter':'ajio','product_id':product['product_id'],'price': price,'shipping':0.0,'confidence':0.9}
            # naive price extraction
            from .flipkart import _extract_price_from_json
            price = _extract_price_from_json(data)
            if price and price > 0:
                return {'adapter':'ajio','product_id':product['product_id'],'price': float(price),'shipping':0.0,'confidence':0.92}
    except Exception as e:
        logger.info('ajio rapidapi error: %s', e)
    return None


async def fetch(session, product):
    """Fetch product price from Ajio"""
    # 1) Try RapidAPI if configured
    rapid = await _fetch_via_rapidapi(session, product)
    if rapid is not None:
        return rapid
    try:
        url = product.get('urls', {}).get('ajio')
        if url:
            text = await http_get_text(session, url)
        else:
            query = f"{product['name']} {product['brand']}"
            search_url = f"https://www.ajio.com/search/?text={query.replace(' ', '%20')}"
            text = await http_get_text(session, search_url)
        if not text:
            logger.info('ajio: empty response')
            return None
        
        soup = BeautifulSoup(text, 'lxml')
        
        # Try multiple selectors for Ajio price tags
        tag = (
            soup.select_one('.prod-sp') or
            soup.select_one('.price-value') or
            soup.select_one('span.price')
        )
        
        price = None
        if tag:
            m = re.search(r"\d[\d,]*\.?\d*", tag.get_text())
            if m:
                price = float(m.group(0).replace(',', ''))
        if price is None:
            # Fallback: fuzzy regex over whole page
            cands = extract_rupee_candidates(text)
            price = pick_price_from_candidates(cands)
        if price is None:
            logger.info('ajio: price not found after fallbacks')
            return None
        
        return {
            'adapter': 'ajio',
            'product_id': product['product_id'],
            'price': price,
            'shipping': 0.0,
            'confidence': 0.8 if tag else 0.65
        }
    except Exception as e:
        logger.exception('ajio adapter error: %s', e)
        return None

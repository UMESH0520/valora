import logging, re
from bs4 import BeautifulSoup
from .common import http_get_text, extract_rupee_candidates, pick_price_from_candidates

logger = logging.getLogger('valora.adapters.snapdeal')


async def fetch(session, product):
    """Fetch product price from Snapdeal"""
    try:
        url = product.get('urls', {}).get('snapdeal')
        if url:
            text = await http_get_text(session, url)
        else:
            query = f"{product['name']} {product['brand']} {product.get('model', '')}"
            search_url = f"https://www.snapdeal.com/search?keyword={query.replace(' ', '+')}"
            text = await http_get_text(session, search_url)
        if not text:
            logger.info('snapdeal: empty response')
            return None
        
        soup = BeautifulSoup(text, 'lxml')
        
        # Try multiple selectors for Snapdeal price tags
        tag = (
            soup.select_one('.payBlkBig') or
            soup.select_one('.product-price') or
            soup.select_one('span.lfloat.product-price')
        )
        
        price = None
        if tag:
            m = re.search(r"\d[\d,]*\.?\d*", tag.get_text())
            if m:
                price = float(m.group(0).replace(',', ''))
        if price is None:
            cands = extract_rupee_candidates(text)
            price = pick_price_from_candidates(cands)
        if price is None:
            logger.info('snapdeal: price not found after fallbacks')
            return None
        
        return {
            'adapter': 'snapdeal',
            'product_id': product['product_id'],
            'price': price,
            'shipping': 0.0,
            'confidence': 0.82 if tag else 0.65
        }
    except Exception as e:
        logger.exception('snapdeal adapter error: %s', e)
        return None

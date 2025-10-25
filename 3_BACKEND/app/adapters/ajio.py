import logging, re
from bs4 import BeautifulSoup
from .common import http_get_text, extract_rupee_candidates, pick_price_from_candidates

logger = logging.getLogger('valora.adapters.ajio')


async def fetch(session, product):
    """Fetch product price from Ajio"""
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

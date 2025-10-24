import logging, re
from bs4 import BeautifulSoup

logger = logging.getLogger('valora.adapters.ajio')


async def fetch(session, product):
    """Fetch product price from Ajio"""
    try:
        url = product.get('urls', {}).get('ajio')
        if url:
            async with session.get(url, headers={'User-Agent': 'VALORA-Bot'}) as resp:
                text = await resp.text()
        else:
            query = f"{product['name']} {product['brand']}"
            search_url = f"https://www.ajio.com/search/?text={query.replace(' ', '%20')}"
            async with session.get(search_url, headers={'User-Agent': 'VALORA-Bot'}) as resp:
                text = await resp.text()
        
        soup = BeautifulSoup(text, 'lxml')
        
        # Try multiple selectors for Ajio price tags
        tag = (
            soup.select_one('.prod-sp') or
            soup.select_one('.price-value') or
            soup.select_one('span.price')
        )
        
        if not tag:
            logger.info('ajio: price tag not found')
            return None
        
        m = re.search(r"\d[\d,]*\.?\d*", tag.get_text())
        if not m:
            return None
        
        price = float(m.group(0).replace(',', ''))
        
        return {
            'adapter': 'ajio',
            'product_id': product['product_id'],
            'price': price,
            'shipping': 0.0,
            'confidence': 0.87
        }
    except Exception as e:
        logger.exception('ajio adapter error: %s', e)
        return None

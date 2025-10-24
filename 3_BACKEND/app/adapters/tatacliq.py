import logging, re
from bs4 import BeautifulSoup

logger = logging.getLogger('valora.adapters.tatacliq')


async def fetch(session, product):
    """Fetch product price from Tata CLiQ"""
    try:
        url = product.get('urls', {}).get('tatacliq')
        if url:
            async with session.get(url, headers={'User-Agent': 'VALORA-Bot'}) as resp:
                text = await resp.text()
        else:
            query = f"{product['name']} {product['brand']} {product.get('model', '')}"
            search_url = f"https://www.tatacliq.com/search/?searchCategory=all&text={query.replace(' ', '%20')}"
            async with session.get(search_url, headers={'User-Agent': 'VALORA-Bot'}) as resp:
                text = await resp.text()
        
        soup = BeautifulSoup(text, 'lxml')
        
        # Try multiple selectors for Tata CLiQ price tags
        tag = (
            soup.select_one('.ProductDescription__priceHolder') or
            soup.select_one('.ProductDetailsMainCard__price__newPrice') or
            soup.select_one('h3.ProductDescription__priceHolder')
        )
        
        if not tag:
            logger.info('tatacliq: price tag not found')
            return None
        
        m = re.search(r"\d[\d,]*\.?\d*", tag.get_text())
        if not m:
            return None
        
        price = float(m.group(0).replace(',', ''))
        
        return {
            'adapter': 'tatacliq',
            'product_id': product['product_id'],
            'price': price,
            'shipping': 0.0,
            'confidence': 0.86
        }
    except Exception as e:
        logger.exception('tatacliq adapter error: %s', e)
        return None

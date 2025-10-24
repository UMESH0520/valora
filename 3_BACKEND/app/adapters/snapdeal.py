import logging, re
from bs4 import BeautifulSoup

logger = logging.getLogger('valora.adapters.snapdeal')


async def fetch(session, product):
    """Fetch product price from Snapdeal"""
    try:
        url = product.get('urls', {}).get('snapdeal')
        if url:
            async with session.get(url, headers={'User-Agent': 'VALORA-Bot'}) as resp:
                text = await resp.text()
        else:
            query = f"{product['name']} {product['brand']} {product.get('model', '')}"
            search_url = f"https://www.snapdeal.com/search?keyword={query.replace(' ', '+')}"
            async with session.get(search_url, headers={'User-Agent': 'VALORA-Bot'}) as resp:
                text = await resp.text()
        
        soup = BeautifulSoup(text, 'lxml')
        
        # Try multiple selectors for Snapdeal price tags
        tag = (
            soup.select_one('.payBlkBig') or
            soup.select_one('.product-price') or
            soup.select_one('span.lfloat.product-price')
        )
        
        if not tag:
            logger.info('snapdeal: price tag not found')
            return None
        
        m = re.search(r"\d[\d,]*\.?\d*", tag.get_text())
        if not m:
            return None
        
        price = float(m.group(0).replace(',', ''))
        
        return {
            'adapter': 'snapdeal',
            'product_id': product['product_id'],
            'price': price,
            'shipping': 0.0,
            'confidence': 0.85
        }
    except Exception as e:
        logger.exception('snapdeal adapter error: %s', e)
        return None

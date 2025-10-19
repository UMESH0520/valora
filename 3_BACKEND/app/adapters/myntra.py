import logging, re
from bs4 import BeautifulSoup
logger = logging.getLogger('valora.adapters.myntra')

async def fetch(session, product):
    try:
        url = product.get('urls', {}).get('myntra')
        if url:
            async with session.get(url, headers={'User-Agent':'VALORA-Bot'}) as resp:
                text = await resp.text()
        else:
            query = f"{product['name']} {product['brand']}"
            search_url = f"https://www.myntra.com/{query.replace(' ','-')}"
            async with session.get(search_url, headers={'User-Agent':'VALORA-Bot'}) as resp:
                text = await resp.text()
        soup = BeautifulSoup(text, 'lxml')
        tag = soup.select_one('.pdp-price') or soup.select_one('.pdp-price span')
        if not tag:
            logger.info('myntra: price tag not found')
            return None
        m = re.search(r"\d[\d,]*\.?\d*", tag.get_text())
        if not m:
            return None
        price = float(m.group(0).replace(',',''))
        return {'adapter':'myntra','product_id':product['product_id'],'price': price,'shipping':0.0,'confidence':0.86}
    except Exception:
        logger.exception('myntra adapter error')
        return None

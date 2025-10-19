import logging, re
from bs4 import BeautifulSoup
logger = logging.getLogger('valora.adapters.amazon')

async def fetch(session, product):
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

import logging, re
from bs4 import BeautifulSoup
logger = logging.getLogger('valora.adapters.flipkart')

async def fetch(session, product):
    try:
        url = product.get('urls', {}).get('flipkart')
        if url:
            async with session.get(url, headers={'User-Agent':'VALORA-Bot'}) as resp:
                text = await resp.text()
        else:
            query = f"{product['name']} {product['brand']} {product.get('model','')}"
            search_url = f"https://www.flipkart.com/search?q={query.replace(' ','+')}"
            async with session.get(search_url, headers={'User-Agent':'VALORA-Bot'}) as resp:
                text = await resp.text()
        soup = BeautifulSoup(text, 'lxml')
        tag = soup.select_one('._30jeq3') or soup.select_one('div._1vC4OE')
        if not tag:
            logger.info('flipkart: price tag not found')
            return None
        m = re.search(r"\d[\d,]*\.?\d*", tag.get_text())
        if not m:
            return None
        price = float(m.group(0).replace(',',''))
        return {'adapter':'flipkart','product_id':product['product_id'],'price': price,'shipping':0.0,'confidence':0.88}
    except Exception:
        logger.exception('flipkart adapter error')
        return None

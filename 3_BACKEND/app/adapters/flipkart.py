import logging, re, os
from bs4 import BeautifulSoup
from .common import http_get_text
logger = logging.getLogger('valora.adapters.flipkart')


async def _fetch_via_api(session, product):
    """Fetch product data using Flipkart API"""
    api_key = os.getenv('FLIPKART_API_KEY')
    if not api_key:
        return None
    
    try:
        # Construct API URL based on product search
        query = f"{product['name']} {product['brand']} {product.get('model','')}".strip()
        
        # Flipkart API endpoint (adjust based on actual API documentation)
        api_url = "https://api.flipkart.com/v1/products/search"
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'VALORA-Bot/1.0'
        }
        
        params = {
            'q': query,
            'limit': 10
        }
        
        async with session.get(api_url, headers=headers, params=params) as resp:
            if resp.status >= 400:
                logger.info('flipkart api request failed with status %s', resp.status)
                return None
                
            try:
                data = await resp.json()
            except Exception as e:
                logger.info('flipkart api json parsing failed: %s', e)
                return None
            
            # Extract price from API response (adjust based on actual API structure)
            products = data.get('products', [])
            if products:
                product_data = products[0]  # Take first result
                price_info = product_data.get('price', {})
                
                # Try different price fields
                price = None
                for field in ['selling_price', 'current_price', 'price', 'amount']:
                    if field in price_info:
                        price = float(price_info[field])
                        break
                
                if price and price > 0:
                    return {
                        'adapter': 'flipkart',
                        'product_id': product['product_id'],
                        'price': price,
                        'shipping': price_info.get('shipping_cost', 0.0),
                        'confidence': 0.95
                    }
                    
    except Exception as e:
        logger.info('flipkart api error: %s', e)
    
    return None


async def fetch(session, product):
    # 1) Try API first (if API key is available)
    api_result = await _fetch_via_api(session, product)
    if api_result is not None:
        return api_result
    
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

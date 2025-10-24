import logging, re, os
from bs4 import BeautifulSoup
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

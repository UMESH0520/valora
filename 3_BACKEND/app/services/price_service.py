import asyncio, logging
from app.ai.fetcher import fetch_product_prices
from app.contracts.submitter import submit_update

logger = logging.getLogger('valora.price_service')

PRODUCT_REGISTRY = {
    'VAL-PRD-001':{
        'product_id':'VAL-PRD-001',
        'name':'Demo Product Alpha 256GB',
        'brand':'DemoBrand',
        'model':'DB-256',
        'category':'Electronics',
        'last_known_price': 100000,
        'urls':{}
    }
}

async def compute(product_id: str, margin_percent: float = 3.0):
    if product_id not in PRODUCT_REGISTRY:
        raise KeyError('product not found')
    product = PRODUCT_REGISTRY[product_id]
    aggregated = await fetch_product_prices(product)
    lowest = aggregated.get('final_lowest_paise')
    if lowest is None:
        raise RuntimeError('no price found')
    display = int(lowest * (100 - int(margin_percent)) / 100)
    result = {
        'product_id': product_id,
        'lowest_paise': lowest,
        'display_paise': display,
        'display_price_readable': f'₹{display/100:.2f}',
        'supporting_adapters': aggregated.get('support'),
        'all_sources': aggregated.get('all')
    }
    try:
        submit_update(product_id, lowest)
    except Exception:
        logger.exception('submit failed - continuing')
    return result

def get_display_price_sync(product_id: str, margin_percent: float = 3.0):
    return asyncio.get_event_loop().run_until_complete(compute(product_id, margin_percent))

import asyncio, logging
from sqlalchemy.orm import Session
from app.ai.fetcher import fetch_product_prices
from app.contracts.submitter import submit_update
from app.database import SessionLocal
from app.models import Product, Price

logger = logging.getLogger('valora.price_service')


async def compute(product_id: str, margin_percent: float = 3.0):
    db: Session = SessionLocal()
    try:
        product: Product | None = db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            raise KeyError('product not found')

        # Prepare minimal product dict for adapters
        product_input = {
            'product_id': product.product_id,
            'name': product.name,
            'brand': product.brand,
            'model': product.model,
            'category': product.category,
            'last_known_price': product.last_known_price,
            'urls': product.urls or {},
        }

        lowest = None
        aggregated = None
        try:
            aggregated = await fetch_product_prices(product_input)
            lowest = aggregated.get('final_lowest_paise')
        except Exception:
            logger.info('adapter aggregation failed; falling back to last_known_price')

        if lowest is None:
            lowest = product.last_known_price
        if lowest is None:
            raise RuntimeError('no price found')

        display = int(lowest * (100 - int(margin_percent)) / 100)
        blockchain_tx_id = None
        # Try to submit to blockchain (best-effort)
        try:
            submit_result = submit_update(product_id, lowest)
            blockchain_tx_id = submit_result.get('tx_id') if isinstance(submit_result, dict) else None
        except Exception:
            logger.exception('submit failed - continuing')

        # Persist computed price to DB
        try:
            price_row = Price(
                product_id=product_id,
                lowest_paise=lowest,
                display_paise=display,
                margin_percent=float(margin_percent),
                supporting_adapters=(aggregated or {}).get('support', []),
                all_sources=(aggregated or {}).get('all', []),
                blockchain_tx_id=blockchain_tx_id,
            )
            db.add(price_row)
            db.commit()
        except Exception:
            logger.exception('failed to persist price row - continuing')

        result = {
            'product_id': product_id,
            'lowest_paise': lowest,
            'display_paise': display,
            'display_price_readable': f'₹{display/100:.2f}',
            'margin_percent': float(margin_percent),
            'supporting_adapters': (aggregated or {}).get('support', []),
            'all_sources': (aggregated or {}).get('all', []),
            'blockchain_tx_id': blockchain_tx_id,
        }
        return result
    finally:
        db.close()


def get_display_price_sync(product_id: str, margin_percent: float = 3.0):
    return asyncio.get_event_loop().run_until_complete(compute(product_id, margin_percent))

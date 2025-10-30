import asyncio, logging
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.ai.fetcher import fetch_product_prices
from app.contracts.submitter import submit_update
from app.database import SessionLocal
from app.models import Product, Price
from app.utils.ws_manager import ws_manager

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

        # First transaction: record lowest price on-chain (if configured)
        first_tx_id = None
        first_tx_success = False
        try:
            first_result = submit_update(product_id, lowest)
            first_tx_id = first_result.get('tx_id') if isinstance(first_result, dict) else None
            first_tx_success = first_result.get('status') == 'confirmed' if isinstance(first_result, dict) else False
            if first_tx_success:
                logger.info(f"First tx confirmed for {product_id} (lowest={lowest}) -> tx_id={first_tx_id}")
                # Update product last known price on successful chain write
                product.last_known_price = lowest
                product.updated_at = func.now()
        except Exception:
            logger.exception('first blockchain submit failed - continuing')

        # Second transaction: record DISPLAY price (lowest minus margin)
        second_tx_id = None
        second_tx_success = False
        try:
            second_result = submit_update(product_id, display)
            second_tx_id = second_result.get('tx_id') if isinstance(second_result, dict) else None
            second_tx_success = second_result.get('status') == 'confirmed' if isinstance(second_result, dict) else False
            if second_tx_success:
                logger.info(f"Second tx confirmed for {product_id} (display={display}) -> tx_id={second_tx_id}")
        except Exception:
            logger.exception('second blockchain submit failed - continuing')

        # Persist computed price to DB
        try:
            price_row = Price(
                product_id=product_id,
                lowest_paise=lowest,
                display_paise=display,
                margin_percent=float(margin_percent),
                supporting_adapters=(aggregated or {}).get('support', []),
                all_sources=(aggregated or {}).get('all', []),
                blockchain_tx_id=second_tx_id or first_tx_id,
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
            'blockchain_tx_id_lowest': first_tx_id,
            'blockchain_tx_id_display': second_tx_id,
            'blockchain_success_lowest': first_tx_success,
            'blockchain_success_display': second_tx_success,
        }

        # Push live update to websocket subscribers
        try:
            await ws_manager.broadcast(product_id, {
                'type': 'price_update',
                'product_id': product_id,
                'display_paise': display,
                'display_price_readable': result['display_price_readable'],
                'lowest_paise': lowest,
                'margin_percent': float(margin_percent),
                'blockchain': {
                    'lowest_tx_id': first_tx_id,
                    'display_tx_id': second_tx_id,
                    'lowest_confirmed': first_tx_success,
                    'display_confirmed': second_tx_success,
                }
            })
        except Exception:
            logger.debug('websocket broadcast skipped or failed')

        return result
    finally:
        db.close()


def get_display_price_sync(product_id: str, margin_percent: float = 3.0):
    return asyncio.get_event_loop().run_until_complete(compute(product_id, margin_percent))

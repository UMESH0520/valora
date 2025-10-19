import asyncio, logging
from app.adapters import ADAPTER_LIST, get_client_session
from app.ai.normalizer import normalize_results
from app.ai.aggregator import aggregate_prices

logger = logging.getLogger('valora.ai.fetcher')

async def fetch_product_prices(product: dict):
    tasks = []
    async with get_client_session() as session:
        for adapter in ADAPTER_LIST:
            tasks.append(adapter.fetch(session, product))
        raw = await asyncio.gather(*tasks, return_exceptions=True)
    results = []
    for r in raw:
        if r is None:
            continue
        if isinstance(r, Exception):
            logger.warning('adapter exception: %s', r)
            continue
        results.append(r)
    if not results:
        raise RuntimeError('no adapter results')
    normalized = normalize_results(results)
    aggregated = aggregate_prices(normalized)
    return aggregated

import os, logging
from algosdk.v2client import algod

logger = logging.getLogger('valora.contracts')

ALGOD_ADDRESS = os.getenv('ALGOD_ADDRESS')
ALGOD_TOKEN = os.getenv('ALGOD_API_TOKEN')
ORACLE_MNEMONIC = os.getenv('ORACLE_MNEMONIC')
APP_ID = int(os.getenv('APP_ID') or '0')

def get_algod_client():
    if not ALGOD_ADDRESS:
        raise EnvironmentError('ALGOD_ADDRESS not set')
    return algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

def submit_update(product_id: str, final_paise: int):
    try:
        client = get_algod_client()
    except Exception as e:
        logger.info('Algod not configured or env missing: %s', e)
        return {'status':'skipped'}
    logger.info('Would submit on-chain: product=%s price=%s', product_id, final_paise)
    return {'status':'prepared'}

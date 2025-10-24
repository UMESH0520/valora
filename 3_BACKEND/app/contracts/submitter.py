import os, logging, time
from algosdk.v2client import algod
from algosdk import transaction, account, mnemonic
from algosdk.error import AlgodHTTPError
from typing import Optional, Dict

logger = logging.getLogger('valora.contracts')

ALGOD_ADDRESS = os.getenv('ALGOD_ADDRESS')
ALGOD_TOKEN = os.getenv('ALGOD_API_TOKEN', '')
ORACLE_MNEMONIC = os.getenv('ORACLE_MNEMONIC')
APP_ID = int(os.getenv('APP_ID') or '0')
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def get_algod_client() -> algod.AlgodClient:
    """Get Algorand client with proper error handling"""
    if not ALGOD_ADDRESS:
        raise EnvironmentError('ALGOD_ADDRESS not set in environment')
    return algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)


def get_oracle_account():
    """Get oracle account from mnemonic"""
    if not ORACLE_MNEMONIC:
        raise EnvironmentError('ORACLE_MNEMONIC not set in environment')
    return mnemonic.to_private_key(ORACLE_MNEMONIC), mnemonic.to_public_key(ORACLE_MNEMONIC)


def wait_for_confirmation(client: algod.AlgodClient, txid: str, timeout: int = 10) -> Dict:
    """Wait for transaction confirmation"""
    start_round = client.status()["last-round"] + 1
    current_round = start_round

    while current_round < start_round + timeout:
        try:
            pending_txn = client.pending_transaction_info(txid)
            if pending_txn.get("confirmed-round", 0) > 0:
                return pending_txn
            if pending_txn.get("pool-error"):
                raise Exception(f"Pool error: {pending_txn['pool-error']}")
        except Exception as e:
            logger.error(f"Error checking transaction: {e}")
            return None
        
        client.status_after_block(current_round)
        current_round += 1
    
    raise Exception(f"Transaction not confirmed after {timeout} rounds")


def submit_simple_payment(product_id: str, final_paise: int, retry_count: int = 0) -> Dict:
    """
    Submit price update as a simple payment transaction with note
    This is used when no smart contract is deployed (APP_ID <= 1)
    """
    try:
        # Get client and account
        client = get_algod_client()
        private_key, sender = get_oracle_account()
        
        # Get suggested parameters
        params = client.suggested_params()
        params.flat_fee = True
        params.fee = 1000  # 0.001 ALGO
        
        # Create note with price data (JSON format)
        import json
        price_data = {
            'product_id': product_id,
            'price_paise': final_paise,
            'price_rupees': final_paise / 100,
            'timestamp': int(time.time()),
            'source': 'VALORA'
        }
        note = json.dumps(price_data).encode('utf-8')
        
        # Create payment transaction to self (0 amount, just for storing data)
        txn = transaction.PaymentTxn(
            sender=sender,
            sp=params,
            receiver=sender,  # Send to self
            amt=0,  # No ALGO transfer, just data storage
            note=note
        )
        
        # Sign transaction
        signed_txn = txn.sign(private_key)
        
        # Submit transaction
        tx_id = client.send_transaction(signed_txn)
        logger.info(f"Submitted blockchain note transaction: {tx_id}")
        
        # Wait for confirmation
        confirmed_txn = wait_for_confirmation(client, tx_id)
        
        if confirmed_txn:
            logger.info(f"Blockchain transaction confirmed in round: {confirmed_txn.get('confirmed-round')}")
            return {
                'status': 'confirmed',
                'tx_id': tx_id,
                'confirmed_round': confirmed_txn.get('confirmed-round'),
                'product_id': product_id,
                'price_paise': final_paise,
                'blockchain_note': price_data
            }
        else:
            raise Exception("Transaction confirmation failed")
            
    except AlgodHTTPError as e:
        logger.error(f"Algorand HTTP error: {e}")
        
        # Retry logic
        if retry_count < MAX_RETRIES:
            logger.info(f"Retrying blockchain transaction (attempt {retry_count + 1}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
            return submit_simple_payment(product_id, final_paise, retry_count + 1)
        
        return {
            'status': 'failed',
            'error': str(e),
            'product_id': product_id,
            'price_paise': final_paise
        }
        
    except Exception as e:
        logger.exception(f"Error submitting simple blockchain transaction: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'product_id': product_id,
            'price_paise': final_paise
        }


def submit_update(product_id: str, final_paise: int, retry_count: int = 0) -> Dict:
    """
    Submit price update to Algorand blockchain
    
    Args:
        product_id: Product identifier
        final_paise: Price in paise (1/100 rupee)
        retry_count: Current retry attempt
    
    Returns:
        Dictionary with status and transaction details
    """
    # Check if blockchain is configured
    if not ALGOD_ADDRESS or not ORACLE_MNEMONIC:
        logger.info('Blockchain not configured, skipping: product=%s price=%s', product_id, final_paise)
        return {
            'status': 'skipped',
            'reason': 'Blockchain not configured',
            'product_id': product_id,
            'price_paise': final_paise
        }
    
    # If APP_ID is 0 or 1, use simple payment transaction with note
    if APP_ID <= 1:
        return submit_simple_payment(product_id, final_paise, retry_count)
    
    try:
        # Get client and account
        client = get_algod_client()
        private_key, sender = get_oracle_account()
        
        # Get suggested parameters
        params = client.suggested_params()
        
        # Create application call transaction
        # Note: This is a simplified example. Actual implementation depends on contract structure
        app_args = [
            product_id.encode('utf-8'),
            final_paise.to_bytes(8, 'big')
        ]
        
        txn = transaction.ApplicationCallTxn(
            sender=sender,
            sp=params,
            index=APP_ID,
            on_complete=transaction.OnComplete.NoOpOC,
            app_args=app_args
        )
        
        # Sign transaction
        signed_txn = txn.sign(private_key)
        
        # Submit transaction
        tx_id = client.send_transaction(signed_txn)
        logger.info(f"Submitted transaction: {tx_id}")
        
        # Wait for confirmation
        confirmed_txn = wait_for_confirmation(client, tx_id)
        
        if confirmed_txn:
            logger.info(f"Transaction confirmed in round: {confirmed_txn.get('confirmed-round')}")
            return {
                'status': 'confirmed',
                'tx_id': tx_id,
                'confirmed_round': confirmed_txn.get('confirmed-round'),
                'product_id': product_id,
                'price_paise': final_paise
            }
        else:
            raise Exception("Transaction confirmation failed")
            
    except AlgodHTTPError as e:
        logger.error(f"Algorand HTTP error: {e}")
        
        # Retry logic
        if retry_count < MAX_RETRIES:
            logger.info(f"Retrying transaction (attempt {retry_count + 1}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
            return submit_update(product_id, final_paise, retry_count + 1)
        
        return {
            'status': 'failed',
            'error': str(e),
            'product_id': product_id,
            'price_paise': final_paise
        }
        
    except Exception as e:
        logger.exception(f"Error submitting to blockchain: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'product_id': product_id,
            'price_paise': final_paise
        }

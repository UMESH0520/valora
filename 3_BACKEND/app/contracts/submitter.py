import os, logging, time
from dotenv import load_dotenv
from algosdk.v2client import algod
from algosdk import transaction, account, mnemonic
from algosdk.error import AlgodHTTPError
from typing import Optional, Dict

# Load environment variables
load_dotenv()

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
    private_key = mnemonic.to_private_key(ORACLE_MNEMONIC)
    public_address = account.address_from_private_key(private_key)
    return private_key, public_address


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


def is_blockchain_configured() -> tuple[bool, str]:
    """Check if blockchain is properly configured"""
    if not ALGOD_ADDRESS:
        return False, "ALGOD_ADDRESS not configured"
    if not ORACLE_MNEMONIC:
        return False, "ORACLE_MNEMONIC not configured"
    if APP_ID == 0:
        return False, "APP_ID not configured (set to 0)"
    return True, "Blockchain fully configured"


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
    is_configured, config_message = is_blockchain_configured()
    if not is_configured:
        logger.info('Blockchain not configured (%s), skipping: product=%s price=%s', 
                   config_message, product_id, final_paise)
        return {
            'status': 'skipped',
            'reason': f'Blockchain not configured: {config_message}',
            'product_id': product_id,
            'price_paise': final_paise
        }
    
    # If APP_ID is 1, use simple payment transaction with note
    # If APP_ID > 1, use smart contract call
    if APP_ID == 1:
        logger.info('Using simple payment method for blockchain storage (APP_ID=1)')
        return submit_simple_payment(product_id, final_paise, retry_count)
    elif APP_ID > 1:
        logger.info('Using smart contract method (APP_ID=%s)', APP_ID)
        return submit_smart_contract_call(product_id, final_paise, retry_count)
    else:
        return {
            'status': 'error',
            'reason': f'Invalid APP_ID: {APP_ID}',
            'product_id': product_id,
            'price_paise': final_paise
        }
    

def submit_smart_contract_call(product_id: str, final_paise: int, retry_count: int = 0) -> Dict:
    """
    Submit price update to smart contract on Algorand blockchain
    
    Args:
        product_id: Product identifier
        final_paise: Price in paise (1/100 rupee)
        retry_count: Current retry attempt
    
    Returns:
        Dictionary with status and transaction details
    """
    try:
        # Get client and account
        client = get_algod_client()
        private_key, sender = get_oracle_account()
        
        # Get suggested parameters
        params = client.suggested_params()
        params.flat_fee = True
        params.fee = 1000  # 0.001 ALGO
        
        # Create application call transaction
        # Method: "update_price"
        method_selector = "update_price"  # This should match your smart contract method
        app_args = [
            method_selector.encode('utf-8'),
            product_id.encode('utf-8'),
            final_paise.to_bytes(8, 'big'),
            int(time.time()).to_bytes(8, 'big')  # timestamp
        ]
        
        txn = transaction.ApplicationCallTxn(
            sender=sender,
            sp=params,
            index=APP_ID,
            on_complete=transaction.OnComplete.NoOpOC,
            app_args=app_args,
            note=f"VALORA price update: {product_id} = {final_paise} paise".encode('utf-8')
        )
        
        # Sign transaction
        signed_txn = txn.sign(private_key)
        
        # Submit transaction
        tx_id = client.send_transaction(signed_txn)
        logger.info(f"Submitted smart contract transaction: {tx_id}")
        
        # Wait for confirmation
        confirmed_txn = wait_for_confirmation(client, tx_id)
        
        if confirmed_txn:
            logger.info(f"Smart contract transaction confirmed in round: {confirmed_txn.get('confirmed-round')}")
            return {
                'status': 'confirmed',
                'method': 'smart_contract',
                'tx_id': tx_id,
                'confirmed_round': confirmed_txn.get('confirmed-round'),
                'product_id': product_id,
                'price_paise': final_paise,
                'app_id': APP_ID
            }
        else:
            raise Exception("Smart contract transaction confirmation failed")
            
    except AlgodHTTPError as e:
        logger.error(f"Algorand HTTP error in smart contract call: {e}")
        
        # Retry logic
        if retry_count < MAX_RETRIES:
            logger.info(f"Retrying smart contract transaction (attempt {retry_count + 1}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
            return submit_smart_contract_call(product_id, final_paise, retry_count + 1)
        
        return {
            'status': 'failed',
            'method': 'smart_contract',
            'error': str(e),
            'product_id': product_id,
            'price_paise': final_paise,
            'app_id': APP_ID
        }
        
    except Exception as e:
        logger.exception(f"Error submitting to smart contract: {e}")
        return {
            'status': 'error',
            'method': 'smart_contract',
            'error': str(e),
            'product_id': product_id,
            'price_paise': final_paise,
            'app_id': APP_ID
        }


def get_blockchain_status() -> Dict:
    """Get current blockchain configuration status"""
    is_configured, message = is_blockchain_configured()
    
    status = {
        'configured': is_configured,
        'message': message,
        'algod_address': ALGOD_ADDRESS,
        'app_id': APP_ID,
        'has_mnemonic': bool(ORACLE_MNEMONIC),
        'method': 'simple_payment' if APP_ID == 1 else 'smart_contract' if APP_ID > 1 else 'none'
    }
    
    if is_configured:
        try:
            client = get_algod_client()
            algod_status = client.status()
            status['algod_status'] = {
                'last_round': algod_status.get('last-round'),
                'time_since_last_round': algod_status.get('time-since-last-round'),
                'catchup_time': algod_status.get('catchup-time')
            }
        except Exception as e:
            status['algod_error'] = str(e)
    
    return status

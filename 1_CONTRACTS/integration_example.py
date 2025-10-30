
# VALORA Integration with External Wallet
# This script shows how to integrate with wallet apps

from algosdk.transaction import PaymentTxn
import json

def create_transaction_for_external_signing():
    """Create transaction that can be signed by external wallet"""
    
    # Your wallet address
    address = "MUZM3B356GHKJ3QO4KI272TYCIGE5YWVXGG2Z6355E4K36TVIFOHSEGJBE"
    
    # Transaction parameters (you'd get these from testnet)
    params = {
        "fee": 1000,
        "first": 12345,  # Current round
        "last": 12355,   # Last valid round
        "gh": "testnet-genesis-hash",  # Genesis hash
        "gen": "testnet-v1.0"  # Genesis ID
    }
    
    # Create payment transaction
    txn = PaymentTxn(
        sender=address,
        sp=params,
        receiver=address,
        amt=1000,  # 0.001 ALGO in microALGOS
        note="VALORA testnet transaction".encode()
    )
    
    # Convert to format for external signing
    txn_dict = {
        "from": address,
        "to": address,
        "amount": 1000,
        "fee": 1000,
        "note": "VALORA testnet transaction",
        "type": "pay"
    }
    
    return txn_dict

# Usage:
# 1. Call this function to create transaction
# 2. Export transaction data to wallet app
# 3. Sign with wallet app
# 4. Submit signed transaction

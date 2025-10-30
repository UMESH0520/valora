#!/usr/bin/env python3

import os
from algosdk.v2client import algod
from algosdk import account, mnemonic
from algosdk.transaction import PaymentTxn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test connection to Algorand testnet"""
    try:
        # Initialize client
        algod_address = os.getenv("ALGOD_ADDRESS")
        algod_token = os.getenv("ALGOD_TOKEN")
        
        print(f"Connecting to: {algod_address}")
        
        # Use AlgoExplorer public API (no auth required)
        if "algoexplorerapi.io" in algod_address:
            client = algod.AlgodClient("", algod_address)
        else:
            # PureStake requires API key in headers
            headers = {"X-API-Key": algod_token}
            client = algod.AlgodClient("", algod_address, headers)
        
        # Test connection
        status = client.status()
        print(f"✅ Connected to Algorand testnet!")
        print(f"Network: {status.get('network', 'unknown')}")
        print(f"Last round: {status.get('last-round', 'unknown')}")
        
        return client
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def test_wallet():
    """Test wallet from mnemonic"""
    try:
        # Get mnemonic from environment
        mnemonic_phrase = os.getenv("CREATOR_MNEMONIC")
        
        if not mnemonic_phrase:
            print("❌ No mnemonic found in .env file")
            return None, None
            
        print("Testing wallet from mnemonic...")
        
        # Generate private key from mnemonic
        private_key = mnemonic.to_private_key(mnemonic_phrase)
        
        # Get account address
        address = account.address_from_private_key(private_key)
        
        print(f"✅ Wallet loaded successfully!")
        print(f"Address: {address}")
        
        # Verify this matches the provided address
        expected_address = os.getenv("WALLET_ADDRESS")
        if expected_address and address == expected_address:
            print("✅ Address matches the provided wallet address!")
        elif expected_address:
            print(f"⚠️  Address mismatch!")
            print(f"   From mnemonic: {address}")
            print(f"   Expected: {expected_address}")
        
        return private_key, address
        
    except Exception as e:
        print(f"❌ Wallet test failed: {e}")
        print("Note: You provided 24 words but Algorand typically uses 25 words.")
        print("Please verify your mnemonic phrase is complete.")
        return None, None

def check_balance(client, address):
    """Check account balance"""
    try:
        account_info = client.account_info(address)
        balance = account_info.get('amount', 0)
        
        print(f"💰 Account balance: {balance / 1000000:.6f} ALGO")
        
        if balance == 0:
            print("⚠️  Account has 0 ALGO balance")
            print("💡 Visit https://testnet.algoexplorer.io/dispenser to get testnet ALGO")
            
        return balance
        
    except Exception as e:
        print(f"❌ Failed to check balance: {e}")
        return 0

def create_test_transaction(client, private_key, sender_address):
    """Create a test transaction (to self)"""
    try:
        # Get suggested parameters
        params = client.suggested_params()
        
        # Create a small payment transaction to self (1 microALGO)
        txn = PaymentTxn(
            sender=sender_address,
            sp=params,
            receiver=sender_address,
            amt=1,  # 1 microALGO
            note="VALORA testnet test transaction".encode()
        )
        
        # Sign transaction
        signed_txn = txn.sign(private_key)
        
        print("✅ Test transaction created and signed!")
        print(f"Transaction ID: {signed_txn.transaction.get_txid()}")
        
        return signed_txn
        
    except Exception as e:
        print(f"❌ Failed to create transaction: {e}")
        return None

def submit_transaction(client, signed_txn):
    """Submit transaction to testnet"""
    try:
        # Submit transaction
        tx_id = client.send_transaction(signed_txn)
        print(f"✅ Transaction submitted!")
        print(f"Transaction ID: {tx_id}")
        print(f"View on explorer: https://testnet.algoexplorer.io/tx/{tx_id}")
        
        # Wait for confirmation
        print("Waiting for confirmation...")
        confirmed_txn = client.pending_transaction_info(tx_id)
        
        if confirmed_txn.get("confirmed-round", 0) > 0:
            print(f"✅ Transaction confirmed in round {confirmed_txn['confirmed-round']}")
        else:
            print("⏳ Transaction pending...")
            
        return tx_id
        
    except Exception as e:
        print(f"❌ Failed to submit transaction: {e}")
        return None

def main():
    print("=" * 50)
    print("VALORA - Algorand Testnet Connection Test")
    print("=" * 50)
    
    # Test connection
    client = test_connection()
    if not client:
        return
    
    print("\n" + "-" * 30)
    
    # Test wallet
    private_key, address = test_wallet()
    if not private_key:
        return
    
    print("\n" + "-" * 30)
    
    # Check balance
    balance = check_balance(client, address)
    
    print("\n" + "-" * 30)
    
    # Create and submit test transaction (only if balance > 0)
    if balance > 1000:  # At least 0.001 ALGO for fees
        print("Creating test transaction...")
        signed_txn = create_test_transaction(client, private_key, address)
        
        if signed_txn:
            print("\nSubmitting to testnet...")
            tx_id = submit_transaction(client, signed_txn)
            
            if tx_id:
                print("\n🎉 Test transaction successful!")
            else:
                print("\n❌ Test transaction failed")
    else:
        print("⚠️  Insufficient balance for test transaction")
        print("💡 Get testnet ALGO from: https://testnet.algoexplorer.io/dispenser")
    
    print("\n" + "=" * 50)
    print("Test complete!")

if __name__ == "__main__":
    main()
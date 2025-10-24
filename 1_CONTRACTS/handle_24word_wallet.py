#!/usr/bin/env python3

import os
import hashlib
import hmac
from algosdk import account
from algosdk.v2client import algod
from algosdk.transaction import PaymentTxn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def words_to_entropy(words):
    """Convert 24 words to entropy (simplified approach)"""
    # This is a basic implementation - not the official BIP39 standard
    word_string = ' '.join(words)
    entropy = hashlib.sha256(word_string.encode()).digest()
    return entropy

def entropy_to_private_key(entropy):
    """Convert entropy to Algorand private key"""
    # Use HMAC-SHA512 to derive key material
    key_material = hmac.new(b"algorand", entropy, hashlib.sha512).digest()
    # Take first 32 bytes as private key
    private_key = key_material[:32]
    return private_key

def create_algorand_address_from_24_words():
    """Create Algorand address from 24-word mnemonic using alternative method"""
    
    print("=" * 60)
    print("VALORA - Alternative 24-Word Wallet Handler")
    print("=" * 60)
    
    mnemonic_phrase = os.getenv("CREATOR_MNEMONIC")
    expected_address = os.getenv("WALLET_ADDRESS")
    
    if not mnemonic_phrase:
        print("❌ No mnemonic found in .env file")
        return None, None
    
    words = mnemonic_phrase.split()
    print(f"Mnemonic: {mnemonic_phrase}")
    print(f"Word count: {len(words)}")
    print(f"Expected address: {expected_address}")
    print()
    
    if len(words) != 24:
        print("❌ This method requires exactly 24 words")
        return None, None
    
    try:
        # Method 1: Direct entropy conversion
        print("🔧 Method 1: Converting 24 words to entropy...")
        entropy = words_to_entropy(words)
        private_key = entropy_to_private_key(entropy)
        
        # Generate address from private key
        address = account.address_from_private_key(private_key)
        
        print(f"Generated address: {address}")
        
        if address == expected_address:
            print("🎯 ✅ PERFECT MATCH! This method works!")
            return private_key, address
        else:
            print("❌ Address doesn't match expected address")
        
        # Method 2: Try different derivation
        print(f"\n🔧 Method 2: Alternative derivation...")
        alt_entropy = hashlib.sha512(mnemonic_phrase.encode()).digest()[:32]
        alt_private_key = entropy_to_private_key(alt_entropy)
        alt_address = account.address_from_private_key(alt_private_key)
        
        print(f"Alternative address: {alt_address}")
        
        if alt_address == expected_address:
            print("🎯 ✅ ALTERNATIVE METHOD WORKS!")
            return alt_private_key, alt_address
        
        # Method 3: Simple hash approach
        print(f"\n🔧 Method 3: Simple hash approach...")
        simple_key = hashlib.sha256(mnemonic_phrase.encode()).digest()
        simple_address = account.address_from_private_key(simple_key)
        
        print(f"Simple hash address: {simple_address}")
        
        if simple_address == expected_address:
            print("🎯 ✅ SIMPLE METHOD WORKS!")
            return simple_key, simple_address
            
        print(f"\n❌ None of the methods matched your expected address")
        print(f"This suggests your wallet uses a different derivation standard.")
        
        return None, None
        
    except Exception as e:
        print(f"❌ Error in address generation: {e}")
        return None, None

def create_wallet_from_address():
    """Create a test wallet using your known address"""
    print(f"\n🔧 Alternative: Working with your known address...")
    
    expected_address = os.getenv("WALLET_ADDRESS")
    if not expected_address:
        print("❌ No wallet address provided")
        return None
    
    print(f"Your wallet address: {expected_address}")
    print("✅ We can work with this address for read-only operations")
    print("💡 For transactions, you'll need to sign externally or use your wallet app")
    
    return expected_address

def test_read_only_operations():
    """Test read-only operations with the wallet address"""
    
    print(f"\n" + "-" * 40)
    print("Testing Read-Only Operations")
    print("-" * 40)
    
    address = os.getenv("WALLET_ADDRESS")
    if not address:
        print("❌ No wallet address available")
        return
    
    # Try to connect to Algorand testnet (read-only)
    algod_address = os.getenv("ALGOD_ADDRESS", "https://node.testnet.algoexplorerapi.io")
    algod_token = os.getenv("ALGOD_TOKEN", "")
    
    try:
        if "algoexplorerapi.io" in algod_address:
            client = algod.AlgodClient("", algod_address)
        else:
            headers = {"X-API-Key": algod_token}
            client = algod.AlgodClient("", algod_address, headers)
        
        # Test connection
        print("🔗 Testing network connection...")
        status = client.status()
        print(f"✅ Connected to Algorand testnet!")
        print(f"Last round: {status.get('last-round', 'unknown')}")
        
        # Check account info (read-only)
        print(f"\n💰 Checking account balance...")
        try:
            account_info = client.account_info(address)
            balance = account_info.get('amount', 0)
            print(f"✅ Account balance: {balance / 1000000:.6f} ALGO")
            
            if balance == 0:
                print("💡 Fund your testnet wallet: https://testnet.algoexplorer.io/dispenser")
            else:
                print("✅ Account has funds - ready for transactions!")
                
        except Exception as e:
            print(f"❌ Could not check balance: {e}")
            print("💡 This might be a new account. Fund it at: https://testnet.algoexplorer.io/dispenser")
        
    except Exception as e:
        print(f"❌ Network connection failed: {e}")
        print("💡 Network issues - try again later")

def create_unsigned_transaction():
    """Create an unsigned transaction that can be signed externally"""
    
    print(f"\n" + "-" * 40)
    print("Creating Unsigned Transaction")
    print("-" * 40)
    
    address = os.getenv("WALLET_ADDRESS")
    if not address:
        print("❌ No wallet address available")
        return
    
    algod_address = os.getenv("ALGOD_ADDRESS", "https://node.testnet.algoexplorerapi.io")
    algod_token = os.getenv("ALGOD_TOKEN", "")
    
    try:
        # Initialize client
        if "algoexplorerapi.io" in algod_address:
            client = algod.AlgodClient("", algod_address)
        else:
            headers = {"X-API-Key": algod_token}
            client = algod.AlgodClient("", algod_address, headers)
        
        # Get network parameters
        params = client.suggested_params()
        
        # Create a simple payment transaction (to self)
        txn = PaymentTxn(
            sender=address,
            sp=params,
            receiver=address,
            amt=1,  # 1 microALGO
            note="VALORA testnet transaction".encode()
        )
        
        print(f"✅ Created unsigned transaction:")
        print(f"   From: {address}")
        print(f"   To: {address}")
        print(f"   Amount: 0.000001 ALGO")
        print(f"   Note: VALORA testnet transaction")
        print(f"   Transaction ID: {txn.get_txid()}")
        
        # Save transaction to file for external signing
        import base64
        import json
        
        txn_dict = {
            "txn": base64.b64encode(txn.dictify()).decode(),
            "sender": address,
            "amount": 1,
            "note": "VALORA testnet transaction",
            "txid": txn.get_txid()
        }
        
        with open("unsigned_transaction.json", "w") as f:
            json.dump(txn_dict, f, indent=2)
        
        print(f"💾 Saved unsigned transaction to: unsigned_transaction.json")
        print(f"💡 You can sign this with your wallet app and submit it manually")
        
        return txn
        
    except Exception as e:
        print(f"❌ Failed to create transaction: {e}")
        return None

def main():
    """Main function to handle 24-word wallet"""
    
    # Try to create wallet from 24 words
    private_key, address = create_algorand_address_from_24_words()
    
    if private_key and address:
        print(f"\n🎉 Success! Your 24-word mnemonic works!")
        print(f"✅ Ready for full transaction capabilities")
        
        # Update .env with working configuration
        print(f"💾 Configuration ready for transactions")
    else:
        # Fallback to address-only operations
        print(f"\n🔄 Falling back to address-only operations...")
        address = create_wallet_from_address()
    
    if address:
        # Test read-only operations
        test_read_only_operations()
        
        # Create unsigned transaction
        create_unsigned_transaction()
        
        print(f"\n" + "=" * 60)
        print("Summary & Next Steps")
        print("=" * 60)
        
        if private_key:
            print("✅ Private key derived successfully")
            print("✅ Can perform all transaction operations")
            print("📋 Next steps:")
            print("1. Fund wallet: https://testnet.algoexplorer.io/dispenser")
            print("2. Test transactions with full capabilities")
        else:
            print("⚠️  Private key not available (address-only mode)")
            print("📋 Next steps:")
            print("1. Fund wallet: https://testnet.algoexplorer.io/dispenser")
            print("2. Use unsigned_transaction.json with your wallet app")
            print("3. Or import your 24-word phrase into a compatible wallet")
    
    print(f"\n💡 Your wallet address: {os.getenv('WALLET_ADDRESS')}")
    print(f"🌐 Network: Algorand Testnet")

if __name__ == "__main__":
    main()
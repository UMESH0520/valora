#!/usr/bin/env python3

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_wallet_guide():
    """Create a comprehensive guide for working with 24-word Algorand wallets"""
    
    print("=" * 70)
    print("VALORA - 24-Word Algorand Wallet Guide & Transaction Setup")
    print("=" * 70)
    
    mnemonic_phrase = os.getenv("CREATOR_MNEMONIC")
    wallet_address = os.getenv("WALLET_ADDRESS")
    
    print(f"📋 Your Configuration:")
    print(f"   Wallet Address: {wallet_address}")
    print(f"   Mnemonic Words: {len(mnemonic_phrase.split()) if mnemonic_phrase else 0}")
    print(f"   Network: Algorand Testnet")
    print()
    
    print("🔍 Analysis:")
    if mnemonic_phrase and len(mnemonic_phrase.split()) == 24:
        print("   ✅ 24-word mnemonic detected")
        print("   ⚠️  Standard Algorand SDK expects 25 words")
        print("   💡 Your wallet likely uses BIP39 or custom derivation")
    
    print("\n" + "=" * 70)
    print("SOLUTION OPTIONS")
    print("=" * 70)
    
    print("\n🎯 Option 1: Use Compatible Wallet Apps")
    print("-" * 40)
    print("Compatible wallets that support 24-word phrases:")
    print("• MyAlgo Wallet (web): https://wallet.myalgo.com")
    print("• AlgoSigner (browser extension)")
    print("• Pera Wallet (mobile/desktop)")
    print("• Exodus Wallet")
    print()
    print("Steps:")
    print("1. Install one of these wallets")
    print("2. Import your 24-word phrase")
    print("3. Verify the generated address matches:")
    print(f"   {wallet_address}")
    print("4. Fund the wallet via: https://testnet.algoexplorer.io/dispenser")
    print("5. Use wallet to sign transactions")
    
    print("\n🎯 Option 2: Manual Transaction Creation")
    print("-" * 40)
    create_manual_transaction_guide(wallet_address)
    
    print("\n🎯 Option 3: Alternative SDKs")
    print("-" * 40)
    print("Try different language SDKs that might handle 24-word phrases:")
    print("• JavaScript: @algorand/sdk-js")
    print("• Go: algorand/go-algorand-sdk")
    print("• Java: algorand/java-algorand-sdk")
    print()
    
    print("\n🎯 Option 4: Use Algorand CLI")
    print("-" * 40)
    print("Install Algorand CLI tools:")
    print("1. Download from: https://developer.algorand.org/docs/clis/")
    print("2. Import wallet: goal wallet import")
    print("3. Create transactions: goal clerk send")
    
    print("\n" + "=" * 70)
    print("RECOMMENDED IMMEDIATE STEPS")
    print("=" * 70)
    
    print("\n1. 💰 Fund Your Wallet")
    print(f"   • Visit: https://testnet.algoexplorer.io/dispenser")
    print(f"   • Enter address: {wallet_address}")
    print(f"   • Get 10 testnet ALGO")
    
    print("\n2. 🔧 Verify Your Wallet")
    print("   • Try MyAlgo Wallet: https://wallet.myalgo.com")
    print("   • Import your 24-word phrase")
    print("   • Check if address matches")
    
    print("\n3. 🚀 Test Transaction")
    print("   • Use wallet app to send 0.001 ALGO to yourself")
    print("   • Verify on explorer: https://testnet.algoexplorer.io")
    
    print(f"\n4. 🔗 Integration with VALORA")
    print("   • Once wallet works, integrate with your project")
    print("   • Use wallet connect or direct signing")

def create_manual_transaction_guide(address):
    """Create guide for manual transaction creation"""
    
    print("Manual transaction steps:")
    print("1. Get network parameters from testnet API")
    print("2. Create transaction object")
    print("3. Sign with external tool/wallet")
    print("4. Submit to network")
    print()
    print(f"Example transaction (self-payment):")
    print(f"   From: {address}")
    print(f"   To: {address}")
    print(f"   Amount: 0.001 ALGO")
    print(f"   Fee: 0.001 ALGO")
    print(f"   Note: 'VALORA testnet transaction'")

def create_integration_script():
    """Create script for integrating with external wallet"""
    
    integration_script = '''
# VALORA Integration with External Wallet
# This script shows how to integrate with wallet apps

from algosdk.transaction import PaymentTxn
import json

def create_transaction_for_external_signing():
    """Create transaction that can be signed by external wallet"""
    
    # Your wallet address
    address = "''' + os.getenv("WALLET_ADDRESS", "") + '''"
    
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
'''
    
    with open("integration_example.py", "w") as f:
        f.write(integration_script)
    
    print(f"💾 Created integration example: integration_example.py")

def main():
    """Main function"""
    
    # Create comprehensive guide
    create_wallet_guide()
    
    # Create integration script
    print(f"\n" + "-" * 50)
    create_integration_script()
    
    print(f"\n" + "=" * 70)
    print("FILES CREATED")
    print("=" * 70)
    print("✅ integration_example.py - Integration script template")
    print("✅ This guide in terminal output")
    
    print(f"\n" + "=" * 70)
    print("QUICK START RECOMMENDATION")
    print("=" * 70)
    print("1. Go to: https://wallet.myalgo.com")
    print("2. Click 'Import Account' → 'Mnemonic'")
    print("3. Enter your 24-word phrase")
    print("4. Check if generated address matches yours")
    print("5. Fund wallet at: https://testnet.algoexplorer.io/dispenser")
    print("6. Test by sending small transaction to yourself")
    
    print(f"\n💡 Your address: {os.getenv('WALLET_ADDRESS')}")
    print(f"🌐 Network: Algorand Testnet")
    print(f"💰 Faucet: https://testnet.algoexplorer.io/dispenser")

if __name__ == "__main__":
    main()
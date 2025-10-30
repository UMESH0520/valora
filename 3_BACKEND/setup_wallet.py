#!/usr/bin/env python3
"""
Setup VALORA with provided wallet address
"""
import os
from algosdk.v2client import algod
from algosdk import account, mnemonic

def check_wallet_balance(address):
    """Check testnet balance for the provided address"""
    print(f"🔍 Checking testnet balance for: {address}")
    
    try:
        # Connect to Algorand testnet
        client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
        
        # Get account info
        account_info = client.account_info(address)
        balance_microalgos = account_info.get('amount', 0)
        balance_algos = balance_microalgos / 1_000_000
        
        print(f"💰 Testnet Balance: {balance_algos} ALGO")
        print(f"📊 Account Status: {'Active' if balance_algos > 0 else 'Needs funding'}")
        
        if balance_algos < 0.1:
            print("⚠️  Low balance detected!")
            print("💡 Get testnet ALGO from: https://testnet.algoexplorer.io/dispenser")
            print(f"📋 Your address: {address}")
            return False
        else:
            print("✅ Sufficient balance for transactions")
            return True
            
    except Exception as e:
        print(f"❌ Error checking balance: {e}")
        print("ℹ️  This might mean the account doesn't exist on testnet yet")
        print("💡 Fund it first at: https://testnet.algoexplorer.io/dispenser")
        return False

def setup_with_mnemonic():
    """Setup blockchain integration with user's mnemonic"""
    wallet_address = "MUZM3B356GHKJ3QO4KI272TYCIGE5YWVXGG2Z6355E4K36TVIFOHSEGJBE"
    
    print("🔗 VALORA Blockchain Setup")
    print("="*50)
    print(f"Wallet Address: {wallet_address}")
    print()
    
    # Check current balance
    has_funds = check_wallet_balance(wallet_address)
    
    if not has_funds:
        print("\n⏳ Please fund your testnet account first, then return here")
        return False
    
    # Get mnemonic from user
    print("\n🔐 To enable blockchain transactions, I need your wallet's mnemonic phrase:")
    print("⚠️  Your mnemonic will only be stored locally in the .env file")
    
    mnemonic_phrase = input("\nEnter your 25-word mnemonic phrase: ").strip()
    
    if not mnemonic_phrase:
        print("❌ No mnemonic provided")
        return False
    
    try:
        # Validate mnemonic matches the address
        private_key = mnemonic.to_private_key(mnemonic_phrase)
        derived_address = account.address_from_private_key(private_key)
        
        if derived_address != wallet_address:
            print(f"❌ Mnemonic doesn't match the provided address!")
            print(f"Expected: {wallet_address}")
            print(f"Got:      {derived_address}")
            return False
        
        print("✅ Mnemonic validated successfully!")
        
        # Update .env file
        update_env_file(mnemonic_phrase)
        
        print("\n🎉 Setup Complete!")
        print("✅ Blockchain integration is now active")
        print("📋 All price updates will be stored on Algorand testnet")
        print("🔍 You can view transactions at: https://testnet.algoexplorer.io/address/" + wallet_address)
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating mnemonic: {e}")
        return False

def update_env_file(mnemonic_phrase):
    """Update .env file with the mnemonic"""
    env_file = ".env"
    
    print(f"📝 Updating {env_file}...")
    
    # Read existing content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Update the relevant lines
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if line.startswith('ORACLE_MNEMONIC='):
            new_lines.append(f'ORACLE_MNEMONIC={mnemonic_phrase}')
        elif line.startswith('APP_ID='):
            new_lines.append('APP_ID=1')  # Simple payment mode
        else:
            new_lines.append(line)
    
    # Write back
    with open(env_file, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Environment configuration updated!")

if __name__ == "__main__":
    setup_with_mnemonic()
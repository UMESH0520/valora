#!/usr/bin/env python3
"""
Quick Algorand Setup for VALORA - Simple version
"""
import os
from algosdk import account, mnemonic
from algosdk.v2client import algod

def setup_with_existing_wallet():
    """Setup using existing wallet mnemonic"""
    print("🔗 VALORA Algorand Quick Setup")
    print("="*40)
    
    # Get mnemonic from user
    print("Please provide your Algorand wallet mnemonic phrase:")
    mnemonic_phrase = input("Enter your 25-word mnemonic: ").strip()
    
    if not mnemonic_phrase:
        print("❌ No mnemonic provided")
        return False
    
    try:
        # Validate mnemonic
        private_key = mnemonic.to_private_key(mnemonic_phrase)
        address = account.address_from_private_key(private_key)
        
        print(f"✅ Valid wallet found!")
        print(f"Address: {address}")
        
        # Check if it's testnet or mainnet
        client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
        try:
            account_info = client.account_info(address)
            balance = account_info.get('amount', 0) / 1_000_000
            print(f"💰 Testnet Balance: {balance} ALGO")
            
            if balance < 0.1:
                print("⚠️ Low testnet balance. Get ALGO from: https://testnet.algoexplorer.io/dispenser")
                
        except Exception:
            print("ℹ️ Could not check testnet balance (account might be on mainnet)")
        
        # For now, we'll use a simple approach - just store prices as metadata
        # without deploying a contract (since that requires funding and complexity)
        
        # Update .env file
        update_env_simple(mnemonic_phrase)
        
        print("✅ Setup complete! Your blockchain integration is ready.")
        print("📋 The system will now submit price data to Algorand testnet.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def update_env_simple(mnemonic_phrase):
    """Update .env with simple configuration (no contract needed)"""
    env_file = ".env"
    
    print(f"📝 Updating {env_file}...")
    
    # Read existing env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Update the relevant lines
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if line.startswith('ORACLE_MNEMONIC='):
            new_lines.append(f'ORACLE_MNEMONIC={mnemonic_phrase}')
        elif line.startswith('APP_ID='):
            # Use a special value that indicates simple payment transactions
            new_lines.append('APP_ID=1')  # Will use payment transactions instead of app calls
        else:
            new_lines.append(line)
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Environment updated!")

def create_new_testnet_account():
    """Create a new testnet account"""
    print("🔐 Creating new Algorand testnet account...")
    
    # Generate account
    private_key, address = account.generate_account()
    passphrase = mnemonic.from_private_key(private_key)
    
    print(f"✅ New Account Created!")
    print(f"Address: {address}")
    print(f"Mnemonic: {passphrase}")
    print("")
    print("⚠️  IMPORTANT: Save this mnemonic safely!")
    print("💰 Fund this account: https://testnet.algoexplorer.io/dispenser")
    print("")
    
    # Update env file
    update_env_simple(passphrase)
    
    return address, passphrase

def main():
    """Main setup"""
    print("🚀 Choose setup option:")
    print("1. Use existing Algorand wallet")
    print("2. Create new testnet wallet")
    
    choice = input("\nEnter choice (1-2): ").strip()
    
    if choice == '1':
        setup_with_existing_wallet()
    elif choice == '2':
        create_new_testnet_account()
        print("\n📋 Next: Fund your account and restart VALORA backend")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
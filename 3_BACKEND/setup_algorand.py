#!/usr/bin/env python3
"""
Algorand Blockchain Setup Utilities for VALORA
"""
import os
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk import transaction
from algosdk.error import AlgodHTTPError
import json

# Algorand testnet configuration
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""

def create_algod_client():
    """Create Algorand client"""
    return algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

def create_new_account():
    """Create a new Algorand account for testnet"""
    print("🔐 Creating new Algorand testnet account...")
    
    # Generate account
    private_key, address = account.generate_account()
    passphrase = mnemonic.from_private_key(private_key)
    
    print(f"✅ New Account Created!")
    print(f"Address: {address}")
    print(f"Mnemonic: {passphrase}")
    print(f"")
    print("⚠️  IMPORTANT: Save this mnemonic safely! You'll need it to recover your account.")
    print("💰 Fund this account with testnet ALGO from: https://testnet.algoexplorer.io/dispenser")
    print("")
    
    return address, passphrase

def check_account_balance(address):
    """Check account balance"""
    try:
        client = create_algod_client()
        account_info = client.account_info(address)
        balance_microalgos = account_info.get('amount', 0)
        balance_algos = balance_microalgos / 1_000_000
        
        print(f"💰 Account Balance: {balance_algos} ALGO")
        
        if balance_algos < 0.1:
            print("⚠️  Low balance! Fund your account at: https://testnet.algoexplorer.io/dispenser")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking balance: {e}")
        return False

def deploy_price_oracle_app(creator_mnemonic):
    """Deploy a simple price oracle smart contract"""
    print("📋 Deploying Price Oracle Smart Contract...")
    
    try:
        client = create_algod_client()
        
        # Get creator account
        creator_private_key = mnemonic.to_private_key(creator_mnemonic)
        creator_address = account.address_from_private_key(creator_private_key)
        
        print(f"Creator: {creator_address}")
        
        # Check balance first
        if not check_account_balance(creator_address):
            return None
        
        # Simple approval program (TEAL)
        approval_program = b\"\"\"
#pragma version 6
// Simple Price Oracle Contract
// Stores product prices on-chain

// Check if this is an application call
txn TypeEnum
int appl
==
assert

// Allow creator to update prices
txn Sender
global CreatorAddress
==
assert

// Store price data
txn ApplicationArgs 0  // product_id
txn ApplicationArgs 1  // price_paise
app_global_put

// Success
int 1
return
\"\"\"
        
        # Clear program (TEAL) - allows anyone to clear
        clear_program = b\"\"\"
#pragma version 6
int 1
return
\"\"\"
        
        # Compile programs
        approval_result = client.compile(approval_program.decode())
        approval_bytes = approval_result['result']
        
        clear_result = client.compile(clear_program.decode())
        clear_bytes = clear_result['result']
        
        # Get suggested parameters
        params = client.suggested_params()
        
        # Create application creation transaction
        txn = transaction.ApplicationCreateTxn(
            sender=creator_address,
            sp=params,
            on_complete=transaction.OnComplete.NoOpOC,
            approval_program=approval_bytes,
            clear_program=clear_bytes,
            global_schema=transaction.StateSchema(num_uints=0, num_byte_slices=64),  # For product storage
            local_schema=transaction.StateSchema(num_uints=0, num_byte_slices=0)
        )
        
        # Sign transaction
        signed_txn = txn.sign(creator_private_key)
        
        # Submit transaction
        tx_id = client.send_transaction(signed_txn)
        print(f"📝 Transaction ID: {tx_id}")
        
        # Wait for confirmation
        confirmed_txn = wait_for_confirmation(client, tx_id)
        
        if confirmed_txn:
            app_id = confirmed_txn.get('application-index')
            print(f"✅ Smart Contract Deployed!")
            print(f"Application ID: {app_id}")
            return app_id
        else:
            print("❌ Contract deployment failed")
            return None
            
    except Exception as e:
        print(f"❌ Error deploying contract: {e}")
        return None

def wait_for_confirmation(client, txid, timeout=10):
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
            print(f"Error checking transaction: {e}")
            return None
        
        client.status_after_block(current_round)
        current_round += 1
    
    raise Exception(f"Transaction not confirmed after {timeout} rounds")

def update_env_file(mnemonic_phrase, app_id):
    """Update .env file with blockchain configuration"""
    env_file = ".env"
    
    print(f"📝 Updating {env_file}...")
    
    # Read existing env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update relevant lines
    new_lines = []
    for line in lines:
        if line.startswith('ORACLE_MNEMONIC='):
            new_lines.append(f'ORACLE_MNEMONIC={mnemonic_phrase}\\n')
        elif line.startswith('APP_ID='):
            new_lines.append(f'APP_ID={app_id}\\n')
        else:
            new_lines.append(line)
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.writelines(new_lines)
    
    print("✅ Environment file updated!")

def test_blockchain_integration():
    """Test the blockchain integration"""
    print("🧪 Testing blockchain integration...")
    
    try:
        # Import and test the submitter
        from app.contracts.submitter import submit_update
        
        # Test with sample data
        result = submit_update("TEST-PRODUCT-001", 125000)  # ₹1250.00
        
        print("📋 Test Result:")
        print(json.dumps(result, indent=2))
        
        if result.get('status') == 'confirmed':
            print("✅ Blockchain integration working!")
            return True
        else:
            print("⚠️ Integration test result:", result.get('status', 'unknown'))
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main setup wizard"""
    print("🚀 VALORA Algorand Blockchain Setup")
    print("="*50)
    
    print("\\nChoose an option:")
    print("1. Create new testnet account")
    print("2. Use existing account (provide mnemonic)")
    print("3. Check account balance")
    print("4. Deploy smart contract")
    print("5. Test integration")
    print("6. Complete setup (all steps)")
    
    choice = input("\\nEnter choice (1-6): ").strip()
    
    if choice == '1':
        address, passphrase = create_new_account()
        print(f"\\n📋 Next steps:")
        print(f"1. Fund account: https://testnet.algoexplorer.io/dispenser")
        print(f"2. Run option 4 to deploy smart contract")
        
    elif choice == '2':
        mnemonic_phrase = input("Enter your 25-word mnemonic phrase: ").strip()
        try:
            private_key = mnemonic.to_private_key(mnemonic_phrase)
            address = account.address_from_private_key(private_key)
            print(f"✅ Valid mnemonic for address: {address}")
            check_account_balance(address)
        except Exception as e:
            print(f"❌ Invalid mnemonic: {e}")
    
    elif choice == '3':
        address = input("Enter Algorand address: ").strip()
        check_account_balance(address)
    
    elif choice == '4':
        mnemonic_phrase = input("Enter creator mnemonic: ").strip()
        app_id = deploy_price_oracle_app(mnemonic_phrase)
        if app_id:
            update_env_file(mnemonic_phrase, app_id)
    
    elif choice == '5':
        test_blockchain_integration()
    
    elif choice == '6':
        print("🔄 Running complete setup...")
        
        # Step 1: Create account
        address, passphrase = create_new_account()
        
        # Step 2: Wait for funding
        input("\\n⏳ Please fund your account and press Enter to continue...")
        
        # Step 3: Check balance
        if not check_account_balance(address):
            print("❌ Account not funded properly. Exiting.")
            return
        
        # Step 4: Deploy contract
        app_id = deploy_price_oracle_app(passphrase)
        if not app_id:
            print("❌ Contract deployment failed. Exiting.")
            return
        
        # Step 5: Update environment
        update_env_file(passphrase, app_id)
        
        # Step 6: Test integration
        test_blockchain_integration()
        
        print("\\n🎉 Complete setup finished!")
        print("✅ Your VALORA blockchain integration is ready!")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
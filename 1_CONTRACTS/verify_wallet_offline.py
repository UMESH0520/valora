#!/usr/bin/env python3

import os
from algosdk import account, mnemonic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_wallet_offline():
    """Verify wallet address generation from mnemonic (offline)"""
    
    print("=" * 50)
    print("VALORA - Offline Wallet Verification")
    print("=" * 50)
    
    try:
        # Get mnemonic from environment
        mnemonic_phrase = os.getenv("CREATOR_MNEMONIC")
        expected_address = os.getenv("WALLET_ADDRESS")
        
        if not mnemonic_phrase:
            print("❌ No mnemonic found in .env file")
            return
            
        print("Testing wallet from mnemonic...")
        print(f"Mnemonic: {mnemonic_phrase}")
        print(f"Expected address: {expected_address}")
        print()
        
        # Count words
        words = mnemonic_phrase.split()
        print(f"Word count: {len(words)}")
        
        if len(words) != 25:
            print(f"⚠️  Warning: Algorand mnemonics should have 25 words, but {len(words)} words provided")
            if len(words) == 24:
                print("💡 Tip: Try adding a checksum word. Common checksum words: abandon, ability, able, about, above, absent, absorb, abstract, absurd, abuse, access, accident")
        
        # Try to generate private key from mnemonic
        try:
            private_key = mnemonic.to_private_key(mnemonic_phrase)
            print("✅ Successfully generated private key from mnemonic")
        except Exception as e:
            print(f"❌ Failed to generate private key: {e}")
            
            # If 24 words, suggest trying with common checksum words
            if len(words) == 24:
                print("\\n🔧 Trying with common checksum words...")
                checksum_words = ["abandon", "ability", "able", "about", "above"]
                
                for word in checksum_words:
                    try:
                        test_mnemonic = mnemonic_phrase + " " + word
                        test_private_key = mnemonic.to_private_key(test_mnemonic)
                        test_address = account.address_from_private_key(test_private_key)
                        
                        print(f"  ✅ Works with '{word}': {test_address}")
                        
                        if test_address == expected_address:
                            print(f"  🎯 MATCH! Your complete mnemonic is: {test_mnemonic}")
                            break
                            
                    except Exception:
                        print(f"  ❌ Failed with '{word}'")
                        continue
            return
        
        # Get account address
        address = account.address_from_private_key(private_key)
        
        print(f"✅ Wallet loaded successfully!")
        print(f"Generated address: {address}")
        print()
        
        # Verify this matches the provided address
        if expected_address:
            if address == expected_address:
                print("🎯 ✅ Perfect! Address matches the provided wallet address!")
                print("✅ Your mnemonic is valid and generates the correct address")
            else:
                print(f"❌ Address mismatch!")
                print(f"   From mnemonic: {address}")
                print(f"   Expected: {expected_address}")
                print()
                print("💡 This could mean:")
                print("   - The mnemonic is incomplete or incorrect")
                print("   - The expected address is wrong")
                print("   - Word order is different")
        else:
            print("⚠️  No expected address provided for comparison")
            
        print()
        print("📋 Summary:")
        print(f"   Mnemonic words: {len(words)}")
        print(f"   Generated address: {address}")
        print(f"   Expected address: {expected_address or 'Not provided'}")
        print(f"   Match: {'✅ Yes' if address == expected_address else '❌ No'}")
        
    except Exception as e:
        print(f"❌ Wallet verification failed: {e}")

def show_network_info():
    """Show network configuration"""
    print("\\n" + "-" * 30)
    print("Network Configuration:")
    print("-" * 30)
    
    algod_address = os.getenv("ALGOD_ADDRESS")
    algod_token = os.getenv("ALGOD_TOKEN")
    
    print(f"Algod Address: {algod_address}")
    print(f"Algod Token: {'Set' if algod_token else 'Not set'}")
    
    if "testnet" in algod_address.lower():
        print("✅ Configured for TESTNET")
        print("💡 Get testnet ALGO: https://testnet.algoexplorer.io/dispenser")
    elif "mainnet" in algod_address.lower():
        print("⚠️  Configured for MAINNET")
    else:
        print("❓ Unknown network")

if __name__ == "__main__":
    verify_wallet_offline()
    show_network_info()
    
    print("\\n" + "=" * 50)
    print("Verification complete!")
    print()
    print("Next steps:")
    print("1. If address matches: You can proceed with transactions")
    print("2. If no match: Check your mnemonic phrase")
    print("3. Fund your testnet wallet: https://testnet.algoexplorer.io/dispenser")
    print("4. Try online connection when network is available")
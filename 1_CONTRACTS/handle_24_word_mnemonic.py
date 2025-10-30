#!/usr/bin/env python3

import os
import hashlib
from algosdk import account, mnemonic
from algosdk.wordlists import word_list_english
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def calculate_checksum_word(words_24):
    """Calculate the 25th checksum word for a 24-word mnemonic"""
    try:
        # Convert words to indices
        word_indices = []
        for word in words_24:
            if word in word_list_english():
                word_indices.append(word_list_english().index(word))
            else:
                raise ValueError(f"Invalid word: {word}")
        
        # Calculate checksum (simplified approach)
        # This is a basic implementation - the actual Algorand checksum is more complex
        checksum_index = sum(word_indices) % len(word_list_english())
        checksum_word = word_list_english()[checksum_index]
        
        return checksum_word
    except Exception as e:
        print(f"Error calculating checksum: {e}")
        return None

def try_24_word_variations():
    """Try various methods to work with 24-word mnemonic"""
    
    print("=" * 60)
    print("VALORA - 24-Word Mnemonic Handler")
    print("=" * 60)
    
    mnemonic_phrase = os.getenv("CREATOR_MNEMONIC")
    expected_address = os.getenv("WALLET_ADDRESS")
    
    if not mnemonic_phrase:
        print("❌ No mnemonic found in .env file")
        return
    
    words = mnemonic_phrase.split()
    print(f"Original mnemonic: {mnemonic_phrase}")
    print(f"Word count: {len(words)}")
    print(f"Expected address: {expected_address}")
    print()
    
    if len(words) != 24:
        print("❌ This script is designed for 24-word mnemonics")
        return
    
    # Method 1: Try common 25th words
    print("🔍 Method 1: Trying common 25th words...")
    common_words = [
        "abandon", "ability", "able", "about", "above", "absent", "absorb", 
        "abstract", "absurd", "abuse", "access", "accident", "account", 
        "accuse", "achieve", "acid", "acoustic", "acquire", "across", "act"
    ]
    
    found_match = False
    for word in common_words:
        try:
            test_mnemonic = mnemonic_phrase + " " + word
            private_key = mnemonic.to_private_key(test_mnemonic)
            address = account.address_from_private_key(private_key)
            
            if address == expected_address:
                print(f"🎯 ✅ FOUND MATCH with '{word}'!")
                print(f"Complete mnemonic: {test_mnemonic}")
                print(f"Address: {address}")
                found_match = True
                
                # Update .env file
                update_env_with_complete_mnemonic(test_mnemonic)
                break
            else:
                print(f"  ❌ '{word}' -> {address[:10]}... (no match)")
                
        except Exception:
            print(f"  ❌ '{word}' -> Invalid mnemonic")
    
    if found_match:
        return
    
    # Method 2: Try calculated checksum
    print(f"\n🔍 Method 2: Calculating potential checksum word...")
    checksum_word = calculate_checksum_word(words)
    if checksum_word:
        try:
            test_mnemonic = mnemonic_phrase + " " + checksum_word
            private_key = mnemonic.to_private_key(test_mnemonic)
            address = account.address_from_private_key(private_key)
            
            print(f"Calculated checksum word: {checksum_word}")
            print(f"Generated address: {address}")
            
            if address == expected_address:
                print("🎯 ✅ Checksum calculation worked!")
                update_env_with_complete_mnemonic(test_mnemonic)
                found_match = True
            else:
                print("❌ Checksum calculation didn't match expected address")
                
        except Exception as e:
            print(f"❌ Checksum method failed: {e}")
    
    # Method 3: Try all possible words (this would take a very long time)
    if not found_match:
        print(f"\n🔍 Method 3: Brute force search (first 50 words)...")
        word_list = word_list_english()[:50]  # Limit to first 50 for demo
        
        for i, word in enumerate(word_list):
            try:
                test_mnemonic = mnemonic_phrase + " " + word
                private_key = mnemonic.to_private_key(test_mnemonic)
                address = account.address_from_private_key(private_key)
                
                if address == expected_address:
                    print(f"🎯 ✅ FOUND MATCH with '{word}' at position {i}!")
                    print(f"Complete mnemonic: {test_mnemonic}")
                    update_env_with_complete_mnemonic(test_mnemonic)
                    found_match = True
                    break
                    
                if i % 10 == 0:
                    print(f"  Checked {i+1} words...")
                    
            except Exception:
                continue
    
    if not found_match:
        print("\n❌ Could not find the 25th word automatically.")
        print("\n💡 Possible solutions:")
        print("1. Check your wallet app for the complete 25-word phrase")
        print("2. Look for wallet backup files")
        print("3. Some wallets display seed phrases in settings")
        print("4. Contact your wallet provider support")
        print("\n⚠️  Alternative: Your mnemonic might be from a different standard")
        print("   (BIP39 vs Algorand native). Try importing into different wallets.")

def update_env_with_complete_mnemonic(complete_mnemonic):
    """Update .env file with the complete 25-word mnemonic"""
    try:
        # Read current .env content
        env_path = ".env"
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update the mnemonic line
        with open(env_path, 'w') as f:
            for line in lines:
                if line.startswith('CREATOR_MNEMONIC='):
                    f.write(f'CREATOR_MNEMONIC="{complete_mnemonic}"\n')
                else:
                    f.write(line)
        
        print(f"✅ Updated .env file with complete 25-word mnemonic")
        
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")

def test_wallet_generation():
    """Test if we can generate the wallet with current mnemonic"""
    try:
        mnemonic_phrase = os.getenv("CREATOR_MNEMONIC")
        private_key = mnemonic.to_private_key(mnemonic_phrase)
        address = account.address_from_private_key(private_key)
        
        print(f"\n✅ SUCCESS! Wallet generated:")
        print(f"Address: {address}")
        print(f"Ready for testnet transactions!")
        
        return True
    except Exception as e:
        print(f"\n❌ Still cannot generate wallet: {e}")
        return False

if __name__ == "__main__":
    try_24_word_variations()
    
    print(f"\n" + "=" * 60)
    print("Testing current mnemonic...")
    if test_wallet_generation():
        print("\n🎉 Your wallet is now ready for Algorand testnet transactions!")
        print("Next steps:")
        print("1. Fund your wallet: https://testnet.algoexplorer.io/dispenser") 
        print("2. Run: python test_wallet_connection.py")
    else:
        print("\n🔧 Manual intervention needed - check wallet backup sources")
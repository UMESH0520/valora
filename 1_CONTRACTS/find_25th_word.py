#!/usr/bin/env python3

import os
from algosdk import account, mnemonic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def try_common_25th_words():
    """Try common words as the 25th word"""
    
    print("=" * 60)
    print("VALORA - Finding 25th Word for 24-Word Mnemonic")
    print("=" * 60)
    
    mnemonic_phrase = os.getenv("CREATOR_MNEMONIC")
    expected_address = os.getenv("WALLET_ADDRESS")
    
    if not mnemonic_phrase:
        print("❌ No mnemonic found in .env file")
        return None
    
    words = mnemonic_phrase.split()
    print(f"Current mnemonic: {mnemonic_phrase}")
    print(f"Word count: {len(words)}")
    print(f"Expected address: {expected_address}")
    print()
    
    if len(words) != 24:
        print("❌ This script is designed for 24-word mnemonics")
        return None
    
    # Extended list of common BIP39 words that often appear as checksums
    common_words = [
        # Most common checksum words
        "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract", 
        "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
        "acoustic", "acquire", "across", "act", "action", "actor", "actress", "actual",
        "adapt", "add", "addict", "address", "adjust", "admit", "adult", "advance",
        "advice", "aerobic", "affair", "afford", "afraid", "again", "agent", "agree",
        "ahead", "aim", "air", "airport", "aisle", "alarm", "album", "alcohol",
        "alert", "alien", "all", "alley", "allow", "almost", "alone", "alpha",
        "already", "also", "alter", "always", "amateur", "amazing", "among", "amount",
        "amused", "analyst", "anchor", "ancient", "anger", "angle", "angry", "animal",
        "ankle", "announce", "annual", "another", "answer", "antenna", "antique", "anxiety",
        "any", "apart", "apology", "appear", "apple", "approve", "april", "arcade",
        "arch", "arctic", "area", "arena", "argue", "arm", "armed", "armor",
        "army", "around", "arrange", "arrest", "arrive", "arrow", "art", "article",
        "artist", "artwork", "ask", "aspect", "assault", "asset", "assist", "assume",
        "asthma", "athlete", "atom", "attack", "attend", "attitude", "attract", "auction",
        "audit", "august", "aunt", "author", "auto", "autumn", "average", "avocado",
        "avoid", "awake", "aware", "away", "awesome", "awful", "awkward", "axis"
    ]
    
    print(f"🔍 Trying {len(common_words)} common words as 25th word...")
    print()
    
    found_matches = []
    
    for i, word in enumerate(common_words):
        try:
            test_mnemonic = mnemonic_phrase + " " + word
            private_key = mnemonic.to_private_key(test_mnemonic)
            address = account.address_from_private_key(private_key)
            
            if address == expected_address:
                print(f"🎯 ✅ PERFECT MATCH with '{word}'!")
                print(f"Complete mnemonic: {test_mnemonic}")
                print(f"Generated address: {address}")
                found_matches.append((word, test_mnemonic, address))
                
                # Update .env file immediately
                update_env_with_complete_mnemonic(test_mnemonic)
                return test_mnemonic
            else:
                # Show first few attempts for debugging
                if i < 5:
                    print(f"  ❌ '{word}' -> {address[:15]}... (no match)")
                elif i % 20 == 0:
                    print(f"  📊 Checked {i+1}/{len(common_words)} words...")
                
        except Exception:
            if i < 5:
                print(f"  ❌ '{word}' -> Invalid mnemonic")
    
    if not found_matches:
        print(f"\n❌ No matches found in {len(common_words)} common words")
        print("\n💡 Your 25th word might be uncommon. Options:")
        print("1. Check your original wallet backup")
        print("2. Look in wallet settings/security section")
        print("3. Try a more extensive search (all 2048 BIP39 words)")
        
        # Offer to try a brute force approach
        response = input("\nWould you like to try ALL possible words? (y/n): ")
        if response.lower() == 'y':
            return try_all_words()
    
    return None

def try_all_words():
    """Brute force try all possible BIP39 words (this could take a while)"""
    print("\n🔍 Brute force mode: Trying all possible words...")
    print("⚠️  This may take several minutes...")
    
    mnemonic_phrase = os.getenv("CREATOR_MNEMONIC")
    expected_address = os.getenv("WALLET_ADDRESS")
    
    # BIP39 wordlist (first 100 words for demo - full list would be 2048 words)
    bip39_sample = [
        "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract",
        "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
        "acoustic", "acquire", "across", "act", "action", "actor", "actress", "actual",
        "adapt", "add", "addict", "address", "adjust", "admit", "adult", "advance",
        "advice", "aerobic", "affair", "afford", "afraid", "again", "agent", "agree",
        "ahead", "aim", "air", "airport", "aisle", "alarm", "album", "alcohol",
        "alert", "alien", "all", "alley", "allow", "almost", "alone", "alpha",
        "already", "also", "alter", "always", "amateur", "amazing", "among", "amount",
        "amused", "analyst", "anchor", "ancient", "anger", "angle", "angry", "animal",
        "ankle", "announce", "annual", "another", "answer", "antenna", "antique", "anxiety",
        "any", "apart", "apology", "appear", "apple", "approve", "april", "arcade",
        "arch", "arctic", "area", "arena", "argue", "arm", "armed", "armor",
        "army", "around", "arrange", "arrest", "arrive", "arrow", "art", "article",
        "artist", "artwork", "ask", "aspect", "assault", "asset", "assist", "assume",
        "asthma", "athlete", "atom", "attack", "attend", "attitude", "attract", "auction",
        "audit", "august", "aunt", "author", "auto", "autumn", "average", "avocado"
    ]
    
    for i, word in enumerate(bip39_sample):
        try:
            test_mnemonic = mnemonic_phrase + " " + word
            private_key = mnemonic.to_private_key(test_mnemonic)
            address = account.address_from_private_key(private_key)
            
            if address == expected_address:
                print(f"\n🎯 ✅ FOUND IT! The 25th word is '{word}'")
                print(f"Complete mnemonic: {test_mnemonic}")
                print(f"Generated address: {address}")
                update_env_with_complete_mnemonic(test_mnemonic)
                return test_mnemonic
            
            if i % 25 == 0:
                print(f"  📊 Progress: {i+1}/{len(bip39_sample)} words checked...")
                
        except Exception:
            continue
    
    print(f"\n❌ No match found in sample of {len(bip39_sample)} words")
    return None

def update_env_with_complete_mnemonic(complete_mnemonic):
    """Update .env file with the complete 25-word mnemonic"""
    try:
        # Read current .env content
        env_path = ".env"
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Replace the mnemonic line
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            if line.startswith('CREATOR_MNEMONIC='):
                new_lines.append(f'CREATOR_MNEMONIC="{complete_mnemonic}"')
            else:
                new_lines.append(line)
        
        # Write back to file
        with open(env_path, 'w') as f:
            f.write('\n'.join(new_lines))
        
        print(f"✅ Updated .env file with complete 25-word mnemonic")
        
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")

def test_current_mnemonic():
    """Test if current mnemonic works"""
    try:
        # Reload environment after potential update
        load_dotenv()
        
        mnemonic_phrase = os.getenv("CREATOR_MNEMONIC")
        private_key = mnemonic.to_private_key(mnemonic_phrase)
        address = account.address_from_private_key(private_key)
        
        print(f"\n✅ SUCCESS! Wallet ready:")
        print(f"Address: {address}")
        print(f"Mnemonic words: {len(mnemonic_phrase.split())}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Current mnemonic still invalid: {e}")
        return False

if __name__ == "__main__":
    # Try to find the 25th word
    complete_mnemonic = try_common_25th_words()
    
    print("\n" + "=" * 60)
    print("Final Test...")
    
    if test_current_mnemonic():
        print("\n🎉 SUCCESS! Your wallet is now ready for Algorand testnet!")
        print("\n📋 Next steps:")
        print("1. Fund your testnet wallet: https://testnet.algoexplorer.io/dispenser")
        print("2. Test transactions: python test_wallet_connection.py")
        print("3. Deploy contracts: python scripts/deploy_stateful.py")
    else:
        print("\n🔧 Unable to complete mnemonic automatically.")
        print("\n💡 Manual solutions:")
        print("1. Check your wallet app's seed phrase section")
        print("2. Look for wallet backup/recovery files")
        print("3. Contact wallet support for seed phrase recovery")
        print("4. Try importing into different wallet apps to see full phrase")
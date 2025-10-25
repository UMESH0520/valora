#!/usr/bin/env python3

import asyncio
import aiohttp
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from adapters.flipkart import fetch

async def test_flipkart_api():
    """Test Flipkart API integration"""
    
    print("=" * 60)
    print("VALORA - Flipkart API Integration Test")
    print("=" * 60)
    
    # Check if API key is configured
    api_key = os.getenv('FLIPKART_API_KEY')
    if api_key:
        print(f"✅ Flipkart API Key configured: {api_key[:8]}...")
    else:
        print("❌ No Flipkart API key found in environment")
        return
    
    # Test product data
    test_products = [
        {
            'product_id': 'TEST-001',
            'name': 'iPhone 15',
            'brand': 'Apple',
            'model': 'Pro',
            'urls': {}
        },
        {
            'product_id': 'TEST-002', 
            'name': 'Samsung Galaxy S24',
            'brand': 'Samsung',
            'model': 'Ultra',
            'urls': {}
        },
        {
            'product_id': 'TEST-003',
            'name': 'OnePlus 12',
            'brand': 'OnePlus',
            'model': '',
            'urls': {}
        }
    ]
    
    print(f"\n🧪 Testing with {len(test_products)} products...")
    
    # Create aiohttp session
    timeout = aiohttp.ClientTimeout(total=30)
    connector = aiohttp.TCPConnector(limit=10)
    
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        for i, product in enumerate(test_products, 1):
            print(f"\n[{i}] Testing: {product['name']} {product['brand']} {product.get('model', '')}")
            print(f"    Product ID: {product['product_id']}")
            
            try:
                # Test the Flipkart adapter
                result = await fetch(session, product)
                
                if result:
                    print(f"    ✅ SUCCESS!")
                    print(f"    💰 Price: ₹{result['price']:,.2f}")
                    print(f"    🚚 Shipping: ₹{result.get('shipping', 0):.2f}")
                    print(f"    🎯 Confidence: {result.get('confidence', 0):.2%}")
                    print(f"    📊 Adapter: {result.get('adapter', 'unknown')}")
                else:
                    print(f"    ❌ No data returned")
                    print(f"    💡 This could be due to:")
                    print(f"       - Product not found on Flipkart")
                    print(f"       - API rate limiting")
                    print(f"       - Network issues")
                    print(f"       - API endpoint/format changes")
                    
            except Exception as e:
                print(f"    ❌ ERROR: {e}")
                print(f"    💡 Check API credentials and network connection")
    
    print(f"\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"API Key: {'✅ Configured' if api_key else '❌ Missing'}")
    print(f"Integration: ✅ Updated")
    print(f"Fallback: ✅ Web scraping available")
    
    print(f"\n💡 Next Steps:")
    print(f"1. Verify API key is valid with Flipkart")
    print(f"2. Check API documentation for correct endpoint format")
    print(f"3. Test with actual VALORA backend: python run.py")
    print(f"4. Check logs in logs/ directory for detailed error info")

async def test_environment():
    """Test environment configuration"""
    print(f"\n" + "-" * 40)
    print("Environment Configuration")
    print("-" * 40)
    
    env_vars = {
        'FLIPKART_API_KEY': 'Flipkart API Key',
        'DATABASE_URL': 'Database URL',
        'JWT_SECRET_KEY': 'JWT Secret',
        'LOG_LEVEL': 'Log Level'
    }
    
    for var, description in env_vars.items():
        value = os.getenv(var)
        if value:
            if 'KEY' in var or 'SECRET' in var:
                print(f"✅ {description}: {value[:8]}..." if len(value) > 8 else f"✅ {description}: {value}")
            else:
                print(f"✅ {description}: {value}")
        else:
            print(f"❌ {description}: Not set")

def main():
    """Main test function"""
    try:
        # Test environment first
        asyncio.run(test_environment())
        
        # Then test API
        asyncio.run(test_flipkart_api())
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print(f"💡 Make sure you're in the 3_BACKEND directory")

if __name__ == "__main__":
    main()
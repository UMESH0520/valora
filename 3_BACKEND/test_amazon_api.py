#!/usr/bin/env python3
"""
Test script for WebScrapingAPI Amazon integration
"""
import asyncio
import aiohttp
import json

async def test_webscrapingapi():
    """Test the WebScrapingAPI with your API key"""
    api_key = 'RHEQHy4bQjAfEzoWPmqhhfyqndqKkHrN'
    url = 'https://ecom.webscrapingapi.com/v1'
    
    # Test product search
    params = {
        'q': 'iPhone 15',
        'type': 'search',
        'amazon_domain': 'amazon.com',
        'engine': 'amazon',
        'api_key': api_key,
    }
    
    print("Testing WebScrapingAPI Amazon search...")
    print(f"URL: {url}")
    print(f"Params: {params}")
    print("-" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")
                
                if response.status == 200:
                    try:
                        data = await response.json()
                        print("✅ API Response (JSON):")
                        print(json.dumps(data, indent=2))
                        
                        # Try to extract price info
                        if 'results' in data and data['results']:
                            first_result = data['results'][0]
                            print("\n🏷️ First product info:")
                            for key in ['title', 'price', 'rating', 'url']:
                                if key in first_result:
                                    print(f"  {key}: {first_result[key]}")
                        
                        return True
                    except Exception as json_error:
                        print(f"❌ JSON parsing error: {json_error}")
                        text = await response.text()
                        print(f"Raw response: {text[:500]}...")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ API Error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

async def test_amazon_adapter():
    """Test the Amazon adapter with mock product data"""
    print("\n" + "="*60)
    print("Testing VALORA Amazon Adapter")
    print("="*60)
    
    # Import the adapter
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
    
    # Set environment variable
    os.environ['WEBSCRAPINGAPI_ECOM_API_KEY'] = 'RHEQHy4bQjAfEzoWPmqhhfyqndqKkHrN'
    os.environ['AMAZON_DOMAIN'] = 'amazon.com'
    
    from adapters.amazon import fetch
    
    # Mock product data
    product = {
        'product_id': 'TEST-001',
        'name': 'iPhone 15',
        'brand': 'Apple',
        'model': '128GB'
    }
    
    print(f"Testing product: {product}")
    
    try:
        async with aiohttp.ClientSession() as session:
            result = await fetch(session, product)
            
            if result:
                print("✅ Amazon adapter result:")
                print(json.dumps(result, indent=2))
                return True
            else:
                print("❌ No result from Amazon adapter")
                return False
                
    except Exception as e:
        print(f"❌ Adapter error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting WebScrapingAPI Tests")
    print("="*60)
    
    # Test 1: Direct API call
    api_success = await test_webscrapingapi()
    
    # Test 2: VALORA adapter
    if api_success:
        adapter_success = await test_amazon_adapter()
    else:
        print("\n⚠️ Skipping adapter test due to API failure")
        adapter_success = False
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    print(f"Direct API Test: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"Adapter Test: {'✅ PASS' if adapter_success else '❌ FAIL'}")
    
    if api_success and adapter_success:
        print("\n🎉 All tests passed! Your API integration is working.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    asyncio.run(main())
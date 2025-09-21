#!/usr/bin/env python3
"""
Test script to verify Wikipedia API access
"""

import requests
import sys

def test_wikipedia_api():
    """Test Wikipedia API access with proper headers."""
    print("🔍 Testing Wikipedia API access...")
    
    # Headers to avoid 403 errors
    headers = {
        'User-Agent': 'WikiRace Game/1.0 (https://github.com/yourusername/wikirace)'
    }
    
    # Test search API
    print("📝 Testing search API...")
    try:
        response = requests.get('https://en.wikipedia.org/w/api.php', {
            'action': 'query',
            'list': 'search',
            'srsearch': 'Asia',
            'format': 'json',
            'srlimit': 1
        }, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Search API working")
            data = response.json()
            if data["query"]["search"]:
                print(f"✅ Found search result: {data['query']['search'][0]['title']}")
            else:
                print("⚠️  No search results found")
        else:
            print(f"❌ Search API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Search API error: {e}")
        return False
    
    # Test random API
    print("\n🎲 Testing random API...")
    try:
        response = requests.get('https://en.wikipedia.org/w/api.php', {
            'action': 'query',
            'format': 'json',
            'list': 'random',
            'rnnamespace': 0,
            'rnlimit': 1
        }, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Random API working")
            data = response.json()
            if data["query"]["random"]:
                print(f"✅ Found random page: {data['query']['random'][0]['title']}")
            else:
                print("⚠️  No random results found")
        else:
            print(f"❌ Random API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Random API error: {e}")
        return False
    
    return True

def main():
    """Run Wikipedia API tests."""
    print("🧪 Wikipedia API Test")
    print("=" * 40)
    
    if test_wikipedia_api():
        print("\n🎉 Wikipedia API is working correctly!")
        print("\n🚀 You can now run your WikiRace project")
        return True
    else:
        print("\n❌ Wikipedia API tests failed.")
        print("\n💡 Possible solutions:")
        print("   - Check your internet connection")
        print("   - Try again later (Wikipedia might be temporarily unavailable)")
        print("   - Check if your firewall is blocking requests")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

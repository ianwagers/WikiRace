#!/usr/bin/env python3
"""
Test script to verify page title fetching
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from gui.SoloGamePage import SoloGamePage
from PyQt6.QtWidgets import QApplication, QTabWidget

def test_page_title_fetching():
    """Test page title fetching functionality."""
    print("🔍 Testing page title fetching...")
    
    # Create a minimal QApplication for testing
    app = QApplication([])
    tab_widget = QTabWidget()
    
    # Create SoloGamePage instance
    solo_page = SoloGamePage(tab_widget, "https://en.wikipedia.org/?curid=123", "https://en.wikipedia.org/?curid=456")
    
    # Test URLs
    test_urls = [
        "https://en.wikipedia.org/?curid=123",  # Should work with API
        "https://en.wikipedia.org/wiki/Asia",   # Should work with HTML parsing
        "https://en.wikipedia.org/wiki/InvalidPage12345",  # Should handle gracefully
    ]
    
    print("\n📝 Testing different URL types:")
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. Testing: {url}")
        try:
            title = solo_page.getTitleFromUrl(url)
            print(f"   ✅ Title: {title}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test page ID method directly
    print(f"\n🔍 Testing page ID method:")
    try:
        title = solo_page.getTitleFromPageId("123")
        print(f"   ✅ Page ID 123 title: {title}")
    except Exception as e:
        print(f"   ❌ Page ID error: {e}")
    
    app.quit()
    return True

def main():
    """Run page title tests."""
    print("🧪 Page Title Fetching Test")
    print("=" * 40)
    
    try:
        if test_page_title_fetching():
            print("\n🎉 Page title fetching tests completed!")
            print("\n🚀 Your WikiRace project should now handle page titles correctly")
            return True
        else:
            print("\n❌ Page title fetching tests failed.")
            return False
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

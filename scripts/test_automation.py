#!/usr/bin/env python3
"""
Test script for social media automation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.social_media_automation import SocialMediaAutomation

def test_automation():
    """Test the automation without actually posting"""
    try:
        automation = SocialMediaAutomation()

        # Test event scraping
        print("Testing event scraping...")
        events = automation.scrape_events("2025-09-20")
        print(f"Found {len(events)} events")

        # Test content generation
        print("\nTesting content generation...")
        content = automation.generate_social_content(events, "2025-09-20")
        print(f"Social: {content['social']}")
        print(f"Reel: {content['reel']}")

        # Test media selection
        print("\nTesting media selection...")
        media = automation.select_random_media()
        if media:
            print(f"Selected media: {media.get('name', 'Unknown')}")
        else:
            print("No media found")

        print("\n✅ All tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_automation()
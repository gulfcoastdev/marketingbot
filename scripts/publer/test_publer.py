#!/usr/bin/env python3
"""
Simple Publer API Test Script
Tests basic functionality with MiCasa.Rentals content
"""

import os
import sys
from datetime import datetime, timedelta
from publer_poster import PublerPoster

def test_publer_connection():
    """Test basic Publer API connection and setup"""
    print("🚀 Testing Publer API Connection...")

    try:
        # Initialize poster
        poster = PublerPoster()
        print("✅ PublerPoster initialized successfully")

        # Test getting workspaces
        print("\n📁 Getting workspaces...")
        workspaces = poster.get_workspaces()
        if not workspaces:
            print("❌ Failed to get workspaces")
            return False

        # Test getting accounts
        print("\n🔗 Getting connected accounts...")
        accounts = poster.get_accounts()
        if not accounts:
            print("❌ Failed to get accounts")
            return False

        print(f"\n📊 Available platforms:")
        for platform, account_list in poster.accounts.items():
            print(f"  • {platform}: {len(account_list)} account(s)")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def create_test_post():
    """Create a test post for MiCasa.Rentals"""
    print("\n🎯 Creating test post...")

    try:
        poster = PublerPoster()

        # Setup
        poster.get_workspaces()
        poster.get_accounts()

        # Create a test post
        test_content = """🏖️ Escape to paradise at MiCasa.Rentals!

Our luxury Pensacola Beach vacation rentals offer:
✨ Stunning beachfront views
🏡 Fully furnished accommodations
🌊 Steps from pristine beaches
🎣 Perfect for families & groups

Book your dream getaway today!

#PensacolaBeach #VacationRental #BeachLife #MiCasaRentals"""

        # Schedule post for 1 minute from now (for testing)
        schedule_time = datetime.now() + timedelta(minutes=1)

        result = poster.create_post(
            text=test_content,
            platforms=['facebook'],  # Start with just Facebook
            schedule_time=schedule_time
        )

        if result:
            print("✅ Test post created successfully!")
            print(f"📅 Scheduled for: {schedule_time.strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            print("❌ Failed to create test post")
            return False

    except Exception as e:
        print(f"❌ Error creating test post: {e}")
        return False

def create_video_post(video_path, caption):
    """Create a post with video content"""
    print(f"\n🎬 Creating video post with: {video_path}")

    try:
        poster = PublerPoster()

        # Setup
        poster.get_workspaces()
        poster.get_accounts()

        result = poster.create_post(
            text=caption,
            platforms=['facebook', 'instagram'],
            media_path=video_path,
            schedule_time=datetime.now() + timedelta(minutes=5)
        )

        if result:
            print("✅ Video post created successfully!")
            return True
        else:
            print("❌ Failed to create video post")
            return False

    except Exception as e:
        print(f"❌ Error creating video post: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 PUBLER API TEST SUITE")
    print("=" * 60)

    # Test 1: Basic connection
    if not test_publer_connection():
        print("\n❌ Basic connection test failed. Exiting.")
        sys.exit(1)

    print("\n" + "=" * 60)

    # Test 2: Create text post
    print("TEST 2: Creating text post...")
    if create_test_post():
        print("✅ Text post test passed!")
    else:
        print("❌ Text post test failed!")

    print("\n" + "=" * 60)

    # Test 3: Create video post (optional)
    video_test = input("Do you want to test video posting? (y/n): ").lower().strip()
    if video_test == 'y':
        video_path = input("Enter path to video file: ").strip()
        if os.path.exists(video_path):
            caption = "🎥 Check out this amazing view from our Pensacola Beach rental! Book your stay at MiCasa.Rentals #PensacolaBeach #VacationRental"
            create_video_post(video_path, caption)
        else:
            print(f"❌ Video file not found: {video_path}")

    print("\n🎉 Test suite completed!")

if __name__ == "__main__":
    main()
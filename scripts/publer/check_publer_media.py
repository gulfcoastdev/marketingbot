#!/usr/bin/env python3
"""
Check Publer Media Script
Quick script to check what media is available in Publer
"""

from publer_poster import PublerPoster
import json

def check_media():
    """Check available media in Publer"""
    try:
        poster = PublerPoster()
        poster.get_workspaces()

        # Get media
        response = poster.session.get(f'{poster.base_url}/media')
        response.raise_for_status()

        data = response.json()
        media_items = data.get('media', [])
        total = data.get('total', 0)

        print(f"📊 Media Summary:")
        print(f"   Total items: {total}")
        print(f"   Items returned: {len(media_items)}")
        print()

        if media_items:
            print("📁 Available Media:")
            for item in media_items:
                filename = item.get('filename', 'Unknown')
                file_type = item.get('type', 'unknown')
                file_id = item.get('id', 'N/A')
                created = item.get('created_at', 'N/A')

                print(f"  🎬 {filename}")
                print(f"     ID: {file_id}")
                print(f"     Type: {file_type}")
                print(f"     Created: {created}")
                print()

            # Count branded videos
            branded_count = sum(1 for item in media_items
                              if any(f'{i}.mp4' in item.get('filename', '') for i in range(1, 32)))
            print(f"🎯 Branded videos (1-31.mp4): {branded_count} found")
        else:
            print("📭 No media items found")
            print()
            print("💡 To upload branded videos:")
            print("   1. Go to Publer dashboard → Media Library")
            print("   2. Upload videos from: brandingburner/promovideosraw_branded/")
            print("   3. Name them: 1_branded.mp4, 2_branded.mp4, etc.")

        return media_items

    except Exception as e:
        print(f"❌ Error checking media: {e}")
        return None

if __name__ == "__main__":
    print("🔍 Checking Publer Media Library...")
    print("=" * 40)
    check_media()
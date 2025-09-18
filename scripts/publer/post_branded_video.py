#!/usr/bin/env python3
"""
Post Branded Video Script
Automatically posts branded videos from the promovideosraw_branded folder
"""

import os
import random
import argparse
from datetime import datetime, timedelta
from publer_poster import PublerPoster

class BrandedVideosPoster:
    def __init__(self):
        self.poster = PublerPoster()
        self.branded_videos_dir = "brandingburner/promovideosraw_branded"

    def setup_api(self):
        """Initialize Publer API connection"""
        try:
            self.poster.get_workspaces()
            self.poster.get_accounts()
            print(f"✅ Connected to Publer API")
            print(f"📱 Available platforms: {list(self.poster.accounts.keys())}")
            return True
        except Exception as e:
            print(f"❌ Failed to setup Publer API: {e}")
            return False

    def get_available_videos(self):
        """Get list of branded videos"""
        if not os.path.exists(self.branded_videos_dir):
            print(f"❌ Branded videos directory not found: {self.branded_videos_dir}")
            return []

        videos = [f for f in os.listdir(self.branded_videos_dir) if f.endswith('.mp4')]
        videos.sort()  # Sort numerically
        print(f"📹 Found {len(videos)} branded videos")
        return videos

    def generate_caption(self, video_name=None):
        """Generate marketing caption for MiCasa.Rentals"""
        captions = [
            "🏖️ Escape to paradise at Pensacola Beach! Our luxury vacation rentals offer stunning beachfront views and unforgettable experiences. Book your dream getaway with MiCasa.Rentals today! #PensacolaBeach #VacationRental #BeachLife #MiCasaRentals",

            "🌊 Wake up to ocean views every morning! MiCasa.Rentals provides fully furnished beachfront accommodations perfect for families, couples, and groups. Experience the best of Pensacola Beach! #BeachVacation #PensacolaBeach #MiCasaRentals #OceanView",

            "✨ Your perfect beach vacation awaits! From pristine white sand beaches to luxury amenities, MiCasa.Rentals has everything you need for an amazing Pensacola Beach getaway. Book now! #PensacolaBeach #LuxuryRental #BeachVacation #MiCasaRentals",

            "🏡 Home away from home on Pensacola Beach! Our premium vacation rentals feature full kitchens, comfortable living spaces, and steps-to-beach access. Create memories that last a lifetime with MiCasaRentals! #VacationRental #PensacolaBeach #BeachHouse #MiCasaRentals",

            "🌅 Breathtaking sunrises, crystal clear waters, and luxury accommodations - that's the MiCasa.Rentals experience! Book your Pensacola Beach vacation today and discover paradise. #PensacolaBeach #BeachLife #VacationRental #MiCasaRentals #Sunrise",

            "🎣 Adventure and relaxation await at Pensacola Beach! Whether you're fishing, swimming, or just soaking up the sun, MiCasa.Rentals provides the perfect basecamp for your beach vacation. #PensacolaBeach #BeachFun #VacationRental #MiCasaRentals",

            "🏖️ White sand beaches, emerald waters, and luxury rentals - Pensacola Beach has it all! Let MiCasa.Rentals be your gateway to the ultimate beach vacation experience. Book today! #EmeraldCoast #PensacolaBeach #LuxuryTravel #MiCasaRentals",

            "🌴 Paradise found at Pensacola Beach! Our spacious vacation rentals offer all the comforts of home with unbeatable beachfront locations. Start planning your escape with MiCasa.Rentals! #BeachParadise #PensacolaBeach #VacationRental #MiCasaRentals"
        ]

        return random.choice(captions)

    def post_random_video(self, platforms=None, schedule_minutes=0):
        """Post a random branded video"""
        if platforms is None:
            platforms = ['facebook']

        videos = self.get_available_videos()
        if not videos:
            print("❌ No branded videos found")
            return False

        # Select random video
        selected_video = random.choice(videos)
        video_path = os.path.join(self.branded_videos_dir, selected_video)

        print(f"🎬 Selected video: {selected_video}")

        # Generate caption
        caption = self.generate_caption(selected_video)

        # Schedule time
        schedule_time = None
        if schedule_minutes > 0:
            schedule_time = datetime.now() + timedelta(minutes=schedule_minutes)
            print(f"📅 Scheduling for: {schedule_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("📤 Posting immediately")

        # Create post
        try:
            result = self.poster.create_post(
                text=caption,
                platforms=platforms,
                media_path=video_path,
                schedule_time=schedule_time
            )

            if result:
                print("✅ Video posted successfully!")
                return True
            else:
                print("❌ Failed to post video")
                return False

        except Exception as e:
            print(f"❌ Error posting video: {e}")
            return False

    def post_specific_video(self, video_number, platforms=None, schedule_minutes=0):
        """Post a specific numbered video"""
        if platforms is None:
            platforms = ['facebook']

        video_filename = f"{video_number}_branded.mp4"
        video_path = os.path.join(self.branded_videos_dir, video_filename)

        if not os.path.exists(video_path):
            print(f"❌ Video not found: {video_filename}")
            return False

        print(f"🎬 Posting video: {video_filename}")

        # Generate caption
        caption = self.generate_caption(video_filename)

        # Schedule time
        schedule_time = None
        if schedule_minutes > 0:
            schedule_time = datetime.now() + timedelta(minutes=schedule_minutes)
            print(f"📅 Scheduling for: {schedule_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Create post
        try:
            result = self.poster.create_post(
                text=caption,
                platforms=platforms,
                media_path=video_path,
                schedule_time=schedule_time
            )

            if result:
                print("✅ Video posted successfully!")
                return True
            else:
                print("❌ Failed to post video")
                return False

        except Exception as e:
            print(f"❌ Error posting video: {e}")
            return False

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Post branded videos to social media via Publer')
    parser.add_argument('--video', type=int, help='Specific video number to post (1-31)')
    parser.add_argument('--platforms', nargs='+', default=['facebook'],
                       help='Social media platforms (facebook, instagram, twitter, linkedin)')
    parser.add_argument('--schedule', type=int, default=0,
                       help='Schedule post for X minutes from now (0 = immediate)')
    parser.add_argument('--random', action='store_true',
                       help='Post a random video instead of specific number')

    args = parser.parse_args()

    print("🚀 MiCasa.Rentals Video Poster")
    print("=" * 50)

    # Initialize poster
    poster = BrandedVideosPoster()

    if not poster.setup_api():
        return

    # Post video
    if args.random or args.video is None:
        success = poster.post_random_video(
            platforms=args.platforms,
            schedule_minutes=args.schedule
        )
    else:
        success = poster.post_specific_video(
            video_number=args.video,
            platforms=args.platforms,
            schedule_minutes=args.schedule
        )

    if success:
        print("🎉 Video posting completed!")
    else:
        print("❌ Video posting failed!")

if __name__ == "__main__":
    main()
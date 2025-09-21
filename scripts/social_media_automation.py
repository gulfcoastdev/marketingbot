#!/usr/bin/env python3
"""
Social Media Automation Script
Scrapes Pensacola events, generates AI content, and posts to social media
"""

import os
import sys
import json
import random
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv
import openai
import re

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from daily_events_scraper import DailyEventsScraper
from scripts.publer.publer_poster import PublerPoster

# Load environment variables
load_dotenv()

class SocialMediaAutomation:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.publer = PublerPoster()
        self.scraper = DailyEventsScraper()

        # Initialize Publer
        if not self.publer.get_workspaces():
            raise Exception("Failed to connect to Publer API")

        if not self.publer.get_accounts():
            raise Exception("Failed to get Publer accounts")

    def scrape_events(self, date_str):
        """Scrape events for given date"""
        print(f"🔍 Scraping events for {date_str}...")
        events = self.scraper.get_events_for_date(date_str)
        print(f"✅ Found {len(events)} events")
        return events

    def generate_social_content(self, events, date_str):
        """Generate social media content using OpenAI function calling"""
        print("🤖 Generating social media content...")

        # Prepare the complete events data as JSON
        events_json = {
            "date": date_str,
            "events": events[:10],  # Include more events for better content generation
            "metadata": {
                "search_url": f"https://www.visitpensacola.com/events/?range=1&date-from={date_str}&date-to={date_str}"
            }
        }

        prompt = f"""You are a content assistant. I will provide a JSON containing event data (title, date, location, description, link, metadata).

Your task is to return a JSON object with two keys:

long_post:

Format as a social media caption with:

Header: ✨ What's Happening in Pensacola – [Day, Date] ✨

Group events under: Downtown vibes, Beach beats, Also happening.

List 3–4 event titles per group, separated by commas, no bullets.

End with two lines:
📍 For more: Visit Pensacola → [metadata.search_url]
✨ Visiting Pensacola? Stay with us → www.micasa.rentals

Keep it plain text, cross-platform friendly.

short_post:

Write 1–2 catchy sentences highlighting 2–3 engaging events.

End with the same two links:
📍 For more: Visit Pensacola → [metadata.search_url]
✨ Visiting Pensacola? Stay with us → www.micasa.rentals

Keep it casual and shorter (ideal for Reels/TikTok captions).

Here's the event data: {json.dumps(events_json, indent=2)}"""

        # Define the function schema for OpenAI
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_social_posts",
                    "description": "Create social media posts for Pensacola events",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "long_post": {
                                "type": "string",
                                "description": "Long-form social media post with event details"
                            },
                            "short_post": {
                                "type": "string",
                                "description": "Short, catchy post for Reels/TikTok"
                            }
                        },
                        "required": ["long_post", "short_post"]
                    }
                }
            }
        ]

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "create_social_posts"}},
                max_tokens=500,
                temperature=0.7
            )

            # Extract the function call result
            if response.choices[0].message.tool_calls:
                function_call = response.choices[0].message.tool_calls[0]
                function_args = json.loads(function_call.function.arguments)

                long_post = function_args.get('long_post', '')
                short_post = function_args.get('short_post', '')

                print(f"✅ Generated content successfully")
                print(f"Long post: {long_post[:100]}...")
                print(f"Short post: {short_post[:100]}...")

                return {
                    'social': long_post,
                    'reel': short_post
                }
            else:
                raise Exception("No function call returned from OpenAI")

        except Exception as e:
            print(f"❌ Error generating content: {e}")
            return {
                'social': f"✨ What's Happening in Pensacola – {date_str} ✨\n\nDowntown vibes, Beach beats, and more!\n\n📍 For more: Visit Pensacola → https://www.visitpensacola.com/events/\n✨ Visiting Pensacola? Stay with us → www.micasa.rentals",
                'reel': f"Pensacola's got the vibes today! 🌊✨\n\n📍 For more: Visit Pensacola → https://www.visitpensacola.com/events/\n✨ Visiting Pensacola? Stay with us → www.micasa.rentals"
            }

    def generate_pensacola_fact(self):
        """Generate a random fact about Pensacola, Gulf Coast, or Escambia area"""
        print("🧠 Generating Pensacola fact...")

        prompt = """Generate a single interesting, fun fact about Pensacola, Gulf Coast, or Escambia County area.

Requirements:
- Focus on history, nature, culture, attractions, or unique features
- Make it engaging and shareable for social media
- Keep it under 300 characters
- Include relevant emojis
- Make it feel local and authentic
- Don't use hashtags

Examples:
Did you know?
🏴‍☠️ Pensacola was once the hideout of pirate Jean Lafitte! The Gulf Coast's swashbuckling history lives on in our crystal waters ⚓
Fun Fact:
🌊 The Gulf Islands National Seashore protects 150 miles of pristine coastline - some of the whitest sand beaches in the world! 🏖️

Generate ONE fact in this style:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.8
            )

            fact = response.choices[0].message.content.strip()
            print(f"✅ Generated fact: {fact}")
            return fact

        except Exception as e:
            print(f"❌ Error generating fact: {e}")
            return "🏖️ Pensacola Beach boasts some of the world's whitest sand beaches, made of pure quartz crystals! ✨"

    def post_pensacola_fact(self, schedule_time=None, immediate=True):
        """Post a random Pensacola fact to social media"""
        print("📱 Posting Pensacola fact...")

        # Generate fact content
        fact_text = self.generate_pensacola_fact()

        # Select random media
        media = self.select_random_media()

        # Calculate auto-delete time (24 hours from post time)
        if schedule_time:
            delete_time = schedule_time + timedelta(hours=24)
        else:
            delete_time = datetime.now() + timedelta(hours=24)

        # Post to Facebook and Instagram
        result = self.publer.create_post_with_media(
            text=fact_text,
            platforms=['facebook', 'instagram'],
            media_id=media.get('id') if media else None,
            post_type='post',
            schedule_time=schedule_time if not immediate else None,
            immediate=immediate,
            auto_delete_at=delete_time
        )

        if result:
            print(f"✅ Pensacola fact posted successfully!")
            print(f"📱 Content: {fact_text}")
            if media:
                print(f"🎬 Media: {media.get('name', 'Unknown')}")
            print(f"⏰ Auto-delete: 24 hours from post time")
        else:
            print(f"❌ Failed to post Pensacola fact")

        return result

    def select_random_media(self):
        """Select random media from Publer library following naming convention"""
        print("🎬 Selecting random media...")

        # Get video media from Publer
        media_data = self.publer.get_media(page=0, media_types=['video'])
        if not media_data or len(media_data.get('media', [])) == 0:
            print("❌ No media found in Publer library")
            return None

        # Filter media following naming convention: number_**.mp4
        video_pattern = re.compile(r'^\d+_.*\.mp4$')
        videos = []

        for media_item in media_data.get('media', []):
            filename = media_item.get('name', '') or media_item.get('filename', '')
            if video_pattern.match(filename):
                videos.append(media_item)

        if not videos:
            print("❌ No videos found matching naming convention (number_**.mp4)")
            return None

        # Select random video
        selected_video = random.choice(videos)
        print(f"✅ Selected video: {selected_video.get('name', 'Unknown')}")
        return selected_video

    def create_posts(self, content, media, date_str, schedule_time=None, immediate=True):
        """Create and publish posts to Facebook and Instagram"""
        publish_mode = "immediate" if immediate else "scheduled"
        print(f"📱 Creating social media posts ({publish_mode})...")

        # Calculate auto-delete time (24 hours from post time)
        if schedule_time:
            delete_time = schedule_time + timedelta(hours=24)
        else:
            delete_time = datetime.now() + timedelta(hours=24)

        results = {}

        # Social Media Post (Facebook + Instagram feed)
        print("📝 Creating social media post...")
        social_post = self.publer.create_post_with_media(
            text=content['social'],
            platforms=['facebook', 'instagram'],
            media_id=media.get('id') if media else None,
            post_type='post',
            schedule_time=schedule_time if not immediate else None,
            immediate=immediate,
            auto_delete_at=delete_time
        )
        results['social_post'] = social_post

        # Reel Post (Facebook + Instagram reels)
        print("🎥 Creating reel post...")
        reel_post = self.publer.create_post_with_media(
            text=content['reel'],
            platforms=['facebook', 'instagram'],
            media_id=media.get('id') if media else None,
            post_type='reel',
            schedule_time=schedule_time if not immediate else None,
            immediate=immediate,
            auto_delete_at=delete_time
        )
        results['reel_post'] = reel_post

        return results

    def run(self, date_str=None, schedule_time=None, immediate=True):
        """Main automation workflow"""
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')

        publish_mode = "immediate" if immediate else "scheduled"
        schedule_info = f" (scheduled for {schedule_time.strftime('%Y-%m-%d %H:%M')})" if schedule_time else ""
        print(f"🚀 Starting social media automation for {date_str} - {publish_mode} publishing{schedule_info}")

        try:
            # Step 1: Scrape events
            events = self.scrape_events(date_str)

            # Step 2: Generate content
            content = self.generate_social_content(events, date_str)

            # Step 3: Select media
            media = self.select_random_media()

            # Step 4: Create posts
            results = self.create_posts(content, media, date_str, schedule_time, immediate)

            print("\n🎉 Automation completed successfully!")
            print(f"📊 Results summary:")
            print(f"   • Events found: {len(events)}")
            print(f"   • Social post: {'✅' if results.get('social_post') else '❌'}")
            print(f"   • Reel post: {'✅' if results.get('reel_post') else '❌'}")
            print(f"   • Media used: {media.get('name', 'None') if media else 'None'}")
            print(f"   • Publishing: {publish_mode}")
            if schedule_time:
                print(f"   • Scheduled for: {schedule_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"   • Auto-delete: 24 hours from post time")

            return results

        except Exception as e:
            print(f"❌ Automation failed: {e}")
            return None

def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='Automate social media posts with Pensacola events')
    parser.add_argument('--date',
                       default=datetime.now().strftime('%Y-%m-%d'),
                       help='Date to scrape events for (YYYY-MM-DD format, default: today)')
    parser.add_argument('--schedule-time',
                       help='Schedule posts for specific time (YYYY-MM-DD HH:MM format)')
    parser.add_argument('--scheduled', action='store_true',
                       help='Use scheduled publishing (default: immediate publishing)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Generate content but don\'t actually post')
    parser.add_argument('--fact', action='store_true',
                       help='Post a random Pensacola fact instead of event-based content')

    args = parser.parse_args()

    try:
        automation = SocialMediaAutomation()

        # Parse schedule time if provided
        schedule_time = None
        if args.schedule_time:
            try:
                schedule_time = datetime.strptime(args.schedule_time, '%Y-%m-%d %H:%M')
            except ValueError:
                print("❌ Invalid schedule time format. Use YYYY-MM-DD HH:MM (e.g., 2025-09-25 14:30)")
                sys.exit(1)

        # Determine publishing mode
        immediate = not args.scheduled
        if args.schedule_time and immediate:
            print("⚠️  Schedule time provided but immediate publishing selected. Using scheduled publishing.")
            immediate = False

        if args.dry_run:
            print("🧪 DRY RUN MODE - No posts will be published")
            # TODO: Add dry run functionality

        # Handle fact posting mode
        if args.fact:
            result = automation.post_pensacola_fact(schedule_time, immediate)
            if result:
                print("\n✅ Pensacola fact posted successfully!")
            else:
                print("\n❌ Pensacola fact posting failed!")
        else:
            # Standard event-based automation
            results = automation.run(args.date, schedule_time, immediate)
            if results:
                print("\n✅ Social media automation completed successfully!")
            else:
                print("\n❌ Social media automation failed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

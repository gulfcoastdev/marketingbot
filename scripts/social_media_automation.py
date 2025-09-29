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

        prompt = """You are a content assistant. I will provide a JSON containing event data (title, date, location, description, link, metadata).

Your task is to return a JSON object with two keys:

long_post:

Format as a social media caption with:

Header: ✨ What's Happening in Pensacola – [Day, Month] ✨

Group events under: different locations .

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

Example Output:

{
  "long_post": "✨ What’s Happening in Pensacola – Sunday, Sept 21 ✨\n\n**Downtown vibes:**\nSpirits of Seville Quarter Ghost Tour, JEKYLL & HYDE, Pensacola Haunted Walking Tour, Mariachi Herencia de México.\n\n**Beach beats:**\nAdult Roller Hockey Games, Jessie Ritter live at Bounce Beach, Horseshoe Kitty at Bamboo Willie’s, Locals Luau Party.\n\n**Also happening:**\nThree Decembers, Your Luck in Bloom.\n\n📍 For more: Visit Pensacola → https://www.visitpensacola.com/events/?range=1&date-from=2025-09-21&date-to=2025-09-21\n✨ Visiting Pensacola? Stay with us → www.micasa.rentals",
  "short_post": "✨ Pensacola Sunday vibes – Sept 21! Catch JEKYLL & HYDE downtown, Horseshoe Kitty rocking Bamboo Willie’s, and the Locals Luau Party on the beach. 📍 For more: Visit Pensacola → https://www.visitpensacola.com/events/?range=1&date-from=2025-09-21&date-to=2025-09-21 ✨ Visiting Pensacola? Stay with us → www.micasa.rentals"
}

Here's the event data: """ + json.dumps(events_json, indent=2) + """





"""

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
        """Select a random fact from JSON file about Pensacola, Gulf Coast, or Escambia area"""
        print("🧠 Selecting random Pensacola fact from database...")

        try:
            # Load facts from JSON file
            facts_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    'data', 'input', 'fun_facts.json')

            with open(facts_file, 'r', encoding='utf-8') as f:
                facts_data = json.load(f)

            # Select random fact
            fact_entry = random.choice(facts_data)
            fact_text = fact_entry['text']
            json_hashtags = fact_entry.get('hashtags', [])

            # Add engaging emojis based on content keywords
            emojis = ""
            fact_lower = fact_text.lower()
            if any(word in fact_lower for word in ['navy', 'naval', 'aviation', 'blue angels']):
                emojis = "✈️ "
            elif any(word in fact_lower for word in ['beach', 'sand', 'coast', 'water', 'gulf']):
                emojis = "🏖️ "
            elif any(word in fact_lower for word in ['pirate', 'spanish', 'history', 'settlement']):
                emojis = "🏴‍☠️ "
            elif any(word in fact_lower for word in ['flags', 'five']):
                emojis = "🏳️ "
            else:
                emojis = "🌟 "

            # Format the fact with emojis
            formatted_fact = f"{emojis}Did you know? {fact_text}"

            # Combine JSON hashtags with all MiCasa hashtags
            micasa_hashtags = ["#MiCasaRentals", "#PensacolaBeachRental", "#FloridaVacation",
                             "#Pensacola", "#FurnishedRental", "#GulfCoastGetaway",
                             "#SnowbirdSeason", "#VisitPensacola", "#BeachLife", "#VacationHome"]

            # Add 2 JSON hashtags + all 10 MiCasa hashtags = max 12 hashtags
            selected_json_hashtags = json_hashtags[:2] if json_hashtags else []
            all_hashtags = selected_json_hashtags + micasa_hashtags
            hashtag_string = " ".join(all_hashtags)

            full_fact = f"{formatted_fact}\n\n{hashtag_string}"

            print(f"✅ Selected fact: {formatted_fact[:100]}...")
            print(f"📝 Combined hashtags: {len(json_hashtags)} from JSON + {len(micasa_hashtags)} MiCasa")
            return full_fact

        except Exception as e:
            print(f"❌ Error loading fact from JSON: {e}")
            # Fallback fact with all MiCasa hashtags
            fallback_hashtags = "#MiCasaRentals #PensacolaBeachRental #FloridaVacation #Pensacola #FurnishedRental #GulfCoastGetaway #SnowbirdSeason #VisitPensacola #BeachLife #VacationHome"
            return f"🏖️ Did you know? Pensacola Beach boasts some of the world's whitest sand beaches, made of pure quartz crystals! ✨\n\n{fallback_hashtags}"

    def post_content(self, content_configs, media, schedule_time=None, immediate=True, test_mode=False, location_id=None):
        """
        Unified method to post content to social media platforms

        Args:
            content_configs (list): List of config dicts with keys: 'text', 'platforms', 'post_type', 'name'
            media (dict): Media object from Publer
            schedule_time (datetime): When to schedule (None for immediate)
            immediate (bool): True for immediate publishing
            test_mode (bool): True for 15-minute auto-delete, False for 24-hour auto-delete
            location_id (str): Location ID to add to posts (None for no location)

        Returns:
            dict: Results for each post type
        """
        # Set auto-delete timing based on mode
        if test_mode:
            auto_delete = {'duration': 15, 'unit': 'Minute'}
        else:
            auto_delete = {'duration': 24, 'unit': 'Hour'}

        # Get default signature for posts (Twitter doesn't support signatures)
        signature_id = self.publer.get_default_signature(['facebook', 'instagram'])

        # Add fallback hashtags if no signature found (all MiCasa hashtags)
        fallback_hashtags = "\n\n#MiCasaRentals #PensacolaBeachRental #FloridaVacation #Pensacola #FurnishedRental #GulfCoastGetaway #SnowbirdSeason #VisitPensacola #BeachLife #VacationHome"

        results = {}

        for config in content_configs:
            text = config['text']
            platforms = config['platforms']
            post_type = config['post_type']
            name = config['name']

            # Add fallback hashtags if no signature, not Twitter-only, and no hashtags already present
            has_hashtags = '#' in text
            if not signature_id and not all(p == 'twitter' for p in platforms) and not has_hashtags:
                text += fallback_hashtags

            print(f"📝 Creating {name}...")
            result = self.publer.create_post_with_media(
                text=text,
                platforms=platforms,
                media_id=media.get('id') if media else None,
                post_type=post_type,
                schedule_time=schedule_time if not immediate else None,
                immediate=immediate,
                auto_delete=auto_delete,
                signature_id=signature_id if 'twitter' not in platforms else None,
                location_id=location_id
            )
            results[name.lower().replace(' ', '_')] = result

        return results

    def post_pensacola_fact(self, schedule_time=None, immediate=True, test_mode=False):
        """Post a random Pensacola fact to social media"""
        print("📱 Posting Pensacola fact...")

        # Generate fact content
        fact_text = self.generate_pensacola_fact()

        # Select random media
        media = self.select_random_media()

        # Add fallback hashtags if no signature found
        signature_id = self.publer.get_default_signature(['facebook', 'instagram'])
        if not signature_id:
            print("📝 No signature found, adding fallback hashtags...")

        # Create content configuration for unified posting
        content_configs = [
            {
                'text': fact_text,
                'platforms': ['facebook', 'instagram', 'twitter'],
                'post_type': 'post',
                'name': 'fact post'
            }
        ]

        # Use unified posting method with Pensacola location
        # Note: Instagram works with 109316785761748, but Facebook may need a different ID
        pensacola_location_id = "109316785761748"  # Generic Pensacola, FL location
        results = self.post_content(content_configs, media, schedule_time, immediate, test_mode, pensacola_location_id)
        result = results.get('fact_post')

        if result:
            delete_timing = "15 minutes" if test_mode else "24 hours"
            print(f"✅ Pensacola fact posted successfully!")
            print(f"📱 Content: {fact_text}")
            if media:
                print(f"🎬 Media: {media.get('name', 'Unknown')}")
            print(f"⏰ Auto-delete: {delete_timing} from post time")
        else:
            print(f"❌ Failed to post Pensacola fact")

        return result

    def select_random_media(self):
        """Select random media from Publer library following naming convention (with pagination)"""
        print("🎬 Selecting random media...")

        # Use the improved paginated method from publer_poster
        selected_video = self.publer.select_random_branded_video()

        if selected_video:
            print(f"✅ Selected video: {selected_video.get('name', 'Unknown')}")
            return selected_video
        else:
            print("❌ No branded videos found matching naming convention (number_**.mp4)")
            return None

    def post_daily_events(self, content, media, date_str, schedule_time=None, immediate=True, test_mode=False):
        """Create and publish daily events posts to Facebook, Instagram, and Twitter"""
        publish_mode = "immediate" if immediate else "scheduled"
        print(f"📱 Creating social media posts ({publish_mode})...")

        # Create content configurations for unified posting
        content_configs = [
            {
                'text': content['social'],
                'platforms': ['facebook', 'instagram'],
                'post_type': 'post',
                'name': 'social post'
            },
            {
                'text': content['social'],  # Use social content for Twitter
                'platforms': ['twitter'],
                'post_type': 'post',
                'name': 'twitter post'
            },
            {
                'text': content['reel'],
                'platforms': ['facebook', 'instagram'],
                'post_type': 'reel',
                'name': 'reel post'
            }
        ]

        # Use unified posting method with Pensacola location
        # Note: Instagram works with 109316785761748, but Facebook may need a different ID
        pensacola_location_id = "109316785761748"  # Generic Pensacola, FL location
        results = self.post_content(content_configs, media, schedule_time, immediate, test_mode, pensacola_location_id)

        return results

    def run(self, date_str=None, schedule_time=None, immediate=True, test_mode=False):
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

            # Step 4: Post daily events
            results = self.post_daily_events(content, media, date_str, schedule_time, immediate, test_mode)

            delete_timing = "15 minutes" if test_mode else "24 hours"
            print("\n🎉 Automation completed successfully!")
            print(f"📊 Results summary:")
            print(f"   • Events found: {len(events)}")
            print(f"   • Social post (FB+IG): {'✅' if results.get('social_post') else '❌'}")
            print(f"   • Twitter post: {'✅' if results.get('twitter_post') else '❌'}")
            print(f"   • Reel post (FB+IG): {'✅' if results.get('reel_post') else '❌'}")
            print(f"   • Media used: {media.get('name', 'None') if media else 'None'}")
            print(f"   • Publishing: {publish_mode}")
            if schedule_time:
                print(f"   • Scheduled for: {schedule_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"   • Auto-delete: {delete_timing} from post time")

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
    parser.add_argument('--test', action='store_true',
                       help='Test mode - auto-delete posts after 15 minutes instead of 24 hours')
    parser.add_argument('--schedule-date',
                       help='Schedule posts for specific date (YYYY-MM-DD format)')
    parser.add_argument('--schedule-hour', type=int, default=9,
                       help='Hour to schedule posts (0-23, default: 9 for 9 AM)')

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
        elif args.schedule_date:
            try:
                # Parse date and combine with hour
                schedule_date = datetime.strptime(args.schedule_date, '%Y-%m-%d')
                schedule_time = schedule_date.replace(hour=args.schedule_hour, minute=0, second=0)
                print(f"📅 Scheduling posts for: {schedule_time.strftime('%Y-%m-%d at %H:%M')}")
            except ValueError:
                print("❌ Invalid schedule date format. Use YYYY-MM-DD (e.g., 2025-09-25)")
                sys.exit(1)

        # Determine publishing mode
        immediate = not args.scheduled and not args.schedule_date
        if (args.schedule_time or args.schedule_date) and immediate:
            print("⚠️  Schedule time/date provided. Using scheduled publishing.")
            immediate = False

        if args.dry_run:
            print("🧪 DRY RUN MODE - No posts will be published")
            # TODO: Add dry run functionality

        # Handle fact posting mode
        if args.fact:
            result = automation.post_pensacola_fact(schedule_time, immediate, args.test)
            if result:
                print("\n✅ Pensacola fact posted successfully!")
            else:
                print("\n❌ Pensacola fact posting failed!")
        else:
            # Standard event-based automation
            results = automation.run(args.date, schedule_time, immediate, args.test)
            if results:
                print("\n✅ Social media automation completed successfully!")
            else:
                print("\n❌ Social media automation failed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

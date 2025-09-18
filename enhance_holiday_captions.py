#!/usr/bin/env python3
"""
Enhance holidays_simplified.json with AI-generated holiday greetings and catchphrases
using OpenAI API to add:
- holiday_text: Quick holiday greeting
- catchphrase: Short, tactful brand tie-in for MiCasa.Rentals
"""

import json
import openai
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HolidayCaptionEnhancer:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = openai.OpenAI(api_key=self.api_key)
        self.processed_count = 0
        self.total_count = 0

    def generate_holiday_enhancements(self, holiday_name, date):
        """Generate holiday greeting and catchphrase using OpenAI"""
        prompt = f"""
You are a marketing copywriter for MiCasa.Rentals, a Pensacola, FL vacation rental company with 12 furnished short-term and long-term rental properties.

For the holiday "{holiday_name}" on {date}, create:

1. holiday_text: A brief, warm holiday greeting (under 70 characters, no emoticons/emojis). Examples:
   - "Happy Halloween"
   - "Celebrating International Women's Day"
   - "Wishing you a peaceful World Mental Health Day"

2. catchphrase: A short, tactful brand tie-in for MiCasa.Rentals (under 70 characters, no emoticons/emojis). Should feel natural, not pushy. Examples:
   - "Your home away from home in beautiful Pensacola awaits"
   - "Comfort meets convenience in our furnished Pensacola rentals"
   - "Experience Pensacola like a local with MiCasa.Rentals"

IMPORTANT: Do not use any emoticons, emojis, or special characters. Keep text professional and under 70 characters each.

Respond in valid JSON format:
{{
  "holiday_text": "Brief greeting here",
  "catchphrase": "Tactful brand tie-in here"
}}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert marketing copywriter specializing in vacation rental marketing."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON response
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # Try to extract from code blocks if AI wrapped in ```json
                if "```json" in content:
                    json_part = content.split("```json")[1].split("```")[0].strip()
                    result = json.loads(json_part)
                    return result
                else:
                    print(f"⚠️ Could not parse JSON for {holiday_name}")
                    return None

        except Exception as e:
            print(f"❌ Error generating content for {holiday_name}: {e}")
            return None

    def enhance_holidays_file(self, input_file="holidays_simplified.json", output_file="holidays_enhanced.json"):
        """Process all holidays and add enhanced captions"""

        # Load existing data
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                holidays = json.load(f)
        except FileNotFoundError:
            print(f"❌ File not found: {input_file}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            return False

        self.total_count = len(holidays)
        print(f"📋 Processing {self.total_count} holidays...")

        enhanced_holidays = []

        for i, holiday in enumerate(holidays, 1):
            holiday_name = holiday.get('selected_holiday', 'Unknown Holiday')
            date = holiday.get('date', 'Unknown Date')

            print(f"\n[{i}/{self.total_count}] Processing: {holiday_name} ({date})")

            # Check if already enhanced
            if 'holiday_text' in holiday and 'catchphrase' in holiday:
                print(f"  ✅ Already enhanced, skipping...")
                enhanced_holidays.append(holiday)
                continue

            # Generate enhancements
            enhancements = self.generate_holiday_enhancements(holiday_name, date)

            if enhancements:
                # Add new fields to existing holiday data
                enhanced_holiday = holiday.copy()
                enhanced_holiday['holiday_text'] = enhancements.get('holiday_text', '')
                enhanced_holiday['catchphrase'] = enhancements.get('catchphrase', '')

                enhanced_holidays.append(enhanced_holiday)
                self.processed_count += 1

                print(f"  ✅ Holiday text: {enhancements.get('holiday_text', '')}")
                print(f"  ✅ Catchphrase: {enhancements.get('catchphrase', '')}")

                # Save progress incrementally every 5 entries
                if i % 5 == 0:
                    self.save_progress(enhanced_holidays, output_file)
                    print(f"  💾 Progress saved ({i}/{self.total_count})")

                # Rate limiting - be respectful to API
                time.sleep(1)
            else:
                print(f"  ❌ Failed to generate enhancements")
                # Keep original data even if enhancement failed
                enhanced_holidays.append(holiday)

        # Final save
        self.save_progress(enhanced_holidays, output_file)

        print(f"\n🎉 Enhancement complete!")
        print(f"  • Total holidays: {self.total_count}")
        print(f"  • Successfully enhanced: {self.processed_count}")
        print(f"  • Output saved: {output_file}")

        return True

    def save_progress(self, data, output_file):
        """Save current progress to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving progress: {e}")

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Enhance holiday data with AI-generated greetings and catchphrases')
    parser.add_argument('--input', default='holidays_simplified.json', help='Input JSON file')
    parser.add_argument('--output', default='holidays_enhanced.json', help='Output JSON file')

    args = parser.parse_args()

    # Validate input file exists
    if not os.path.exists(args.input):
        print(f"❌ Input file not found: {args.input}")
        return

    # Initialize enhancer
    try:
        enhancer = HolidayCaptionEnhancer()
    except ValueError as e:
        print(f"❌ {e}")
        print("💡 Make sure OPENAI_API_KEY is set in your .env file")
        return

    # Process holidays
    success = enhancer.enhance_holidays_file(args.input, args.output)

    if success:
        print(f"\n✅ Enhancement completed successfully!")
        print(f"📄 Enhanced data saved to: {args.output}")
    else:
        print(f"\n❌ Enhancement failed")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Generate event images from scraped Pensacola events data
"""

import sys
sys.path.append('.')

import json
from holiday_image_generator import HolidayImageGenerator
from datetime import datetime
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EventImageGenerator:
    def __init__(self):
        self.generator = HolidayImageGenerator()
        self.events_output_file = "data/output/events_images_output.json"
        
    def load_events(self, filename="data/input/pensacola_events.json", limit=5):
        """Load events from scraped data, limit to first N events"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            # Take first N events and convert to holiday format
            limited_events = events[:limit] if limit else events
            
            logger.info(f"Loaded {len(limited_events)} events from {filename}")
            return limited_events
            
        except Exception as e:
            logger.error(f"Error loading events: {e}")
            return []
    
    def convert_event_to_holiday_format(self, event):
        """Convert scraped event to holiday format for processing"""
        return {
            "name": event.get('title', 'Unknown Event'),
            "date": event.get('date', ''),
            "description": event.get('description', ''),
            "country": "US",
            "type": "local_event",
            "location": event.get('location', ''),
            "time": event.get('time', ''),
            "original_link": event.get('link', ''),
            "source": event.get('source', 'Visit Pensacola')
        }
    
    def check_existing_content(self):
        """Check what content has already been generated"""
        if Path(self.events_output_file).exists():
            try:
                with open(self.events_output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data.get('events_by_date', {})
            except:
                return {}
        return {}
    
    def save_events_output(self, events_data):
        """Save events output to JSON file"""
        output_data = {
            "generated_at": datetime.now().isoformat(),
            "total_events": len(events_data),
            "events_by_date": events_data
        }
        
        with open(self.events_output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Events output saved: {self.events_output_file}")
    
    def generate_event_images(self, limit=5):
        """Generate images for events"""
        logger.info(f"🎨 Generating images for first {limit} events")
        
        # Load events
        events = self.load_events(limit=limit)
        if not events:
            logger.error("No events to process")
            return False
        
        # Check existing content
        existing_content = self.check_existing_content()
        
        events_data = {}
        processed_count = 0
        skipped_count = 0
        
        for i, event in enumerate(events, 1):
            event_date = event.get('date', '')
            event_title = event.get('title', 'Unknown')
            
            # Create unique key for this event
            event_key = f"{event_date}_{i}"
            
            logger.info(f"Processing event {i}/{len(events)}: {event_title}")
            
            # Check if already generated
            if event_key in existing_content and existing_content[event_key].get('content_ready', False):
                logger.info(f"Content already exists for {event_title}, skipping")
                events_data[event_key] = existing_content[event_key]
                skipped_count += 1
                continue
            
            # Convert to holiday format for processing
            holiday_format = self.convert_event_to_holiday_format(event)
            
            # Create custom prompt for events
            ai_result = self.generate_event_content([holiday_format])
            
            if not ai_result:
                logger.warning(f"Failed to generate content for {event_title}")
                continue
            
            # Generate background image
            safe_name = f"event_{event_date.replace('-', '_')}_{i}"
            background_image_path = self.generator.generate_image_with_dalle(
                ai_result.get('image_prompt', ''),
                safe_name
            )
            
            # Apply watermark
            final_image_path = background_image_path
            if background_image_path:
                final_image_path = self.generator.apply_text_overlays(background_image_path)
            
            # Compile event data
            event_data = {
                "event_key": event_key,
                "original_event": event,
                "selected_title": ai_result.get('selected_holiday', event_title),
                "tone_category": ai_result.get('tone_category', ''),
                "caption": ai_result.get('caption', ''),
                "image_prompt": ai_result.get('image_prompt', ''),
                "background_image_path": background_image_path,
                "final_image_path": final_image_path,
                "generated_at": datetime.now().isoformat(),
                "content_ready": bool(ai_result.get('image_prompt') and final_image_path)
            }
            
            events_data[event_key] = event_data
            processed_count += 1
            logger.info(f"✅ Successfully processed: {event_title}")
            
            # Save incrementally
            self.save_events_output(events_data)
        
        logger.info(f"Processing complete: {processed_count} processed, {skipped_count} skipped")
        return True
    
    def generate_event_content(self, event_list):
        """Generate AI content for events using modified prompt"""
        try:
            event_array = []
            for event in event_list:
                event_array.append({
                    "name": event.get('name', 'Unknown Event'),
                    "country": event.get('country', 'US'),
                    "type": "local_event",
                    "location": event.get('location', ''),
                    "description": event.get('description', '')
                })
            
            system_prompt = """
You are a content assistant for local Pensacola events.
You are given a JSON array of local events.

Your task:
1. Pick the most engaging event (usually the first/main one).
2. Classify into a tone category:
   - Playful → fun, casual events like festivals, parties, entertainment
   - Festive → celebrations, cultural events, community gatherings  
   - Respectful → educational, memorial, serious community events
3. Write a short, engaging caption for social media.
4. Write a background image generation prompt for Instagram.

The image prompt must:
- Match the tone category and event theme
- Be styled for Instagram (square format)
- Focus on Pensacola's coastal atmosphere when relevant
- Include elements that represent the event type
- Use natural, authentic visuals - not overly artificial
- Exclude all text, captions, logos, watermarks from the image

Return JSON with these keys:
- "selected_holiday" (the event name)
- "tone_category" 
- "caption"
- "image_prompt"
"""
            
            user_prompt = f"Local Pensacola events:\n{json.dumps(event_array, indent=2)}"
            
            response = self.generator.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response: {content}")
                return {}
                
        except Exception as e:
            logger.error(f"Error generating event content: {e}")
            return {}

def main():
    """Main function"""
    try:
        generator = EventImageGenerator()
        success = generator.generate_event_images(limit=5)
        
        if success:
            print("\n🎉 Event image generation completed!")
            print("📋 Check assets/images/ folder for generated images")
            print("📄 Check events_images_output.json for complete data")
        else:
            print("❌ Event image generation failed")
            
    except Exception as e:
        logger.error(f"Script failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
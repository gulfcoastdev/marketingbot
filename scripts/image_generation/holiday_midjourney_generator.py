#!/usr/bin/env python3
"""
Holiday Image Generator using Midjourney API
Integrates Midjourney generation with existing holiday workflow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from holiday_image_generator import HolidayImageGenerator
from midjourney_generator import MidjourneyGenerator
from datetime import datetime, timedelta
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HolidayMidjourneyGenerator(HolidayImageGenerator):
    """Holiday generator using Midjourney instead of DALL-E"""
    
    def __init__(self):
        super().__init__()
        self.midjourney = MidjourneyGenerator()
        
    def generate_image_with_midjourney(self, image_prompt, safe_name, animate=False):
        """
        Generate holiday image using Midjourney
        
        Args:
            image_prompt (str): The image generation prompt
            safe_name (str): Safe filename for the image
            animate (bool): Whether to also create an animated version
        
        Returns:
            str: Path to generated image, or None if failed
        """
        try:
            logger.info(f"🎨 Generating Midjourney image for: {safe_name}")
            
            # Enhance prompt for Instagram/social media format
            enhanced_prompt = f"{image_prompt}, professional social media content, high quality, Instagram ready"
            
            # Generate with Midjourney
            result = self.midjourney.generate_and_animate(
                prompt=enhanced_prompt,
                aspect_ratio="1:1",  # Square for Instagram
                animate=animate,
                motion_strength=3
            )
            
            if result.get('error'):
                logger.error(f"❌ Midjourney generation failed: {result['error']}")
                return None
            
            # Move the file to our expected location
            midjourney_path = result.get('image_path')
            if not midjourney_path:
                logger.error("❌ No image path returned from Midjourney")
                return None
            
            # Create expected filename in our assets/images directory
            expected_path = self.images_dir / f"{safe_name}_background.png"
            
            # Move/copy the file
            import shutil
            shutil.move(midjourney_path, expected_path)
            
            logger.info(f"✅ Midjourney image saved: {expected_path}")
            
            # If animated, also move the video
            if animate and result.get('video_path'):
                video_expected_path = self.images_dir / f"{safe_name}_animated.mp4"
                shutil.move(result['video_path'], video_expected_path)
                logger.info(f"🎬 Animation saved: {video_expected_path}")
            
            return str(expected_path)
            
        except Exception as e:
            logger.error(f"❌ Error in Midjourney generation: {e}")
            return None
    
    def process_holidays_with_midjourney(self, holidays_file="data/input/2025holidays.json", 
                                      output_file="data/output/midjourney_holidays_output.json", 
                                      skip_existing=True, start_date=None, days_ahead=None,
                                      animate_images=False):
        """
        Process holidays using Midjourney for image generation
        
        Args:
            holidays_file (str): Input holidays JSON file
            output_file (str): Output JSON file
            skip_existing (bool): Skip dates that already have content
            start_date (str): Start date (YYYY-MM-DD)
            days_ahead (int): Number of days to process
            animate_images (bool): Whether to also create animations
        
        Returns:
            list: Processed holiday data
        """
        logger.info("🚀 Starting holiday processing with Midjourney")
        
        # Load and filter holidays
        holidays = self.load_holidays(holidays_file)
        if not holidays:
            return []
        
        # Apply date filtering
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_dt = datetime.now()
        
        if days_ahead:
            end_dt = start_dt + timedelta(days=days_ahead)
            holidays = [h for h in holidays 
                       if start_dt <= datetime.strptime(h['date'], '%Y-%m-%d') <= end_dt]
        
        logger.info(f"📅 Processing {len(holidays)} holidays from {start_dt.strftime('%Y-%m-%d')}")
        
        # Group holidays by date
        grouped_holidays = self.group_holidays_by_day(holidays)
        
        # Load existing output
        existing_output = self.load_existing_output(output_file)
        existing_data = existing_output.get('holidays_by_date', {})
        
        processed_results = []
        new_data = {}
        
        for date, holidays_for_date in grouped_holidays.items():
            logger.info(f"📊 Processing {len(holidays_for_date)} holiday(s) for {date}")
            
            # Skip if exists and skip_existing is True
            if skip_existing and date in existing_data and existing_data[date].get('content_ready', False):
                logger.info(f"⏭️ Content already exists for {date}, skipping")
                processed_results.extend(existing_data[date].get('original_holidays', []))
                new_data[date] = existing_data[date]
                continue
            
            # Generate AI content (caption + prompt)
            ai_result = self.generate_image_prompt_and_caption(holidays_for_date)
            if not ai_result:
                logger.warning(f"⚠️ Failed to generate AI content for {date}")
                continue
            
            # Create safe filename
            safe_name = f"holiday_{date.replace('-', '_')}"
            
            # Generate image with Midjourney
            background_image_path = self.generate_image_with_midjourney(
                ai_result.get('image_prompt', ''),
                safe_name,
                animate=animate_images
            )
            
            # Apply watermark/text overlays
            final_image_path = background_image_path
            if background_image_path:
                final_image_path = self.apply_text_overlays(background_image_path)
            
            # Create holiday data entry
            holiday_data = {
                "date": date,
                "original_holidays": holidays_for_date,
                "selected_holiday": ai_result.get('selected_holiday', 'Unknown'),
                "tone_category": ai_result.get('tone_category', ''),
                "caption": ai_result.get('caption', ''),
                "image_prompt": ai_result.get('image_prompt', ''),
                "caption_style": {},
                "branding_style": {},
                "background_image_path": background_image_path,
                "final_image_path": final_image_path,
                "generated_at": datetime.now().isoformat(),
                "content_ready": bool(ai_result.get('image_prompt') and final_image_path),
                "generated_with": "midjourney",
                "animated": animate_images
            }
            
            # Check for animation file
            if animate_images:
                animation_path = self.images_dir / f"{safe_name}_animated.mp4"
                if animation_path.exists():
                    holiday_data["animation_path"] = str(animation_path)
            
            new_data[date] = holiday_data
            processed_results.extend(holidays_for_date)
            
            logger.info(f"✅ Successfully processed {date}")
            
            # Save incrementally
            self.save_complete_output_fixed(new_data, output_file)
            logger.info(f"💾 Saved progress to {output_file}")
        
        logger.info(f"🎉 Processing complete: {len(new_data)} dates processed")
        return processed_results

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate holiday content with Midjourney")
    parser.add_argument('--holidays-file', default='data/input/2025holidays.json', 
                       help='Input holidays JSON file')
    parser.add_argument('--output-file', default='data/output/midjourney_holidays_output.json', 
                       help='Output JSON file')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD), defaults to today')
    parser.add_argument('--days-ahead', type=int, default=30, 
                       help='Number of days ahead to process (default: 30)')
    parser.add_argument('--no-skip-existing', action='store_true', 
                       help='Regenerate existing content')
    parser.add_argument('--animate', action='store_true', 
                       help='Also generate animated versions')
    
    args = parser.parse_args()
    
    try:
        generator = HolidayMidjourneyGenerator()
        
        result = generator.process_holidays_with_midjourney(
            holidays_file=args.holidays_file,
            output_file=args.output_file,
            skip_existing=not args.no_skip_existing,
            start_date=args.start_date,
            days_ahead=args.days_ahead,
            animate_images=args.animate
        )
        
        logger.info(f"🎉 Successfully processed {len(result)} holidays")
        
    except ValueError as e:
        logger.error(f"❌ Setup error: {e}")
        logger.info("💡 Make sure MIDJOURNEY_API_KEY is set in your .env file")
        logger.info("💡 Run: python midjourney_generator.py setup")
    except Exception as e:
        logger.error(f"❌ Processing error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
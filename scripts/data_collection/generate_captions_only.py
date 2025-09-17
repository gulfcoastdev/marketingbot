#!/usr/bin/env python3
"""
Generate captions and prompts ONLY - no images
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'image_generation'))

from holiday_image_generator import HolidayImageGenerator
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_captions_only(start_date, days_ahead):
    """Generate only captions and prompts, no images"""
    generator = HolidayImageGenerator()
    
    # Load holidays
    holidays = generator.load_holidays("../../data/input/2025holidays.json")
    
    # Filter holidays for date range
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = start_dt + timedelta(days=days_ahead)
    
    filtered_holidays = []
    for holiday in holidays:
        holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d')
        if start_dt <= holiday_date <= end_dt:
            filtered_holidays.append(holiday)
    
    # Group by date
    grouped_holidays = generator.group_holidays_by_day(filtered_holidays)
    logger.info(f"Processing {len(grouped_holidays)} dates for captions only")
    
    # Load existing data
    existing_output = generator.load_existing_output("../../data/output/upcoming_holidays_output.json")
    existing_data = existing_output.get('holidays_by_date', {})
    
    new_data = {}
    
    for date, holidays_for_date in grouped_holidays.items():
        logger.info(f"Generating caption for {date}")
        
        # Generate AI content (caption + prompt only)
        ai_result = generator.generate_image_prompt_and_caption(holidays_for_date)
        
        if not ai_result:
            logger.warning(f"Failed to generate content for {date}")
            continue
        
        # Create entry WITHOUT images
        holiday_data = {
            "date": date,
            "original_holidays": holidays_for_date,
            "selected_holiday": ai_result.get('selected_holiday', 'Unknown'),
            "tone_category": ai_result.get('tone_category', ''),
            "caption": ai_result.get('caption', ''),
            "image_prompt": ai_result.get('image_prompt', ''),
            "caption_style": {},
            "branding_style": {},
            "background_image_path": None,  # NO IMAGE
            "final_image_path": None,       # NO IMAGE
            "generated_at": datetime.now().isoformat(),
            "content_ready": False  # Not ready since no image
        }
        
        new_data[date] = holiday_data
        logger.info(f"✅ Generated caption for {date}: {ai_result.get('caption', '')[:50]}...")
    
    # Merge with existing data and save
    merged_data = existing_data.copy()
    merged_data.update(new_data)
    
    generator.save_complete_output_fixed(new_data, "../../data/output/upcoming_holidays_output.json")
    
    logger.info(f"✅ Generated captions for {len(new_data)} dates")
    return new_data

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Generate captions and prompts only - no images')
    parser.add_argument('--start-date', default="2025-09-18", help='Start date (YYYY-MM-DD)')
    parser.add_argument('--days-ahead', type=int, default=16, help='Number of days to process')

    args = parser.parse_args()

    result = generate_captions_only(args.start_date, args.days_ahead)
    print(f"Generated captions for {len(result)} dates")
#!/usr/bin/env python3
"""
Brand holiday videos by matching video files with enhanced holiday data
Videos are matched by date based on filename patterns
"""

import json
import os
import sys
import subprocess
import re
from datetime import datetime

class HolidayVideoBrander:
    def __init__(self, enhanced_data_file="holidays_enhanced.json", video_folder="brandingburner", logo_path="brandingburner/logo.png"):
        self.enhanced_data_file = enhanced_data_file
        self.video_folder = video_folder
        self.logo_path = logo_path
        self.video_processing_script = "scripts/video_processing/add_video_branding.py"

        # Load enhanced holiday data
        self.holiday_data = self.load_holiday_data()
        if not self.holiday_data:
            raise ValueError(f"Could not load holiday data from {enhanced_data_file}")

        # Validate video processing script exists
        if not os.path.exists(self.video_processing_script):
            raise ValueError(f"Video processing script not found: {self.video_processing_script}")

        # Validate logo exists
        if not os.path.exists(self.logo_path):
            raise ValueError(f"Logo file not found: {self.logo_path}")

    def load_holiday_data(self):
        """Load enhanced holiday data"""
        try:
            with open(self.enhanced_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Enhanced data file not found: {self.enhanced_data_file}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            return None

    def parse_video_date(self, filename):
        """Parse date from video filename"""
        # Pattern: DDMM.mp4 (e.g., 1709.mp4 = September 17)
        match = re.match(r'(\d{2})(\d{2})\.mp4$', filename)
        if match:
            day = match.group(1)
            month = match.group(2)
            # Assume 2025 year
            try:
                return f"2025-{month}-{day}"
            except:
                return None
        return None

    def find_video_files(self):
        """Find all video files and extract dates"""
        video_files = []

        if not os.path.exists(self.video_folder):
            print(f"❌ Video folder not found: {self.video_folder}")
            return video_files

        for filename in os.listdir(self.video_folder):
            if filename.endswith('.mp4') and not filename.startswith(('final_', 't1', 'social_')):
                date = self.parse_video_date(filename)
                if date:
                    video_path = os.path.join(self.video_folder, filename)
                    video_files.append({
                        'filename': filename,
                        'path': video_path,
                        'date': date
                    })

        return sorted(video_files, key=lambda x: x['date'])

    def find_holiday_data_for_date(self, date):
        """Find holiday data for a specific date"""
        for holiday in self.holiday_data:
            if holiday.get('date') == date:
                return holiday
        return None

    def brand_video(self, video_info, holiday_data, output_folder="brandingburner/branded"):
        """Brand a single video with holiday data"""
        holiday_text = holiday_data.get('holiday_text', '')
        catchphrase = holiday_data.get('catchphrase', '')

        if not holiday_text or not catchphrase:
            print(f"  ❌ Missing text data for {holiday_data.get('selected_holiday', 'Unknown')}")
            return None

        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # Generate output filename
        date_clean = video_info['date'].replace('-', '_')
        holiday_name_clean = re.sub(r'[^\w\s-]', '', holiday_data.get('selected_holiday', 'holiday')).replace(' ', '_')
        output_filename = f"branded_{date_clean}_{holiday_name_clean}.mp4"
        output_path = os.path.join(output_folder, output_filename)

        # Build command to run video branding script
        cmd = [
            'python3', self.video_processing_script,
            '--input', video_info['path'],
            '--logo', self.logo_path,
            '--text', holiday_text,
            '--promo', catchphrase,
            '--output', output_path
        ]

        print(f"  🎬 Creating: {output_filename}")
        print(f"    Holiday text: \"{holiday_text}\"")
        print(f"    Catchphrase: \"{catchphrase}\"")

        try:
            # Change to the correct directory to run the script
            original_cwd = os.getcwd()

            result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=original_cwd)
            print(f"  ✅ Success: {output_path}")
            return output_path

        except subprocess.CalledProcessError as e:
            print(f"  ❌ Error creating branded video: {e.stderr}")
            return None
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            return None

    def process_all_videos(self):
        """Process all matching videos"""
        print("🎥 Finding video files...")
        video_files = self.find_video_files()

        if not video_files:
            print("❌ No video files found with date patterns")
            return

        print(f"📋 Found {len(video_files)} video files with date patterns")

        processed_count = 0
        matched_count = 0

        for video_info in video_files:
            print(f"\n[{video_files.index(video_info) + 1}/{len(video_files)}] Processing: {video_info['filename']} ({video_info['date']})")

            # Find matching holiday data
            holiday_data = self.find_holiday_data_for_date(video_info['date'])

            if not holiday_data:
                print(f"  ⚠️ No holiday data found for {video_info['date']}")
                continue

            matched_count += 1
            print(f"  🎯 Matched: {holiday_data.get('selected_holiday', 'Unknown Holiday')}")

            # Check if enhanced fields exist
            if not holiday_data.get('holiday_text') or not holiday_data.get('catchphrase'):
                print(f"  ⚠️ Missing enhanced fields (holiday_text/catchphrase)")
                continue

            # Brand the video
            result = self.brand_video(video_info, holiday_data)

            if result:
                processed_count += 1

        print(f"\n🎉 Processing complete!")
        print(f"  • Video files found: {len(video_files)}")
        print(f"  • Matched with holiday data: {matched_count}")
        print(f"  • Successfully branded: {processed_count}")

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Brand holiday videos with enhanced captions')
    parser.add_argument('--data', default='holidays_enhanced.json', help='Enhanced holiday data file')
    parser.add_argument('--videos', default='brandingburner', help='Video folder path')
    parser.add_argument('--logo', default='brandingburner/logo.png', help='Logo file path')
    parser.add_argument('--output', default='brandingburner/branded', help='Output folder for branded videos')

    args = parser.parse_args()

    # Validate enhanced data file exists
    if not os.path.exists(args.data):
        print(f"❌ Enhanced data file not found: {args.data}")
        print("💡 Run enhance_holiday_captions.py first to create the enhanced data")
        return

    try:
        brander = HolidayVideoBrander(args.data, args.videos, args.logo)
        brander.process_all_videos()

    except ValueError as e:
        print(f"❌ {e}")
        return
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return

if __name__ == "__main__":
    main()
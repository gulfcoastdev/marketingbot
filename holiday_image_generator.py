#!/usr/bin/env python3
"""
Holiday Image Generator - Process holidays, generate image prompts and create images with DALL-E
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import logging

import openai
from dotenv import load_dotenv
import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HolidayImageGenerator:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Create directories
        self.images_dir = Path("holiday_images")
        self.data_dir = Path("holiday_data")
        self.images_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
    
    def load_holidays(self, filename="holidays.json"):
        """Load holidays from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                holidays = json.load(f)
            logger.info(f"Loaded {len(holidays)} holidays from {filename}")
            return holidays
        except FileNotFoundError:
            logger.error(f"Holidays file {filename} not found")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing {filename}: {e}")
            return []
    
    def group_holidays_by_day(self, holidays):
        """Group holidays by date"""
        grouped = defaultdict(list)
        
        for holiday in holidays:
            date = holiday.get('date', '')
            if date:
                grouped[date].append(holiday)
        
        logger.info(f"Grouped holidays into {len(grouped)} date groups")
        return dict(grouped)
    
    def generate_image_prompt_and_caption(self, holidays_for_day):
        """
        Generate image prompt and caption using OpenAI
        
        Args:
            holidays_for_day: List of holidays occurring on the same day
        """
        # Convert to the expected format for the prompt
        holiday_array = []
        for holiday in holidays_for_day:
            holiday_array.append({
                "name": holiday.get('name', 'Unknown Holiday'),
                "country": holiday.get('country', 'US'),
                "type": holiday.get('type', 'observance')
            })
        
        system_prompt = """
     You are a content assistant.  
You are given a JSON array of holidays for a specific date.  

Your task:  
1. Pick the most important or engaging holiday.  
   - Prioritize: National public holiday > major cultural/religious holiday > fun/quirky day.  
2. Classify the holiday into a tone category:  
   - Playful → quirky fun days like National Ninja Day, Burger Day.  
   - Festive → cultural/religious holidays like Chanukah, Diwali, Christmas.  
   - Respectful → solemn remembrance days like Veterans Day, Memorial Day, MLK Day.  
3. Write a short caption.  
4. Write a **background image generation prompt** for social media.  

The image prompt must:  
- Match the tone category (Playful / Festive / Respectful).  
- Be styled for Instagram (square format).  
- Focus only on background visuals, colors, atmosphere, composition, and symbolic characters.  
- Designed for virality but in a **natural, authentic way**:  
  - Eye-catching without being overly artificial (avoid over-saturation unless playful).  
  - Use realistic lighting and cinematic depth instead of exaggerated glow.  
  - Maintain balanced color palettes based on tone.  
  - Motion effects, subtle glow, or texture are allowed — but refined.  
- **Holiday symbolism**: May include a person or character that represents the holiday  
  (e.g., ninja for Ninja Day, Santa for Christmas, a family lighting a menorah for Chanukah,  
  soldier silhouettes for Veterans Day).  
- **Explicitly exclude all text, captions, logos, watermarks, or words from the image.**  

Return your response as a JSON object with exactly these keys:  
- "selected_holiday"  
- "tone_category"  
- "caption"  
- "image_prompt"  

"""
        
        user_prompt = f"JSON input:\n{json.dumps(holiday_array, indent=2)}"

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse OpenAI JSON response: {content}")
                return {}
                
        except Exception as e:
            logger.error(f"Error generating prompt and caption: {e}")
            return {}
    
    def generate_image_with_dalle(self, image_prompt, filename_prefix):
        """Generate image using DALL-E"""
        if not image_prompt:
            logger.warning("Empty image prompt, skipping image generation")
            return None
        
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            # Get the image URL
            image_url = response.data[0].url
            
            # Download the image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Save the image
            image_filename = self.images_dir / f"{filename_prefix}.png"
            with open(image_filename, 'wb') as f:
                f.write(image_response.content)
            
            logger.info(f"Image saved: {image_filename}")
            return str(image_filename)
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None
    
    def apply_text_overlays(self, image_path, caption=None, caption_style=None, branding_style=None):
        """Apply caption and branding text overlays to the generated image"""
        if not image_path or not os.path.exists(image_path):
            logger.warning(f"Image not found for text overlay: {image_path}")
            return image_path
        
        try:
            # Open the image
            with Image.open(image_path) as img:
                # Convert to RGBA for transparency support
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Create a transparent overlay for text
                overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(overlay)
                img_width, img_height = img.size
                
                # Only apply subtle branding watermark (no caption)
                branding_text = "Micasa.rentals"
                self.add_watermark_text(draw, branding_text, img_width, img_height)
                
                # Composite the overlay onto the original image
                final_img = Image.alpha_composite(img, overlay)
                
                # Convert back to RGB for saving as PNG
                final_img = final_img.convert('RGB')
                
                # Save the image with overlays
                overlay_path = image_path.replace('.png', '_with_text.png')
                final_img.save(overlay_path, 'PNG', quality=95)
                
                logger.info(f"Text overlays applied: {overlay_path}")
                return overlay_path
                
        except Exception as e:
            logger.error(f"Error applying text overlays: {e}")
            return image_path
    
    def add_text_to_image(self, draw, text, style, img_width, img_height, is_caption=True):
        """Add text to image with specified styling"""
        try:
            # Extract style parameters
            font_name = style.get('font', 'Helvetica')
            size_desc = style.get('size', 'medium')
            position = style.get('position', 'centered')
            color = style.get('color', 'white')
            
            # Convert size description to actual pixels with proper sizing
            if is_caption:
                # Caption font - limit to reasonable size for 20% coverage
                if 'large' in size_desc.lower():
                    font_size = int(img_width * 0.06)  # 6% for captions
                elif 'small' in size_desc.lower():
                    font_size = int(img_width * 0.04)  # 4% for small captions
                else:
                    font_size = int(img_width * 0.05)  # 5% for medium captions
            else:
                # Branding font - always smaller
                font_size = int(img_width * 0.025)  # Always 2.5% for branding
            
            # Enhanced font loading with better detection and fallbacks
            font = self.load_font(font_name, font_size)
            
            # Wrap text with proper margins
            if is_caption:
                # Add margins (10% on each side = 20% total margin, 80% usable width)
                margin = int(img_width * 0.1)
                usable_width = img_width - (2 * margin)
                
                # Calculate characters per line based on usable width and font size
                avg_char_width = font_size * 0.6  # Approximate character width
                max_chars_per_line = int(usable_width / avg_char_width)
                max_chars_per_line = max(15, min(max_chars_per_line, 40))  # Reasonable bounds
                
                wrapped_lines = textwrap.wrap(text, width=max_chars_per_line)
                
                # Limit to maximum 4 lines to stay within 20% height
                if len(wrapped_lines) > 4:
                    wrapped_lines = wrapped_lines[:3] + [wrapped_lines[3] + "..."]
            else:
                wrapped_lines = [text]
            
            # Calculate text positioning
            total_text_height = len(wrapped_lines) * font_size * 1.2
            
            if position == 'centered' or position == 'center':
                start_y = (img_height - total_text_height) // 2
            elif 'bottom' in position:
                start_y = img_height - total_text_height - (font_size // 2)
            elif 'top' in position:
                start_y = font_size // 2
            else:
                start_y = (img_height - total_text_height) // 2
            
            # Draw each line of text
            for i, line in enumerate(wrapped_lines):
                # Get text dimensions
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                
                if is_caption:
                    # For captions, respect margins
                    margin = int(img_width * 0.1)
                    if 'right' in position:
                        x = img_width - margin - text_width
                    elif 'left' in position:
                        x = margin
                    else:
                        x = (img_width - text_width) // 2
                else:
                    # For branding, use smaller margins
                    small_margin = font_size // 2
                    if 'right' in position:
                        x = img_width - text_width - small_margin
                    elif 'left' in position:
                        x = small_margin
                    else:
                        x = (img_width - text_width) // 2
                
                y = start_y + (i * font_size * 1.2)
                
                # Create smaller, refined text outline for cleaner look
                outline_width = max(3, font_size // 15)  # Smaller border proportional to font size
                
                # Force high contrast: white text with black border for maximum readability
                text_color = (255, 255, 255)  # Always white text
                outline_color = (0, 0, 0, 255)  # Always black outline
                
                # Draw thick outline in multiple directions for clean border effect
                for adj_x in range(-outline_width, outline_width + 1):
                    for adj_y in range(-outline_width, outline_width + 1):
                        if adj_x != 0 or adj_y != 0:  # Don't draw on center position
                            draw.text((x + adj_x, y + adj_y), line, font=font, fill=outline_color)
                
                # Draw main text on top
                draw.text((x, y), line, font=font, fill=text_color)
                
        except Exception as e:
            logger.error(f"Error adding text '{text}': {e}")
    
    def add_watermark_text(self, draw, text, img_width, img_height):
        """Add subtle transparent watermark text"""
        try:
            # Watermark styling - small, transparent, bottom-right
            font_size = int(img_width * 0.02)  # 2% of image width - very small
            
            # Load clean, professional font for watermark
            font = self.load_font("Arial", font_size)
            
            # Less transparent white text for better visibility
            watermark_color = (255, 255, 255, 150)  # White with 60% opacity
            
            # Position in bottom-right with small margin
            margin = int(img_width * 0.02)  # 2% margin
            
            # Get text dimensions
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Position coordinates
            x = img_width - text_width - margin
            y = img_height - text_height - margin
            
            # Draw transparent text (no outline needed - very subtle)
            draw.text((x, y), text, font=font, fill=watermark_color)
            
            logger.info(f"Applied subtle watermark: {text}")
            
        except Exception as e:
            logger.error(f"Error adding watermark '{text}': {e}")
    
    def load_font(self, font_name, font_size):
        """Enhanced font loading with better detection and fallbacks"""
        try:
            # Normalize font name
            font_name_clean = font_name.strip()
            
            # Font family mappings for better fallbacks
            font_families = {
                'comic sans': ['ComicSansMS', 'Comic Sans MS', 'ComicSans', 'Chalkduster', 'Marker Felt'],
                'comic sans ms': ['ComicSansMS', 'Comic Sans MS', 'ComicSans', 'Chalkduster', 'Marker Felt'],
                'arial': ['Arial', 'ArialMT', 'Helvetica', 'HelveticaNeue'],
                'helvetica': ['Helvetica', 'HelveticaNeue', 'Arial', 'ArialMT'],
                'times': ['TimesNewRomanPSMT', 'Times New Roman', 'Times', 'Georgia'],
                'times new roman': ['TimesNewRomanPSMT', 'Times New Roman', 'Times', 'Georgia'],
                'montserrat': ['Montserrat', 'HelveticaNeue', 'Helvetica', 'Arial'],
                'open sans': ['OpenSans', 'HelveticaNeue', 'Helvetica', 'Arial'],
                'roboto': ['Roboto', 'HelveticaNeue', 'Helvetica', 'Arial'],
                'georgia': ['Georgia', 'TimesNewRomanPSMT', 'Times'],
                'verdana': ['Verdana', 'Arial', 'Helvetica'],
                'trebuchet': ['TrebuchetMS', 'Trebuchet MS', 'Arial', 'Helvetica'],
                'impact': ['Impact', 'Arial Black', 'ArialMT'],
                'courier': ['CourierNewPSMT', 'Courier New', 'Courier', 'Monaco']
            }
            
            # Get font candidates (original + fallbacks)
            font_candidates = [font_name_clean]
            font_key = font_name_clean.lower().strip()
            
            if font_key in font_families:
                font_candidates.extend(font_families[font_key])
            else:
                # Add generic fallbacks based on font characteristics
                if any(word in font_key for word in ['sans', 'helvetica', 'arial']):
                    font_candidates.extend(['Arial', 'Helvetica', 'HelveticaNeue'])
                elif any(word in font_key for word in ['serif', 'times', 'georgia']):
                    font_candidates.extend(['Georgia', 'TimesNewRomanPSMT', 'Times'])
                elif any(word in font_key for word in ['mono', 'courier', 'code']):
                    font_candidates.extend(['CourierNewPSMT', 'Monaco', 'Courier'])
                else:
                    # Default fallbacks
                    font_candidates.extend(['Arial', 'Helvetica', 'Georgia'])
            
            # Try to load fonts in order of preference
            for candidate in font_candidates:
                font_paths = self.get_font_paths(candidate)
                
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        try:
                            font = ImageFont.truetype(font_path, font_size)
                            if candidate != font_name_clean:
                                logger.info(f"Using fallback font '{candidate}' for '{font_name_clean}'")
                            else:
                                logger.info(f"Successfully loaded font '{font_name_clean}'")
                            return font
                        except Exception as e:
                            logger.debug(f"Failed to load {font_path}: {e}")
                            continue
            
            # Final fallback to system default
            logger.warning(f"Could not load '{font_name_clean}' or any fallbacks, using system default")
            return ImageFont.load_default()
            
        except Exception as e:
            logger.error(f"Error in font loading: {e}")
            return ImageFont.load_default()
    
    def get_font_paths(self, font_name):
        """Get possible font file paths for a given font name"""
        # Clean font name variations
        name_clean = font_name.replace(' ', '')
        name_with_spaces = font_name
        
        # Common font extensions and variations
        extensions = ['.ttc', '.ttf', '.otf']
        weight_variations = ['', '-Regular', '-Bold', '-Medium', 'MT', 'PS']
        
        paths = []
        
        # macOS system font locations
        system_dirs = [
            '/System/Library/Fonts/',
            '/Library/Fonts/',
            '/System/Library/Fonts/Helvetica.ttc',  # Special case for Helvetica
            '/System/Library/Fonts/Arial.ttf',      # Special case for Arial
        ]
        
        for base_dir in system_dirs:
            if base_dir.endswith(('.ttc', '.ttf', '.otf')):
                # Direct font file paths
                paths.append(base_dir)
                continue
                
            # Generate possible font file names
            for ext in extensions:
                for variation in weight_variations:
                    # Try different naming conventions
                    possible_names = [
                        f"{name_clean}{variation}{ext}",
                        f"{name_with_spaces}{variation}{ext}",
                        f"{name_clean.lower()}{variation.lower()}{ext}",
                    ]
                    
                    for name in possible_names:
                        paths.append(os.path.join(base_dir, name))
        
        # Add some specific known font paths for common fonts
        specific_paths = {
            'arial': ['/System/Library/Fonts/Arial.ttf'],
            'helvetica': ['/System/Library/Fonts/Helvetica.ttc'],
            'times': ['/System/Library/Fonts/Times.ttc'],
            'georgia': ['/System/Library/Fonts/Georgia.ttf'],
            'verdana': ['/System/Library/Fonts/Verdana.ttf'],
            'trebuchetms': ['/System/Library/Fonts/Trebuchet MS.ttf'],
            'impact': ['/System/Library/Fonts/Impact.ttf'],
            'comicsansms': ['/Library/Fonts/Comic Sans MS.ttf', '/System/Library/Fonts/ComicSansMS.ttf'],
        }
        
        font_key = font_name.lower().replace(' ', '').replace('-', '')
        if font_key in specific_paths:
            paths.extend(specific_paths[font_key])
        
        return paths
    
    def parse_color(self, color_desc, is_caption=True):
        """Parse color description to RGB tuple with smart defaults"""
        color_map = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'gold': (255, 215, 0),
            'golden': (255, 215, 0),
            'golden-yellow': (255, 223, 0),
            'yellow': (255, 255, 0),
            'blue': (100, 150, 255),
            'red': (255, 80, 80),
            'green': (80, 255, 80),
            'orange': (255, 165, 0),
            'purple': (200, 100, 255)
        }
        
        # Look for known colors in description
        for color_name, rgb in color_map.items():
            if color_name in color_desc.lower():
                # For captions, ensure high contrast colors
                if is_caption:
                    if color_name in ['blue', 'purple', 'green'] and 'dark' not in color_desc.lower():
                        # Make darker colors lighter for better visibility
                        return tuple(min(255, c + 50) for c in rgb)
                return rgb
        
        # Smart defaults based on text type
        if is_caption:
            return (255, 255, 255)  # White for captions (high contrast)
        else:
            return (255, 215, 0)    # Gold for branding (premium look)
    
    def load_existing_output(self, output_file="holiday_output.json"):
        """Load existing output file"""
        if Path(output_file).exists():
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_complete_output(self, all_data, output_file="holiday_output.json"):
        """Save complete output to single JSON file"""
        output_data = {
            "generated_at": datetime.now().isoformat(),
            "total_dates": len(all_data),
            "holidays_by_date": all_data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Complete output saved: {output_file}")
        return output_file
    
    def filter_holidays_by_date_range(self, holidays, start_date=None, days_ahead=None):
        """Filter holidays by date range"""
        if start_date is None:
            start_date = datetime.now()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d') if isinstance(start_date, str) else start_date
        
        if days_ahead is None:
            days_ahead = 75
            
        end_date = start_date + timedelta(days=days_ahead)
        
        filtered_holidays = []
        for holiday in holidays:
            holiday_date_str = holiday.get('date', '')
            if holiday_date_str:
                try:
                    holiday_date = datetime.strptime(holiday_date_str, '%Y-%m-%d')
                    if start_date <= holiday_date <= end_date:
                        filtered_holidays.append(holiday)
                except ValueError:
                    continue
        
        logger.info(f"Filtered {len(holidays)} holidays to {len(filtered_holidays)} within date range {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        return filtered_holidays
    
    def process_holidays(self, holidays_file="holidays.json", output_file="holiday_output.json", skip_existing=True, start_date=None, days_ahead=None):
        """Process holidays within date range and generate content"""
        holidays = self.load_holidays(holidays_file)
        if not holidays:
            logger.error("No holidays to process")
            return
        
        # Filter holidays by date range if specified
        if start_date or days_ahead:
            holidays = self.filter_holidays_by_date_range(holidays, start_date, days_ahead)
        
        # Group by date
        grouped_holidays = self.group_holidays_by_day(holidays)
        
        # Load existing output if it exists
        existing_output = self.load_existing_output(output_file) if skip_existing else {}
        existing_data = existing_output.get('holidays_by_date', {})
        
        all_data = {}
        processed_count = 0
        skipped_count = 0
        
        for date, day_holidays in grouped_holidays.items():
            logger.info(f"Processing {len(day_holidays)} holiday(s) for {date}")
            
            # Check if content already exists
            if skip_existing and date in existing_data and existing_data[date].get('content_ready', False):
                logger.info(f"Content already exists for {date}, skipping")
                all_data[date] = existing_data[date]
                skipped_count += 1
                continue
            
            # Generate prompt and caption using OpenAI
            ai_result = self.generate_image_prompt_and_caption(day_holidays)
            
            if not ai_result:
                logger.warning(f"Failed to generate content for {date}")
                continue
            
            # Generate background image
            safe_date = date.replace('-', '_')
            background_image_path = self.generate_image_with_dalle(
                ai_result.get('image_prompt', ''), 
                f"holiday_{safe_date}_background"
            )
            
            # Apply watermark overlay (no caption text)
            final_image_path = background_image_path
            if background_image_path:
                final_image_path = self.apply_text_overlays(
                    background_image_path,
                    None,  # No caption
                    {},    # No caption style needed
                    {}     # No branding style needed
                )
            
            # Compile data for this date
            date_data = {
                "date": date,
                "original_holidays": day_holidays,
                "selected_holiday": ai_result.get('selected_holiday', ''),
                "tone_category": ai_result.get('tone_category', ''),
                "caption": ai_result.get('caption', ''),
                "image_prompt": ai_result.get('image_prompt', ''),
                "caption_style": ai_result.get('caption_style', {}),
                "branding_style": ai_result.get('branding_style', {}),
                "background_image_path": background_image_path,
                "final_image_path": final_image_path,
                "generated_at": datetime.now().isoformat(),
                "content_ready": bool(ai_result.get('image_prompt') and ai_result.get('caption') and final_image_path)
            }
            
            all_data[date] = date_data
            processed_count += 1
            logger.info(f"Successfully processed {date}")
            
            # Save output incrementally after each processed holiday
            self.save_complete_output(all_data, output_file)
            logger.info(f"💾 Saved progress to {output_file}")
        
        # Final save (in case we have existing data that wasn't processed)
        if existing_data:
            # Merge existing data that wasn't reprocessed
            for existing_date, existing_data_item in existing_data.items():
                if existing_date not in all_data:
                    all_data[existing_date] = existing_data_item
        
        self.save_complete_output(all_data, output_file)
        
        logger.info(f"Processing complete: {processed_count} processed, {skipped_count} skipped")
        return all_data

def main():
    parser = argparse.ArgumentParser(description='Generate holiday marketing content with images')
    parser.add_argument('--holidays-file', default='2025holidays.json', help='Input holidays JSON file')
    parser.add_argument('--output-file', default='holiday_output.json', help='Output JSON file')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD), defaults to today')
    parser.add_argument('--days-ahead', type=int, default=75, help='Number of days ahead to process (default: 75)')
    parser.add_argument('--no-skip-existing', action='store_true', help='Regenerate existing content')
    
    args = parser.parse_args()
    
    try:
        generator = HolidayImageGenerator()
        result = generator.process_holidays(
            holidays_file=args.holidays_file,
            output_file=args.output_file,
            skip_existing=not args.no_skip_existing,
            start_date=args.start_date,
            days_ahead=args.days_ahead
        )
        
        if result:
            logger.info(f"✅ Successfully generated content, saved to {args.output_file}")
        else:
            logger.warning("⚠️ No content generated")
            
    except Exception as e:
        logger.error(f"Script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

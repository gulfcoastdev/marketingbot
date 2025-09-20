# Marketing Bot - Project Structure

## Root Directory
- `daily_events_scraper.py` - Main events scraper with JSON output
- `CLAUDE.md` - Project instructions and documentation
- `requirements.txt` - Python dependencies
- `.env` / `.env.example` - Environment variables

## Key Directories

### `/scripts/`
- `publer/` - Publer API integration for social media posting
- `video_processing/` - Video branding and processing tools

### `/data/`
- Input and output data files
- Holiday JSON files
- Event scraping results

### `/assets/`
- Generated images and media files

### `/brandingburner/`
- Video processing workspace
- Branded videos and logos

### `/pensacola_scraper_env/`
- Python virtual environment

### `/tests/`
- Unit tests and test files

## Archived Items

### `/old_scripts/`
- `brand_holiday_videos.py` - Legacy holiday video generator
- `enhance_holiday_captions.py` - Caption enhancement tool
- `update_image_prompts.py` - Image prompt updater

### `/old_data/`
- Legacy JSON data files
- Test data and debugging files

### `/archive/`
- Old README files
- Command reference files
- Deprecated documentation

## Current Active Scripts
1. **Events Scraper**: `daily_events_scraper.py`
2. **Publer API**: `scripts/publer/publer_poster.py`
3. **Video Branding**: `scripts/video_processing/add_video_branding.py`
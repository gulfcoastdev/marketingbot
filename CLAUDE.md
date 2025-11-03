# Marketing Bot - Claude Instructions

## Project Overview
This marketing bot generates holiday images and marketing content, and scrapes Pensacola events for promotional content.

## Environment Setup

### 1. Virtual Environment
Always activate the virtual environment before running any scripts:
```bash
source pensacola_scraper_env/bin/activate
```

### 2. Environment Variables
Ensure `.env` file exists in the project root with required API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Python Version
Use Python 3 for all scripts:
```bash
python3 script_name.py
```

## Main Scripts

### Holiday Image Generator (`holiday_image_generator.py`)
**Primary script for generating holiday marketing images and content**

#### Features:
- Generates AI-powered holiday images using DALL-E
- Creates marketing captions and content
- Supports flexible date ranges
- Skips existing content to prevent regeneration
- Saves progress incrementally to prevent data loss
- Outputs images to `assets/images/` folder

#### Usage:
```bash
# Generate content for next 75 days (default)
python3 holiday_image_generator.py

# Generate content for specific date range
python3 holiday_image_generator.py --start-date 2025-09-15 --days-ahead 30

# Custom input/output files
python3 holiday_image_generator.py --holidays-file 2025holidays.json --output-file custom_output.json

# Force regenerate existing content
python3 holiday_image_generator.py --no-skip-existing
```

#### Arguments:
- `--holidays-file`: Input JSON file with holidays (default: `data/input/2025holidays.json`)
- `--output-file`: Output JSON file for results (default: `data/output/upcoming_holidays_output.json`)
- `--start-date`: Start date in YYYY-MM-DD format (default: today)
- `--days-ahead`: Number of days to process (default: 75)
- `--no-skip-existing`: Regenerate existing content

#### Output Structure:
- **Images**: Saved to `assets/images/` folder
  - `holiday_YYYY_MM_DD_background.png` - Original AI-generated image
  - `holiday_YYYY_MM_DD_background_with_text.png` - Image with watermark
- **Data**: JSON file with complete holiday data, captions, and image paths

### Ultimate Scraper (`ultimate_scraper.py`)
**Scrapes Pensacola event websites for promotional content**

#### Features:
- Scrapes multiple Pensacola tourism and event websites
- Extracts event details, dates, descriptions
- Outputs structured JSON data for marketing use
- Handles multiple data sources and formats

#### Usage:
```bash
python3 ultimate_scraper.py
```

#### Output:
- `pensacola_events.json` - Structured event data

## Data Files

### Input Files:
- `data/input/2025holidays.json` - Complete list of holidays for the year
- `.env` - Environment variables (API keys)

### Output Files:
- `data/output/upcoming_holidays_output.json` - Generated holiday content
- `data/input/pensacola_events.json` - Scraped Pensacola events
- `assets/images/` - Generated holiday images

## Workflow Examples

### Generate Holiday Content for Next 2 Months:
```bash
source pensacola_scraper_env/bin/activate
python3 holiday_image_generator.py --days-ahead 60 --output-file next_2_months.json
```

### Scrape Fresh Pensacola Events:
```bash
source pensacola_scraper_env/bin/activate
python3 ultimate_scraper.py
```

### Continue from Specific Date:
```bash
source pensacola_scraper_env/bin/activate
python3 holiday_image_generator.py --start-date 2025-12-01 --days-ahead 31
```

### Regenerate Captions Only (No API Costs for Images):
```bash
# Regenerate captions for all existing entries
source pensacola_scraper_env/bin/activate
python3 holiday_image_generator.py --regenerate-captions --output-file data/output/upcoming_holidays_output.json

# Regenerate captions for specific dates only
python3 holiday_image_generator.py --regenerate-captions --target-dates 2025-12-25 2025-12-26 2025-12-27 --output-file data/output/upcoming_holidays_output.json
```

## Tips for Claude
1. **Always activate virtual environment first**
2. **Use `python3` command prefix**
3. **Check for `.env` file before running scripts**
4. **Holiday image generator prevents timeouts with incremental saves**
5. **Images are automatically skipped if they already exist**
6. **Progress is logged in real-time for long-running processes**
7. **For large date ranges (>30 days), expect timeouts - restart from last processed date**
8. **FIXED: Data is now preserved when regenerating - no more overwrites!**
9. **Use `--regenerate-captions` to update captions without expensive image regeneration**
10. **Unit tests available - run `python3 test_holiday_generator.py` to validate functionality**

## Troubleshooting

### Common Issues:
1. **Module not found**: Activate virtual environment
2. **API key errors**: Check `.env` file exists and contains valid keys
3. **Timeout on large batches**: Restart from last processed date using `--start-date`
4. **Permission errors**: Ensure write access to `assets/images/` folder

### Recovery Commands:
```bash
# Check last processed date in output file
grep -o '"2025-[0-9][0-9]-[0-9][0-9]"' data/output/upcoming_holidays_output.json | tail -1

# Continue from last date
python3 holiday_image_generator.py --start-date LAST_DATE --days-ahead REMAINING_DAYS
```

## Midjourney Image Generator

**Alternative high-quality image generation using Midjourney API**

### Setup Midjourney:
```bash
# Create environment file and add API key
python3 midjourney_generator.py setup
# Edit .env file and add MIDJOURNEY_API_KEY from userapi.ai

# Test connection
python3 midjourney_generator.py test
```

### Holiday Generation with Midjourney:
```bash
# Generate holiday content using Midjourney (higher quality than DALL-E)
python3 holiday_midjourney_generator.py --days-ahead 30

# Generate with animations (creates MP4 videos)
python3 holiday_midjourney_generator.py --days-ahead 7 --animate

# Single image generation
python3 midjourney_generator.py generate "festive Christmas scene, professional marketing"
```

### Midjourney Benefits:
- **Higher Quality**: Superior image generation compared to DALL-E
- **Animation Support**: Creates animated MP4 videos from static images
- **Professional Output**: Optimized for social media marketing
- **Cost Effective**: Often better value than OpenAI pricing
- **Drop-in Replacement**: Works with existing holiday workflow

## Social Media Automation (`scripts/social_media_automation.py`)

### **Overview**
Primary script for automated social media posting via Publer API. Posts to Facebook, Instagram, and Twitter with random fun facts or event-based content.

### **Basic Usage**

#### Post Random Fun Fact:
```bash
# Immediate post (24-hour auto-delete)
python3 scripts/social_media_automation.py --fact

# Test mode (15-minute auto-delete)
python3 scripts/social_media_automation.py --fact --test
```

#### Schedule Fun Facts:
```bash
# Schedule for specific date at 9 AM
python3 scripts/social_media_automation.py --fact --schedule-date 2025-10-15 --schedule-hour 9

# Schedule for specific date at 5 PM
python3 scripts/social_media_automation.py --fact --schedule-date 2025-10-15 --schedule-hour 17

# Schedule exact time
python3 scripts/social_media_automation.py --fact --schedule-time "2025-10-15 14:30"
```

#### Schedule Multiple Days (with API rate limiting):
```bash
# Schedule AM and PM posts for Oct 12-30
for date in {12..30}; do
  python3 scripts/social_media_automation.py --fact --schedule-date 2025-10-$date --schedule-hour 9
  sleep 2
  python3 scripts/social_media_automation.py --fact --schedule-date 2025-10-$date --schedule-hour 17
  sleep 2
done
```

#### Event-Based Content:
```bash
# Post today's events immediately
python3 scripts/social_media_automation.py

# Post events for specific date
python3 scripts/social_media_automation.py --date 2025-10-15

# Schedule event post
python3 scripts/social_media_automation.py --date 2025-10-15 --schedule-time "2025-10-15 09:00"
```

### **Command Line Arguments**
- `--fact` - Post random Pensacola fact (from `data/input/fun_facts.json`)
- `--date YYYY-MM-DD` - Date for event scraping (default: today)
- `--schedule-date YYYY-MM-DD` - Schedule for specific date
- `--schedule-hour 0-23` - Hour to schedule (default: 9)
- `--schedule-time "YYYY-MM-DD HH:MM"` - Exact schedule time
- `--test` - Test mode with 15-minute auto-delete
- `--scheduled` - Use scheduled publishing
- `--dry-run` - Generate content without posting

### **Platform Posting Behavior**
- **Facebook + Instagram**: Same content, supports signatures/locations
- **Twitter**: Posts separately, no signatures (character limits)
- **Reels**: Short-form video content (Facebook + Instagram)

### **Content Features**

#### Fun Facts:
- 106+ unique Pensacola facts in database
- Random selection for variety
- Automatic emoji assignment based on content
- Location tagging: Pensacola, FL
- Random branded video pairing (37 videos)

#### Hashtags:
Default hashtags added to all posts:
```
#Pensacola #PensacolaBeach #VisitPensacola #MicasaRentals
```
Plus 2 topic-specific hashtags from fun_facts.json (6 total max)

#### Event Posts:
- Scrapes live events from Visit Pensacola
- OpenAI-generated captions
- Long-form (social) and short-form (reel) versions
- Includes event links and MiCasa branding

### **Auto-Delete Timing**
- **Test Mode** (`--test`): 15 minutes
- **Production Mode** (default): 24 hours
- All posts auto-delete after specified time

### **API Rate Limiting**
To avoid Publer 429 errors when scheduling multiple posts:
- Add 2-3 second delays between posts (`sleep 2`)
- Pause 3+ seconds every 5 requests
- If rate limited, wait 30+ seconds before continuing

### **Media Selection**
- Automatically selects from branded video library
- Pattern: `^\d+_.*\.mp4$` (e.g., `17_branded.mp4`)
- Pagination support for all 37 videos
- Random selection prevents repetition

### **Examples**

#### Schedule a Week of Fun Facts (AM + PM):
```bash
source pensacola_scraper_env/bin/activate
for date in {12..18}; do
  echo "Scheduling for Oct $date..."
  python3 scripts/social_media_automation.py --fact --schedule-date 2025-10-$date --schedule-hour 9
  sleep 2
  python3 scripts/social_media_automation.py --fact --schedule-date 2025-10-$date --schedule-hour 17
  sleep 2
done
```

#### Test Fact Post Locally:
```bash
source pensacola_scraper_env/bin/activate
python3 scripts/social_media_automation.py --fact --test
# Posts will auto-delete in 15 minutes
```

#### Schedule Tomorrow's Events:
```bash
source pensacola_scraper_env/bin/activate
python3 scripts/social_media_automation.py --date 2025-10-16 --schedule-time "2025-10-16 08:00"
```

## Testing Requirements

### **ALWAYS RUN TESTS BEFORE DEPLOYING CHANGES**

After making any changes to social media automation, you MUST run the test suite to ensure functionality is preserved.

### **Test Suite Commands:**
```bash
# Activate virtual environment
source pensacola_scraper_env/bin/activate

# Run all social media automation tests
python3 tests/test_social_media_automation.py

# Run holiday generator tests
python3 tests/test_holiday_generator.py

# Run basic automation integration test (no posting)
python3 scripts/test_automation.py

# Run Publer API tests
python3 scripts/publer/test_publer.py
```

### **Test Coverage:**
- **Unit Tests**: Content generation, media selection, hashtag fallback
- **Integration Tests**: Event scraping, API connectivity
- **Regex Validation**: Video naming pattern matching
- **Error Handling**: OpenAI failures, missing media, API errors
- **Auto-Delete Timing**: 10 minutes vs 24 hours validation

### **Critical Testing Scenarios:**
1. **Media Selection**: Verify regex pattern `^\d+_.*\.mp4$` works correctly
2. **Hashtag Fallback**: Ensure `#micasa #pensacola #furnished #rental` added when no signature
3. **Multi-Platform Posting**: Facebook, Instagram, and Twitter receive posts
4. **OpenAI Function Calling**: Structured content generation works
5. **Auto-Delete Timing**: Test vs production timing differences
6. **Twitter Integration**: Verify Twitter posts work without signatures

### **Before Each Deployment:**
```bash
# Full test sequence
source pensacola_scraper_env/bin/activate
python3 tests/test_social_media_automation.py
python3 scripts/test_automation.py
echo "✅ All tests passed - safe to deploy"
```

### **When Tests Fail:**
- **DO NOT** deploy changes
- Debug and fix failing tests first
- Re-run full test suite
- Only deploy after all tests pass
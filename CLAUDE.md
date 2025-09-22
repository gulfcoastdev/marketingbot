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

## Social Media Post Auto-Delete Guidelines

### **Auto-Delete Timing Rules:**
- **Test Posts**: 10 minutes (for testing functionality)
- **Production Posts**: 24 hours (default for all regular content)
- **Custom Posts**: As specified by user

### **Implementation:**
```python
# Test posts (debugging/testing)
delete_time = datetime.now() + timedelta(minutes=10)

# Production posts (default)
delete_time = datetime.now() + timedelta(hours=24)

# Custom timing (as specified)
delete_time = datetime.now() + timedelta(hours=CUSTOM_HOURS)
```

### **When to Use:**
- **10 minutes**: Testing automation, debugging API calls, verifying content
- **24 hours**: Daily events, facts, regular marketing content
- **Custom**: Special campaigns, announcements, or user-specified duration

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
3. **Dual Platform Posting**: Both Facebook and Instagram receive posts
4. **OpenAI Function Calling**: Structured content generation works
5. **Auto-Delete Timing**: Test vs production timing differences

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
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
- Outputs images to `holiday_images/` folder

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
- `--holidays-file`: Input JSON file with holidays (default: `2025holidays.json`)
- `--output-file`: Output JSON file for results (default: `holiday_output.json`)
- `--start-date`: Start date in YYYY-MM-DD format (default: today)
- `--days-ahead`: Number of days to process (default: 75)
- `--no-skip-existing`: Regenerate existing content

#### Output Structure:
- **Images**: Saved to `holiday_images/` folder
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
- `2025holidays.json` - Complete list of holidays for the year
- `.env` - Environment variables (API keys)

### Output Files:
- `upcoming_holidays_output.json` - Generated holiday content
- `pensacola_events.json` - Scraped Pensacola events
- `holiday_images/` - Generated holiday images

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

## Tips for Claude
1. **Always activate virtual environment first**
2. **Use `python3` command prefix**
3. **Check for `.env` file before running scripts**
4. **Holiday image generator prevents timeouts with incremental saves**
5. **Images are automatically skipped if they already exist**
6. **Progress is logged in real-time for long-running processes**
7. **For large date ranges (>30 days), expect timeouts - restart from last processed date**

## Troubleshooting

### Common Issues:
1. **Module not found**: Activate virtual environment
2. **API key errors**: Check `.env` file exists and contains valid keys
3. **Timeout on large batches**: Restart from last processed date using `--start-date`
4. **Permission errors**: Ensure write access to `holiday_images/` folder

### Recovery Commands:
```bash
# Check last processed date in output file
grep -o '"2025-[0-9][0-9]-[0-9][0-9]"' upcoming_holidays_output.json | tail -1

# Continue from last date
python3 holiday_image_generator.py --start-date LAST_DATE --days-ahead REMAINING_DAYS
```
# Holiday Image Generator

This script processes holidays from a JSON file, groups them by date, generates image prompts and captions using OpenAI, and creates images with DALL-E.

## Setup

1. **Environment Setup**:
   ```bash
   # Copy the example env file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   OPENAI_API_KEY=your_actual_api_key_here
   ```

2. **Install Dependencies** (already done if using the pensacola_scraper_env):
   ```bash
   pip install openai python-dotenv pillow requests
   ```

## Usage

1. **Prepare Holiday Data**:
   - Edit `holidays.json` with your holidays
   - Format: `[{"name": "Holiday Name", "date": "YYYY-MM-DD", "description": "Description"}]`

2. **Run the Script**:
   ```bash
   python holiday_image_generator.py
   ```

## Features

- **Holiday Grouping**: Groups multiple holidays occurring on the same date
- **Smart Content Generation**: Uses GPT-4 to create image prompts and social media captions
- **DALL-E Integration**: Generates high-quality 1024x1024 images
- **Local Storage**: Saves both JSON data and images locally
- **Duplicate Prevention**: Checks existing content to avoid regenerating
- **Pensacola Focus**: Tailored prompts for Pensacola's coastal/tourism market

## Output Structure

```
holiday_output.json    # Single JSON file with all holidays
holiday_images/        # Generated images
├── holiday_2025_09_01.png
├── holiday_2025_09_11.png
└── ...
```

## JSON Output Format

```json
{
  "generated_at": "2025-09-10T12:00:00.000Z",
  "total_dates": 7,
  "holidays_by_date": {
    "2025-09-01": {
      "date": "2025-09-01",
      "original_holidays": [...],
      "selected_holiday": "Labor Day",
      "tone_category": "Respectful",
      "caption": "Honoring workers this Labor Day!",
      "image_prompt": "Instagram square post with bold text 'Honoring workers this Labor Day!' in elegant serif font...",
      "image_path": "holiday_images/holiday_2025_09_01.png",
      "generated_at": "2025-09-10T12:00:00.000Z",
      "content_ready": true
    }
  }
}
```

## Customization

- Modify the `system_prompt` in `generate_image_prompt_and_caption()` method
- Adjust DALL-E parameters in `generate_image_with_dalle()` method
- Change image size, quality, or model as needed
# Social Media Poster

A comprehensive, multi-platform social media posting system with immediate posting (Twitter/X) and scheduling capabilities (Facebook/Instagram).

## Features

### ✨ Core Capabilities
- **Multi-Platform Support**: Twitter/X, Facebook, Instagram
- **Immediate Posting**: Instant publishing to Twitter/X
- **Scheduled Posts**: Facebook/Instagram native scheduling + local queue system
- **Media Support**: Images, videos, reels, carousel posts
- **Batch Processing**: Post from JSON configuration files
- **Abstraction Layer**: Unified API for all platforms

### 🔧 Post Types Supported
- **Text posts**
- **Images** with alt-text
- **Videos**
- **Instagram Reels**
- **Stories** (platform dependent)
- **Carousel posts** (multiple media)

### 📱 Platform Features
| Platform | Immediate | Scheduled | Media | Stories | Reels |
|----------|-----------|-----------|-------|---------|--------|
| Twitter/X | ✅ | ❌* | ✅ | ❌ | ❌ |
| Facebook | ✅ | ✅ | ✅ | ✅ | ❌ |
| Instagram | ✅ | ⚠️** | ✅ | ✅ | ✅ |

*Twitter doesn't support native API scheduling
**Instagram scheduling uses local queue system

## Installation

### 1. Install Dependencies
```bash
source pensacola_scraper_env/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Credentials
Copy `.env.example` to `.env` and fill in your API credentials:

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. API Setup Guide

#### Twitter/X API
1. Create Twitter Developer account at [developer.twitter.com](https://developer.twitter.com)
2. Create a new app and get:
   - Consumer Key & Secret
   - Access Token & Secret
   - Bearer Token
3. Enable OAuth 1.0a and OAuth 2.0

#### Facebook API
1. Create Facebook Developer account at [developers.facebook.com](https://developers.facebook.com)
2. Create app and add Facebook Login + Facebook Pages products
3. Get Page Access Token with required permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_show_list`

#### Instagram API
1. Set up Instagram Business Account
2. Connect to Facebook Page
3. Use Facebook Graph API with Instagram Basic Display
4. Get Instagram Account ID from Business Manager

## Usage

### Command Line Interface

#### Quick Post (Immediate)
```bash
# Text post to Twitter
python3 social_media_poster.py --text "Hello world!" --platform twitter

# Image post to Instagram
python3 social_media_poster.py --text "Check out this image! 📸" --platform instagram --type image --media "path/to/image.jpg" --hashtags photography art

# Video to Facebook
python3 social_media_poster.py --text "Amazing video content!" --platform facebook --type video --media "https://example.com/video.mp4"
```

#### Scheduled Posts
```bash
# Schedule Facebook post
python3 social_media_poster.py --text "Good morning!" --platform facebook --schedule "2025-12-25 09:00"

# Schedule Instagram post with media
python3 social_media_poster.py --text "Holiday vibes ✨" --platform instagram --type image --media "holiday_images/holiday_2025_12_25_background_with_text.png" --schedule "2025-12-25 08:00"
```

#### Batch Posting from JSON
```bash
# Create sample JSON file
python3 social_media_poster.py --create-sample

# Post from JSON
python3 social_media_poster.py --json-file sample_posts.json

# Process scheduled posts
python3 social_media_poster.py --process-scheduled
```

#### Authentication Test
```bash
python3 social_media_poster.py --authenticate
```

### Python API Usage

```python
from social_media_poster import SocialMediaPoster, Platform, PostType

# Initialize poster
poster = SocialMediaPoster()

# Authenticate with platforms
auth_results = poster.authenticate_all()

# Quick text post
result = poster.post_now(
    text="Hello from Python! 🐍",
    platform=Platform.TWITTER,
    hashtags=["python", "automation"]
)

# Post with media
result = poster.post_now(
    text="Check out our latest content!",
    platform=Platform.INSTAGRAM,
    media_url="holiday_images/holiday_2025_12_01_background_with_text.png",
    post_type=PostType.IMAGE,
    hashtags=["content", "marketing"]
)

# Schedule post
from datetime import datetime, timedelta

result = poster.schedule_post(
    text="Scheduled post for tomorrow!",
    platform=Platform.FACEBOOK,
    scheduled_time=datetime.now() + timedelta(days=1),
    media_url="path/to/image.jpg",
    post_type=PostType.IMAGE
)
```

### JSON Configuration Format

```json
[
  {
    "text": "🎉 Exciting news! Check out our latest content!",
    "platform": "twitter",
    "post_type": "image",
    "media": [
      {
        "url": "holiday_images/holiday_2025_12_01_background_with_text.png",
        "type": "image",
        "alt_text": "Holiday marketing image"
      }
    ],
    "hashtags": ["marketing", "content", "social"],
    "link": "https://example.com",
    "scheduled_time": null
  },
  {
    "text": "Happy Holidays! 🎄",
    "platform": "facebook",
    "post_type": "image",
    "media": [
      {
        "url": "holiday_images/holiday_2025_12_25_background_with_text.png",
        "type": "image"
      }
    ],
    "scheduled_time": "2025-12-25T09:00:00"
  }
]
```

## Integration with Holiday Generator

### Automatic Social Media Posts from Holiday Content

```python
# Example: Post today's holiday content
from holiday_image_generator import HolidayImageGenerator
from social_media_poster import SocialMediaPoster, Platform, PostType
import json
from datetime import datetime

# Load generated holiday content
with open('upcoming_holidays_output.json', 'r') as f:
    holiday_data = json.load(f)

poster = SocialMediaPoster()
poster.authenticate_all()

today = datetime.now().strftime('%Y-%m-%d')
if today in holiday_data['holidays_by_date']:
    holiday = holiday_data['holidays_by_date'][today]
    
    # Post to Twitter
    twitter_result = poster.post_now(
        text=holiday['caption'],
        platform=Platform.TWITTER,
        media_url=holiday['final_image_path'],
        post_type=PostType.IMAGE,
        hashtags=[holiday['selected_holiday'].replace(' ', '')]
    )
    
    # Post to Instagram
    instagram_result = poster.post_now(
        text=holiday['caption'],
        platform=Platform.INSTAGRAM,
        media_url=holiday['final_image_path'],
        post_type=PostType.IMAGE
    )
```

## Advanced Features

### Custom Platform Implementation
```python
from social_media_poster import SocialMediaPlatform, Platform

class LinkedInPlatform(SocialMediaPlatform):
    def authenticate(self) -> bool:
        # LinkedIn authentication logic
        pass
    
    def post_immediate(self, post_data: PostData) -> Dict[str, Any]:
        # LinkedIn posting logic
        pass
    
    def schedule_post(self, post_data: PostData) -> Dict[str, Any]:
        # LinkedIn scheduling logic
        pass
```

### Bulk Holiday Content Publishing
```python
# Bulk post all upcoming holidays
def bulk_post_holidays(days_ahead=7):
    with open('upcoming_holidays_output.json', 'r') as f:
        holiday_data = json.load(f)
    
    poster = SocialMediaPoster()
    poster.authenticate_all()
    
    posts_config = []
    
    for date, holiday in holiday_data['holidays_by_date'].items():
        # Create posts for each platform
        for platform in ['twitter', 'facebook', 'instagram']:
            posts_config.append({
                'text': holiday['caption'],
                'platform': platform,
                'post_type': 'image',
                'media': [{'url': holiday['final_image_path'], 'type': 'image'}],
                'hashtags': [holiday['selected_holiday'].replace(' ', '')],
                'scheduled_time': f"{date}T09:00:00"
            })
    
    # Save as JSON and process
    with open('bulk_holiday_posts.json', 'w') as f:
        json.dump(posts_config, f, indent=2)
    
    return poster.post_from_json('bulk_holiday_posts.json')
```

## Error Handling & Monitoring

### Built-in Error Handling
- API rate limit handling
- Automatic retries for failed posts
- Detailed error reporting
- Graceful platform failures

### Monitoring Scheduled Posts
```bash
# Check scheduled posts status
python3 -c "
import json
with open('scheduled_posts.json', 'r') as f:
    posts = json.load(f)
print(f'Pending scheduled posts: {len(posts)}')
"
```

## Security Best Practices

### Environment Variables
- Never commit API keys to git
- Use `.env` file for credentials
- Rotate API keys regularly
- Use minimum required permissions

### Rate Limiting
- Built-in rate limit handling
- Automatic backoff and retry
- Platform-specific limits respected

## Troubleshooting

### Common Issues
1. **Authentication Failed**: Check API credentials and permissions
2. **Media Upload Failed**: Verify file format and size limits
3. **Scheduling Not Working**: Check timezone settings and future dates
4. **Rate Limited**: Wait and retry, or reduce posting frequency

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with detailed logging
poster = SocialMediaPoster()
result = poster.post_now("Debug test", Platform.TWITTER)
```

## API Reference

### Classes
- `SocialMediaPoster`: Main orchestrator class
- `PostData`: Universal post data structure
- `MediaItem`: Media attachment structure
- `SocialMediaPlatform`: Abstract base class for platforms

### Enums
- `Platform`: Supported social media platforms
- `PostType`: Types of posts (text, image, video, reel, etc.)

### Methods
- `post_now()`: Immediate posting
- `schedule_post()`: Schedule for later
- `post_from_json()`: Batch posting from JSON
- `process_scheduled_posts()`: Process pending scheduled posts
- `authenticate_all()`: Authenticate with all platforms

This system provides a robust, scalable solution for automated social media marketing with comprehensive platform support and flexible configuration options.
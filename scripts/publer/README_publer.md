# Publer API Social Media Posting

Automated social media posting system using Publer API for MiCasa.Rentals marketing campaigns.

## Setup

### 1. Environment Variables
Add your Publer API key to the `.env` file:
```
PUBLER_API_KEY=your_publer_api_key_here
```

### 2. Dependencies
Install required packages:
```bash
pip install requests python-dotenv
```

### 3. Publer Account Requirements
- **Business or Enterprise Publer account** (API access not available on free plans)
- Connected social media accounts in your Publer workspace
- API key generated with required scopes: workspaces, accounts, posts

## Scripts Overview

### 1. `publer_poster.py`
Core Publer API client with comprehensive functionality:
- Workspace and account management
- Post creation and scheduling
- Media upload support
- Job status monitoring

### 2. `test_publer.py`
Test script to verify API connection and basic functionality:
- Tests workspace/account access
- Creates sample text posts
- Optional video posting test

### 3. `post_branded_video.py`
Production script for posting branded promotional videos:
- Posts videos from `brandingburner/promovideosraw_branded/` folder
- Random or specific video selection
- Pre-written MiCasa.Rentals marketing captions
- Multi-platform posting support

## Usage Examples

### Basic API Test
```bash
python3 test_publer.py
```

### Post Random Branded Video
```bash
# Post immediately to Facebook
python3 post_branded_video.py --random

# Schedule for 30 minutes from now
python3 post_branded_video.py --random --schedule 30

# Post to multiple platforms
python3 post_branded_video.py --random --platforms facebook instagram
```

### Post Specific Video
```bash
# Post video #15 immediately
python3 post_branded_video.py --video 15

# Schedule video #8 for 1 hour from now, multiple platforms
python3 post_branded_video.py --video 8 --schedule 60 --platforms facebook instagram linkedin
```

### Using the Core API Directly
```python
from publer_poster import PublerPoster

# Initialize
poster = PublerPoster()
poster.get_workspaces()
poster.get_accounts()

# Create text post
poster.create_post(
    text="Your marketing message here!",
    platforms=['facebook', 'instagram'],
    schedule_time=datetime.now() + timedelta(hours=1)
)

# Create video post
poster.create_post(
    text="Check out this amazing video!",
    platforms=['facebook'],
    media_path="path/to/video.mp4"
)
```

## Supported Platforms

Based on Publer API documentation:
- Facebook (Pages)
- Instagram (Business accounts)
- Twitter/X
- LinkedIn (Pages)
- Pinterest
- YouTube
- TikTok
- And more...

*Note: Available platforms depend on your connected accounts in Publer*

## Post Types Supported

- **Text posts**: Simple status updates
- **Photo posts**: Images with captions
- **Video posts**: Video content with captions
- **Link posts**: URLs with preview cards
- **Carousel posts**: Multiple images/videos
- **Stories**: Instagram/Facebook stories
- **Reels**: Short-form video content

## Marketing Captions

The `post_branded_video.py` script includes 8 pre-written marketing captions for MiCasa.Rentals:

1. Beach paradise escape messaging
2. Ocean view luxury focus
3. Perfect vacation awaits theme
4. Home away from home concept
5. Sunrise and luxury experience
6. Adventure and relaxation balance
7. Emerald Coast destination highlight
8. Paradise found at Pensacola Beach

Captions are randomly selected to provide variety in your social media feed.

## Scheduling Features

- **Immediate posting**: `--schedule 0` or omit parameter
- **Future scheduling**: `--schedule X` (X = minutes from now)
- **Custom scheduling**: Use the API directly with specific datetime objects

## Error Handling

The scripts include comprehensive error handling for:
- API authentication failures
- Network connectivity issues
- Missing media files
- Invalid account configurations
- Job status monitoring timeouts

## Workflow Integration

### Daily Posting
```bash
# Schedule today's promotional video for peak engagement time
python3 post_branded_video.py --random --schedule 240 --platforms facebook instagram
```

### Weekly Campaign
```bash
# Post specific videos throughout the week
python3 post_branded_video.py --video 1 --schedule 60
python3 post_branded_video.py --video 15 --schedule 1500  # Tomorrow
python3 post_branded_video.py --video 22 --schedule 2940  # Day after
```

### Event-Based Posting
```bash
# Post related to today's events (integrate with daily_events_scraper.py)
python3 daily_events_scraper.py --date $(date +%Y-%m-%d) --quiet > today_events.json
# Then use events data to customize posting strategy
```

## Monitoring and Analytics

- Use `poster.get_posts()` to retrieve recent posts
- Monitor job status with `poster.check_job_status(job_id)`
- Check post performance in Publer dashboard
- Review engagement metrics for optimization

## Troubleshooting

### Common Issues

1. **"No workspaces found"**
   - Verify API key is correct
   - Ensure Business/Enterprise Publer account
   - Check API key scopes include 'workspaces'

2. **"No accounts found"**
   - Connect social media accounts in Publer dashboard
   - Verify accounts are active and authorized
   - Check workspace permissions

3. **"Media upload failed"**
   - Verify file exists and is accessible
   - Check file format compatibility
   - Ensure file size within limits

4. **"Post creation failed"**
   - Verify account permissions
   - Check platform-specific content requirements
   - Review text length limits

### Debug Mode
Add debug prints to scripts for troubleshooting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Notes

- Keep API keys secure and never commit to version control
- Use environment variables for sensitive data
- Regularly rotate API keys
- Monitor API usage and rate limits
- Review posted content before scheduling

## Rate Limits

Publer API has rate limits (specific limits not documented):
- Implement delays between bulk operations
- Monitor response headers for rate limit info
- Use scheduling to distribute posts over time

## Future Enhancements

Potential improvements:
- Content calendar integration
- A/B testing for captions
- Analytics data collection
- Automatic hashtag optimization
- Event-based content customization
- Multi-language caption support
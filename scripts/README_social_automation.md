# Social Media Automation Script

Automatically scrapes Pensacola events, generates AI-powered social media content, and posts to Facebook and Instagram with branded videos.

## Features

- 🔍 **Event Scraping**: Scrapes Visit Pensacola for daily events
- 🤖 **AI Content Generation**: Uses OpenAI GPT-4 to create engaging social media posts
- 🎬 **Random Media Selection**: Selects videos from Publer library (naming convention: `number_**.mp4`)
- 📱 **Multi-Platform Posting**: Posts to Facebook and Instagram (feed + reels)
- ⏰ **Auto-Delete**: Automatically deletes posts after 24 hours
- 🎯 **Branded Content**: Promotes MiCasa.Rentals vacation rentals

## Usage

### Basic Usage
```bash
# Run automation for today (immediate publishing)
python3 scripts/social_media_automation.py

# Run for specific date (immediate publishing)
python3 scripts/social_media_automation.py --date 2025-09-25

# Schedule posts for specific time
python3 scripts/social_media_automation.py --schedule-time "2025-09-25 14:30"

# Use scheduled publishing mode
python3 scripts/social_media_automation.py --scheduled

# Test without posting
python3 scripts/social_media_automation.py --dry-run
```

### Publishing Modes

**Immediate Publishing** (Default):
- Posts are published instantly using Publer's immediate publishing API
- Uses endpoint: `/api/v1/posts/schedule/publish`
- No scheduling delay - posts go live immediately

**Scheduled Publishing**:
- Posts are scheduled for future publishing
- Uses endpoint: `/api/v1/posts/schedule`
- Requires `--scheduled` flag or `--schedule-time` parameter

### What Gets Posted

**Social Media Posts** (Facebook + Instagram Feed):
- Engaging text highlighting Pensacola events and MiCasa rentals
- Video content from Publer library
- Auto-deletes after 24 hours

**Reel Posts** (Facebook + Instagram Reels):
- Short, energetic content for video format
- Same video content but optimized for reels
- Auto-deletes after 24 hours

## Requirements

### Environment Variables
```
OPENAI_API_KEY=your_openai_api_key
PUBLER_API_KEY=your_publer_api_key_with_media_scope
```

### Publer Setup
1. API key must have `media` scope enabled
2. Upload branded videos following naming convention: `1_video.mp4`, `2_content.mp4`, etc.
3. Connect Facebook and Instagram accounts

### Video Naming Convention
Videos in Publer library should follow this pattern:
- `1_beachview.mp4`
- `18_branded.mp4`
- `25_sunset.mp4`
- etc.

## Script Workflow

1. **Scrape Events**: Gets events for specified date from Visit Pensacola
2. **Generate Content**: Uses OpenAI to create 2 types of content:
   - Social post (150 chars, feed content)
   - Reel post (100 chars, energetic video content)
3. **Select Media**: Randomly picks a video from Publer library
4. **Create Posts**: Publishes 4 posts total:
   - Facebook feed post with video
   - Instagram feed post with video
   - Facebook reel with video
   - Instagram reel with video
5. **Auto-Delete**: All posts delete automatically after 24 hours

## Testing

```bash
# Test all components without posting
python3 scripts/test_automation.py

# Check Publer API permissions
python3 scripts/publer/check_api_permissions.py
```

## Error Handling

The script handles common issues:
- No events found → Uses fallback content
- No media found → Posts without media
- OpenAI API errors → Uses fallback content
- Publer API errors → Detailed error messages

## Sample Output

```
🚀 Starting social media automation for 2025-09-20
🔍 Scraping events for 2025-09-20...
✅ Found 22 events
🤖 Generating social media content...
✅ Generated content:
SOCIAL: 🎭 Mystery, art, and Oktoberfest await in Pensacola today! 🍻 After the fun, unwind at our luxury beachfront rentals at MiCasa 🏖️🌅
REEL: Don't miss Pensacola's vibrant scene! 🎉 Stay at MiCasa and get the beachfront luxury experience! 🏖️✨
🎬 Selecting random media...
✅ Selected video: 18_branded.mp4
📱 Creating social media posts...
📝 Creating social media post...
✅ Post created successfully for facebook, instagram!
🎥 Creating reel post...
✅ Reel post created successfully for facebook, instagram!
⏰ Auto-delete scheduled for: 2025-09-21 18:30

🎉 Automation completed successfully!
📊 Results summary:
   • Events found: 22
   • Social post: ✅
   • Reel post: ✅
   • Media used: 18_branded.mp4
   • Auto-delete: 24 hours from now
```

## Scheduling Examples

### Immediate Publishing (Default)
```bash
# Post immediately for today's events
python3 scripts/social_media_automation.py

# Post immediately for specific date
python3 scripts/social_media_automation.py --date 2025-12-25
```

### Scheduled Publishing
```bash
# Schedule posts for 2 PM tomorrow
python3 scripts/social_media_automation.py --schedule-time "2025-09-21 14:00"

# Use scheduled mode (posts go into Publer queue)
python3 scripts/social_media_automation.py --scheduled --date 2025-09-25
```

### Automation with Cron Jobs

**Daily immediate posting at 9 AM:**
```bash
0 9 * * * cd /path/to/marketing-bot && source pensacola_scraper_env/bin/activate && python3 scripts/social_media_automation.py
```

**Schedule posts for later in the day:**
```bash
# Generate and schedule posts at 8 AM for 2 PM publishing
0 8 * * * cd /path/to/marketing-bot && source pensacola_scraper_env/bin/activate && python3 scripts/social_media_automation.py --schedule-time "$(date -d '+6 hours' +'%Y-%m-%d %H:00')"
```
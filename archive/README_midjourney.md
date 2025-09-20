# Midjourney Image Generator

Generate and animate images using the unofficial Midjourney API through userapi.ai.

## Setup

1. **Get API Key**: Sign up at userapi.ai and get your Midjourney API key
2. **Configure Environment**: Copy the example and add your API key
   ```bash
   cp .env.midjourney.example .env
   # Edit .env and add your MIDJOURNEY_API_KEY
   ```

## Usage

### Basic Image Generation
```bash
# Generate a single image
python3 midjourney_generator.py generate "beautiful sunset over ocean, cinematic"

# Generate and animate
python3 midjourney_generator.py generate "cozy holiday scene with warm lighting"
```

### Holiday Content Generation
```bash
# Generate holiday content for next 30 days with Midjourney
python3 holiday_midjourney_generator.py --days-ahead 30

# Generate with animations
python3 holiday_midjourney_generator.py --days-ahead 7 --animate

# Generate from specific date
python3 holiday_midjourney_generator.py --start-date 2025-09-20 --days-ahead 15
```

### Test the Service
```bash
# Test API connection and generate sample images
python3 midjourney_generator.py test
```

## Features

### Core Functionality
- **Image Generation**: High-quality images using Midjourney
- **Animation**: Convert static images to animated videos
- **Batch Processing**: Generate multiple holiday images efficiently
- **Quality Control**: Professional social media ready output
- **Error Handling**: Robust retry logic and error reporting

### Integration
- **Holiday Generator**: Drop-in replacement for DALL-E
- **Existing Workflow**: Works with existing caption generation
- **Watermarks**: Applies same branding as original system
- **File Organization**: Saves to organized folder structure

## API Endpoints (userapi.ai)

The script uses these common endpoints:
- `POST /midjourney/v1/imagine` - Generate image
- `GET /midjourney/v1/task/{task_id}` - Check status  
- `POST /midjourney/v1/animate` - Animate image

## Configuration

### Environment Variables
```bash
# Required
MIDJOURNEY_API_KEY=your_api_key_here

# Optional - custom base URL
MIDJOURNEY_BASE_URL=https://api.userapi.ai/midjourney/v1
```

### Output Structure
```
assets/
├── midjourney/           # Raw Midjourney outputs
│   ├── image_20250912_143022.png
│   └── image_20250912_143022_animated.mp4
└── images/              # Holiday workflow outputs  
    ├── holiday_2025_09_13_background.png
    ├── holiday_2025_09_13_background_with_text.png
    └── holiday_2025_09_13_animated.mp4
```

## Prompt Enhancement

The system automatically enhances your prompts for better social media results:

**Original**: "sunset over mountains"
**Enhanced**: "sunset over mountains, professional social media content, high quality, Instagram ready --ar 1:1 --quality standard"

## Animation Options

- **Motion Strength**: 1-10 intensity scale
- **Format**: MP4 video output
- **Duration**: Typically 3-5 seconds
- **Quality**: Maintains original image resolution

## Error Handling

- **Timeout Protection**: Max 5 minutes per generation
- **Rate Limiting**: Respects API limits
- **Retry Logic**: Auto-retry on temporary failures
- **Fallback**: Graceful degradation if animation fails

## Cost Considerations

- **Image Generation**: ~$0.10-0.30 per image (varies by service)
- **Animation**: ~$0.20-0.50 per animation
- **Batch Processing**: Monitor costs with large date ranges
- **Rate Limits**: Respect service limits to avoid extra charges

## Troubleshooting

### Common Issues

1. **API Key Error**: Check your .env file has correct key
2. **Timeout**: Reduce batch size or increase timeout values  
3. **Animation Failed**: Check image URL is publicly accessible
4. **Quality Issues**: Adjust prompt or quality settings

### Debug Mode
```bash
# Enable verbose logging
export MIDJOURNEY_DEBUG=1
python3 midjourney_generator.py test
```

## Examples

### Holiday Marketing
```bash
# Generate Christmas content
python3 midjourney_generator.py generate "festive Christmas scene with warm lights, cozy atmosphere, professional marketing image"

# Generate animated New Year content  
python3 holiday_midjourney_generator.py --start-date 2025-12-31 --days-ahead 2 --animate
```

### Custom Prompts
```python
from midjourney_generator import MidjourneyGenerator

generator = MidjourneyGenerator()
result = generator.generate_and_animate(
    prompt="modern minimalist office space, natural lighting, professional",
    aspect_ratio="16:9",
    animate=True,
    motion_strength=4
)
```

## Performance Tips

1. **Batch Processing**: Process multiple dates in single session
2. **Skip Existing**: Use `--no-skip-existing` only when needed
3. **Optimize Prompts**: Clear, specific prompts generate better results
4. **Monitor Costs**: Track API usage to avoid overspend
5. **Cache Results**: Generated images are saved locally

## Support

For API-specific issues, check:
- userapi.ai documentation
- Service status page
- Rate limit information

For script issues, check logs and error messages for troubleshooting guidance.
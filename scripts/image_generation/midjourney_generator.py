#!/usr/bin/env python3
"""
Midjourney Image Generator using userapi.ai
Generates and animates images using unofficial Midjourney API
"""

import os
import requests
import json
import time
from datetime import datetime
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MidjourneyGenerator:
    def __init__(self):
        """Initialize Midjourney API client"""
        self.api_key = os.getenv('MIDJOURNEY_API_KEY')
        if not self.api_key:
            raise ValueError("MIDJOURNEY_API_KEY not found in environment variables")
        
        # Correct userapi.ai base URL and headers
        self.base_url = "https://api.userapi.ai"
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Create output directory
        self.output_dir = Path("assets/midjourney")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_image(self, prompt, aspect_ratio="1:1", model="midjourney", quality="standard"):
        """
        Generate image using Midjourney API
        
        Args:
            prompt (str): Text prompt for image generation
            aspect_ratio (str): Image aspect ratio (1:1, 16:9, 9:16, etc.)
            model (str): Model version to use
            quality (str): Image quality (standard, high)
        
        Returns:
            dict: Response with task ID and status
        """
        try:
            # Format prompt for Midjourney
            formatted_prompt = f"{prompt} --ar {aspect_ratio} --quality {quality}"
            
            payload = {
                "prompt": formatted_prompt,
                "webhook_url": None,
                "webhook_secret": None
            }
            
            logger.info(f"🎨 Generating image with prompt: {prompt}")
            logger.info(f"📐 Aspect ratio: {aspect_ratio}, Quality: {quality}")
            
            # Submit generation request to correct endpoint
            url = f"{self.base_url}/midjourney/v2/imagine"
            logger.info(f"🔗 Calling: {url}")
            
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"📋 API Response: {result}")
                task_id = result.get('task_id') or result.get('hash') or result.get('id')
                logger.info(f"✅ Image generation started. Task ID: {task_id}")
                return result
            else:
                logger.error(f"❌ Failed to generate image: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generating image: {e}")
            return None
    
    def check_task_status(self, task_id):
        """
        Check the status of a generation task
        
        Args:
            task_id (str): Task ID from generation request
        
        Returns:
            dict: Task status and result
        """
        try:
            # Use the correct status endpoint with hash parameter
            url = f"{self.base_url}/midjourney/v2/status"
            params = {"hash": task_id}
            
            logger.info(f"🔍 Checking status: {url}?hash={task_id}")
            
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"⚠️ Status check returned {response.status_code}: {response.text[:100]}")
                return {"status": "unknown", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Error checking task status: {e}")
            return None
    
    def wait_for_completion(self, task_id, max_wait_time=300, check_interval=10):
        """
        Wait for image generation to complete
        
        Args:
            task_id (str): Task ID to monitor
            max_wait_time (int): Maximum wait time in seconds
            check_interval (int): Time between status checks
        
        Returns:
            dict: Final task result or None if timeout/error
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            logger.info(f"⏳ Checking task status...")
            
            status = self.check_task_status(task_id)
            if not status:
                logger.error("❌ Failed to get task status")
                return None
            
            task_status = status.get('status', 'unknown')
            logger.info(f"📊 Task status: {task_status}")
            
            if task_status == 'completed':
                logger.info("🎉 Image generation completed!")
                return status
            elif task_status == 'failed':
                logger.error("❌ Image generation failed")
                return status
            elif task_status in ['processing', 'in_queue', 'started']:
                logger.info(f"⏳ Still processing... waiting {check_interval}s")
                time.sleep(check_interval)
            else:
                logger.warning(f"⚠️ Unknown status: {task_status}")
                time.sleep(check_interval)
        
        logger.error(f"⏰ Timeout after {max_wait_time}s")
        return None
    
    def download_image(self, image_url, filename=None):
        """
        Download generated image
        
        Args:
            image_url (str): URL of the generated image
            filename (str): Optional custom filename
        
        Returns:
            str: Path to downloaded image
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"midjourney_{timestamp}.png"
            
            filepath = self.output_dir / filename
            
            logger.info(f"📥 Downloading image to {filepath}")
            
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ Image saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Error downloading image: {e}")
            return None
    
    def animate_image(self, image_url_or_path, motion_strength=5):
        """
        Animate a generated image using Runway ML style animation
        
        Args:
            image_url_or_path (str): URL or local path to image
            motion_strength (int): Animation intensity (1-10)
        
        Returns:
            dict: Animation task result
        """
        try:
            # Prepare payload for animation
            payload = {
                "image_url": image_url_or_path if image_url_or_path.startswith('http') else None,
                "motion_strength": motion_strength,
                "webhook_url": None
            }
            
            # If local file, we might need to upload it first
            if not image_url_or_path.startswith('http'):
                logger.info("📤 Local file detected, animation may require image URL")
                # In real implementation, you'd upload the file first
                return {"error": "Local file animation requires upload endpoint"}
            
            logger.info(f"🎬 Starting animation with motion strength: {motion_strength}")
            
            response = requests.post(
                f"{self.base_url}/animate",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Animation started. Task ID: {result.get('task_id')}")
                return result
            else:
                logger.error(f"❌ Animation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error animating image: {e}")
            return None
    
    def generate_and_animate(self, prompt, aspect_ratio="1:1", animate=True, motion_strength=5):
        """
        Complete workflow: generate image and optionally animate it
        
        Args:
            prompt (str): Image generation prompt
            aspect_ratio (str): Image aspect ratio
            animate (bool): Whether to animate the result
            motion_strength (int): Animation intensity
        
        Returns:
            dict: Complete workflow results
        """
        logger.info(f"🚀 Starting complete workflow for: {prompt}")
        
        # Step 1: Generate image
        generation_result = self.generate_image(prompt, aspect_ratio)
        if not generation_result:
            return {"error": "Image generation failed"}
        
        task_id = generation_result.get('task_id') or generation_result.get('hash') or generation_result.get('id')
        
        # Step 2: Wait for completion
        final_result = self.wait_for_completion(task_id, max_wait_time=300, check_interval=15)
        if not final_result or final_result.get('status') != 'completed':
            return {"error": "Image generation did not complete successfully"}
        
        # Step 3: Download image
        image_url = final_result.get('image_url') or final_result.get('result', {}).get('image_url')
        if not image_url:
            return {"error": "No image URL in result"}
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_prompt = "".join(c for c in prompt[:50] if c.isalnum() or c in (' ', '_')).strip()
        filename = f"{safe_prompt}_{timestamp}.png"
        
        image_path = self.download_image(image_url, filename)
        if not image_path:
            return {"error": "Image download failed"}
        
        result = {
            "image_path": image_path,
            "image_url": image_url,
            "prompt": prompt,
            "task_id": task_id
        }
        
        # Step 4: Animate if requested
        if animate:
            logger.info("🎬 Starting animation...")
            animation_result = self.animate_image(image_url, motion_strength)
            
            if animation_result and not animation_result.get('error'):
                animation_task_id = animation_result.get('task_id')
                animation_final = self.wait_for_completion(animation_task_id)
                
                if animation_final and animation_final.get('status') == 'completed':
                    video_url = animation_final.get('video_url') or animation_final.get('result', {}).get('video_url')
                    if video_url:
                        video_filename = f"{safe_prompt}_{timestamp}_animated.mp4"
                        video_path = self.download_image(video_url, video_filename)  # Same method works for videos
                        
                        result.update({
                            "video_path": video_path,
                            "video_url": video_url,
                            "animation_task_id": animation_task_id
                        })
                        logger.info("🎉 Animation completed successfully!")
                    else:
                        logger.warning("⚠️ Animation completed but no video URL found")
                else:
                    logger.warning("⚠️ Animation did not complete successfully")
            else:
                logger.warning("⚠️ Animation failed to start")
        
        return result

def create_env_example():
    """Create example environment file"""
    env_example_content = """# Midjourney API Configuration
# Get your API key from userapi.ai or similar service
MIDJOURNEY_API_KEY=your_midjourney_api_key_here

# Optional: Custom base URL if using different service
# MIDJOURNEY_BASE_URL=https://api.userapi.ai/midjourney/v1
"""
    
    with open('.env.midjourney.example', 'w') as f:
        f.write(env_example_content)
    
    logger.info("Created .env.midjourney.example file")

def test_generation():
    """Test the Midjourney generator"""
    try:
        generator = MidjourneyGenerator()
        
        # Test prompts
        test_prompts = [
            "A serene mountain landscape at sunset, photorealistic",
            "Modern minimalist office space with natural lighting",
            "Festive holiday celebration with warm colors and joy"
        ]
        
        for prompt in test_prompts:
            logger.info(f"\n🧪 Testing prompt: {prompt}")
            
            # Generate and animate
            result = generator.generate_and_animate(
                prompt=prompt,
                aspect_ratio="16:9",
                animate=True,
                motion_strength=3
            )
            
            if result.get('error'):
                logger.error(f"❌ Test failed: {result['error']}")
            else:
                logger.info(f"✅ Test completed successfully!")
                logger.info(f"   Image: {result.get('image_path')}")
                logger.info(f"   Video: {result.get('video_path', 'Not animated')}")
            
            break  # Only test first prompt to avoid rate limits

    except ValueError as e:
        logger.error(f"❌ Setup error: {e}")
        logger.info("💡 Make sure to set MIDJOURNEY_API_KEY in your .env file")
    except Exception as e:
        logger.error(f"❌ Test error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_generation()
        elif sys.argv[1] == "setup":
            create_env_example()
        elif sys.argv[1] == "generate":
            if len(sys.argv) < 3:
                print("Usage: python midjourney_generator.py generate 'your prompt here'")
                sys.exit(1)
            
            prompt = " ".join(sys.argv[2:])
            generator = MidjourneyGenerator()
            result = generator.generate_and_animate(prompt, animate=True)
            
            if result.get('error'):
                logger.error(f"❌ Generation failed: {result['error']}")
            else:
                logger.info("🎉 Generation completed!")
                print(f"Image: {result.get('image_path')}")
                print(f"Video: {result.get('video_path', 'Not animated')}")
        else:
            print("Usage:")
            print("  python midjourney_generator.py setup    # Create example .env file")
            print("  python midjourney_generator.py test     # Test the service")  
            print("  python midjourney_generator.py generate 'prompt' # Generate image/video")
    else:
        print("Midjourney Image and Animation Generator")
        print("\nUsage:")
        print("  python midjourney_generator.py setup    # Create example .env file")
        print("  python midjourney_generator.py test     # Test the service")
        print("  python midjourney_generator.py generate 'your prompt' # Generate image/video")
        print("\nExample:")
        print("  python midjourney_generator.py generate 'beautiful sunset over ocean, cinematic'")
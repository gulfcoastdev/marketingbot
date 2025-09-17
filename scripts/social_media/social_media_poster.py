#!/usr/bin/env python3
"""
Social Media Poster - Universal posting system for multiple platforms
Supports immediate posting (Twitter/X) and scheduled posting (Facebook/Instagram)
"""

import json
import os
import sys
import logging
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import requests
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PostType(Enum):
    """Supported post types"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    REEL = "reel"
    STORY = "story"
    CAROUSEL = "carousel"

class Platform(Enum):
    """Supported social media platforms"""
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"

@dataclass
class MediaItem:
    """Media item for posts"""
    url: str
    type: str  # image, video
    alt_text: Optional[str] = None
    caption: Optional[str] = None

@dataclass
class PostData:
    """Universal post data structure"""
    text: str
    platform: Platform
    post_type: PostType = PostType.TEXT
    media: Optional[List[MediaItem]] = None
    scheduled_time: Optional[datetime] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    link: Optional[str] = None
    location: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'text': self.text,
            'platform': self.platform.value,
            'post_type': self.post_type.value,
            'media': [{'url': m.url, 'type': m.type, 'alt_text': m.alt_text, 'caption': m.caption} 
                     for m in self.media] if self.media else None,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'hashtags': self.hashtags,
            'mentions': self.mentions,
            'link': self.link,
            'location': self.location
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PostData':
        """Create PostData from dictionary"""
        media = None
        if data.get('media'):
            media = [MediaItem(**m) for m in data['media']]
        
        scheduled_time = None
        if data.get('scheduled_time'):
            scheduled_time = datetime.fromisoformat(data['scheduled_time'])
        
        return cls(
            text=data['text'],
            platform=Platform(data['platform']),
            post_type=PostType(data['post_type']),
            media=media,
            scheduled_time=scheduled_time,
            hashtags=data.get('hashtags'),
            mentions=data.get('mentions'),
            link=data.get('link'),
            location=data.get('location')
        )

class SocialMediaPlatform(ABC):
    """Abstract base class for social media platforms"""
    
    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self._authenticated = False
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the platform"""
        pass
    
    @abstractmethod
    def post_immediate(self, post_data: PostData) -> Dict[str, Any]:
        """Post immediately to the platform"""
        pass
    
    @abstractmethod
    def schedule_post(self, post_data: PostData) -> Dict[str, Any]:
        """Schedule a post for later"""
        pass
    
    @abstractmethod
    def get_post_status(self, post_id: str) -> Dict[str, Any]:
        """Get status of a scheduled or published post"""
        pass
    
    def validate_post_data(self, post_data: PostData) -> bool:
        """Validate post data for this platform"""
        return True

class TwitterPlatform(SocialMediaPlatform):
    """Twitter/X platform implementation"""
    
    def __init__(self, credentials: Dict[str, str]):
        super().__init__(credentials)
        self.client = None
        self.api = None
    
    def authenticate(self) -> bool:
        """Authenticate with Twitter API v2"""
        try:
            # Twitter API v2 client for posting
            self.client = tweepy.Client(
                bearer_token=self.credentials.get('bearer_token'),
                consumer_key=self.credentials.get('consumer_key'),
                consumer_secret=self.credentials.get('consumer_secret'),
                access_token=self.credentials.get('access_token'),
                access_token_secret=self.credentials.get('access_token_secret'),
                wait_on_rate_limit=True
            )
            
            # Twitter API v1.1 for media upload
            auth = tweepy.OAuth1UserHandler(
                self.credentials.get('consumer_key'),
                self.credentials.get('consumer_secret'),
                self.credentials.get('access_token'),
                self.credentials.get('access_token_secret')
            )
            self.api = tweepy.API(auth)
            
            # Test authentication
            user = self.client.get_me()
            logger.info(f"Twitter authentication successful for @{user.data.username}")
            self._authenticated = True
            return True
            
        except Exception as e:
            logger.error(f"Twitter authentication failed: {e}")
            return False
    
    def post_immediate(self, post_data: PostData) -> Dict[str, Any]:
        """Post immediately to Twitter"""
        if not self._authenticated:
            raise Exception("Not authenticated with Twitter")
        
        try:
            media_ids = []
            
            # Upload media if present
            if post_data.media:
                for media_item in post_data.media:
                    if media_item.url.startswith('http'):
                        # Download remote media
                        response = requests.get(media_item.url)
                        media_data = response.content
                        filename = f"temp_media_{datetime.now().timestamp()}"
                    else:
                        # Local file
                        with open(media_item.url, 'rb') as f:
                            media_data = f.read()
                        filename = media_item.url
                    
                    # Upload to Twitter
                    media = self.api.media_upload(filename=filename, file=media_data)
                    media_ids.append(media.media_id)
                    
                    # Add alt text if provided
                    if media_item.alt_text:
                        self.api.create_media_metadata(media.media_id, media_item.alt_text)
            
            # Prepare tweet text
            tweet_text = post_data.text
            if post_data.hashtags:
                tweet_text += " " + " ".join([f"#{tag}" for tag in post_data.hashtags])
            if post_data.link:
                tweet_text += f" {post_data.link}"
            
            # Post tweet
            response = self.client.create_tweet(
                text=tweet_text,
                media_ids=media_ids if media_ids else None
            )
            
            result = {
                'success': True,
                'post_id': response.data['id'],
                'url': f"https://twitter.com/i/status/{response.data['id']}",
                'platform': 'twitter',
                'posted_at': datetime.now().isoformat()
            }
            
            logger.info(f"Successfully posted to Twitter: {result['url']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to post to Twitter: {e}")
            return {
                'success': False,
                'error': str(e),
                'platform': 'twitter'
            }
    
    def schedule_post(self, post_data: PostData) -> Dict[str, Any]:
        """Twitter doesn't support native scheduling via API"""
        return {
            'success': False,
            'error': 'Twitter API does not support native scheduling. Use immediate posting or third-party tools.',
            'platform': 'twitter'
        }
    
    def get_post_status(self, post_id: str) -> Dict[str, Any]:
        """Get Twitter post status"""
        try:
            tweet = self.client.get_tweet(post_id, tweet_fields=['created_at', 'public_metrics'])
            return {
                'success': True,
                'post_id': post_id,
                'status': 'published',
                'metrics': tweet.data.public_metrics,
                'created_at': tweet.data.created_at.isoformat(),
                'platform': 'twitter'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': 'twitter'
            }

class FacebookPlatform(SocialMediaPlatform):
    """Facebook platform implementation"""
    
    def __init__(self, credentials: Dict[str, str]):
        super().__init__(credentials)
        self.page_id = credentials.get('page_id')
        self.access_token = credentials.get('access_token')
    
    def authenticate(self) -> bool:
        """Authenticate with Facebook Graph API"""
        try:
            # Test API access
            url = f"https://graph.facebook.com/v18.0/me"
            params = {'access_token': self.access_token}
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Facebook authentication successful for {data.get('name')}")
                self._authenticated = True
                return True
            else:
                logger.error(f"Facebook authentication failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Facebook authentication error: {e}")
            return False
    
    def post_immediate(self, post_data: PostData) -> Dict[str, Any]:
        """Post immediately to Facebook"""
        if not self._authenticated:
            raise Exception("Not authenticated with Facebook")
        
        try:
            url = f"https://graph.facebook.com/v18.0/{self.page_id}/feed"
            
            # Prepare post data
            post_params = {
                'message': post_data.text,
                'access_token': self.access_token
            }
            
            if post_data.link:
                post_params['link'] = post_data.link
            
            # Add media if present
            if post_data.media and post_data.media[0].url:
                if post_data.post_type == PostType.IMAGE:
                    # For images, use photos endpoint
                    url = f"https://graph.facebook.com/v18.0/{self.page_id}/photos"
                    post_params['url'] = post_data.media[0].url
                elif post_data.post_type == PostType.VIDEO:
                    # For videos, use videos endpoint
                    url = f"https://graph.facebook.com/v18.0/{self.page_id}/videos"
                    post_params['file_url'] = post_data.media[0].url
            
            response = requests.post(url, data=post_params)
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    'success': True,
                    'post_id': data['id'],
                    'url': f"https://facebook.com/{data['id']}",
                    'platform': 'facebook',
                    'posted_at': datetime.now().isoformat()
                }
                logger.info(f"Successfully posted to Facebook: {result['post_id']}")
                return result
            else:
                return {
                    'success': False,
                    'error': response.text,
                    'platform': 'facebook'
                }
                
        except Exception as e:
            logger.error(f"Failed to post to Facebook: {e}")
            return {
                'success': False,
                'error': str(e),
                'platform': 'facebook'
            }
    
    def schedule_post(self, post_data: PostData) -> Dict[str, Any]:
        """Schedule a post on Facebook"""
        if not self._authenticated:
            raise Exception("Not authenticated with Facebook")
        
        try:
            url = f"https://graph.facebook.com/v18.0/{self.page_id}/feed"
            
            # Calculate scheduled publish time (Unix timestamp)
            scheduled_timestamp = int(post_data.scheduled_time.timestamp())
            
            post_params = {
                'message': post_data.text,
                'published': 'false',  # Draft mode
                'scheduled_publish_time': scheduled_timestamp,
                'access_token': self.access_token
            }
            
            if post_data.link:
                post_params['link'] = post_data.link
            
            response = requests.post(url, data=post_params)
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    'success': True,
                    'post_id': data['id'],
                    'scheduled_time': post_data.scheduled_time.isoformat(),
                    'platform': 'facebook',
                    'status': 'scheduled'
                }
                logger.info(f"Successfully scheduled Facebook post: {result['post_id']}")
                return result
            else:
                return {
                    'success': False,
                    'error': response.text,
                    'platform': 'facebook'
                }
                
        except Exception as e:
            logger.error(f"Failed to schedule Facebook post: {e}")
            return {
                'success': False,
                'error': str(e),
                'platform': 'facebook'
            }
    
    def get_post_status(self, post_id: str) -> Dict[str, Any]:
        """Get Facebook post status"""
        try:
            url = f"https://graph.facebook.com/v18.0/{post_id}"
            params = {
                'fields': 'id,message,created_time,is_published,scheduled_publish_time',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'post_id': post_id,
                    'status': 'published' if data.get('is_published') else 'scheduled',
                    'created_at': data.get('created_time'),
                    'scheduled_time': data.get('scheduled_publish_time'),
                    'platform': 'facebook'
                }
            else:
                return {
                    'success': False,
                    'error': response.text,
                    'platform': 'facebook'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': 'facebook'
            }

class InstagramPlatform(SocialMediaPlatform):
    """Instagram platform implementation (via Facebook Graph API)"""
    
    def __init__(self, credentials: Dict[str, str]):
        super().__init__(credentials)
        self.instagram_account_id = credentials.get('instagram_account_id')
        self.access_token = credentials.get('access_token')
    
    def authenticate(self) -> bool:
        """Authenticate with Instagram Graph API"""
        try:
            url = f"https://graph.facebook.com/v18.0/{self.instagram_account_id}"
            params = {'access_token': self.access_token}
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Instagram authentication successful for {data.get('username')}")
                self._authenticated = True
                return True
            else:
                logger.error(f"Instagram authentication failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Instagram authentication error: {e}")
            return False
    
    def post_immediate(self, post_data: PostData) -> Dict[str, Any]:
        """Post immediately to Instagram"""
        if not self._authenticated:
            raise Exception("Not authenticated with Instagram")
        
        try:
            # Step 1: Create media container
            container_url = f"https://graph.facebook.com/v18.0/{self.instagram_account_id}/media"
            
            container_params = {
                'caption': post_data.text,
                'access_token': self.access_token
            }
            
            # Add media based on post type
            if post_data.media and post_data.media[0].url:
                if post_data.post_type == PostType.IMAGE:
                    container_params['image_url'] = post_data.media[0].url
                elif post_data.post_type == PostType.VIDEO or post_data.post_type == PostType.REEL:
                    container_params['video_url'] = post_data.media[0].url
                    container_params['media_type'] = 'REELS' if post_data.post_type == PostType.REEL else 'VIDEO'
            
            # Create container
            container_response = requests.post(container_url, data=container_params)
            
            if container_response.status_code != 200:
                return {
                    'success': False,
                    'error': f"Failed to create media container: {container_response.text}",
                    'platform': 'instagram'
                }
            
            container_id = container_response.json()['id']
            
            # Step 2: Publish media
            publish_url = f"https://graph.facebook.com/v18.0/{self.instagram_account_id}/media_publish"
            publish_params = {
                'creation_id': container_id,
                'access_token': self.access_token
            }
            
            publish_response = requests.post(publish_url, data=publish_params)
            
            if publish_response.status_code == 200:
                data = publish_response.json()
                result = {
                    'success': True,
                    'post_id': data['id'],
                    'platform': 'instagram',
                    'posted_at': datetime.now().isoformat()
                }
                logger.info(f"Successfully posted to Instagram: {result['post_id']}")
                return result
            else:
                return {
                    'success': False,
                    'error': f"Failed to publish media: {publish_response.text}",
                    'platform': 'instagram'
                }
                
        except Exception as e:
            logger.error(f"Failed to post to Instagram: {e}")
            return {
                'success': False,
                'error': str(e),
                'platform': 'instagram'
            }
    
    def schedule_post(self, post_data: PostData) -> Dict[str, Any]:
        """Schedule a post on Instagram (limited support)"""
        # Instagram API has limited scheduling support
        # For now, store in a queue for later processing
        scheduled_post = {
            'post_data': post_data.to_dict(),
            'scheduled_time': post_data.scheduled_time.isoformat(),
            'status': 'scheduled',
            'platform': 'instagram',
            'created_at': datetime.now().isoformat()
        }
        
        # Save to scheduled posts file
        self._save_scheduled_post(scheduled_post)
        
        return {
            'success': True,
            'post_id': f"scheduled_{datetime.now().timestamp()}",
            'scheduled_time': post_data.scheduled_time.isoformat(),
            'platform': 'instagram',
            'status': 'scheduled',
            'note': 'Instagram scheduling managed locally. Use process_scheduled_posts() to publish.'
        }
    
    def _save_scheduled_post(self, post_data: Dict[str, Any]):
        """Save scheduled post to local storage"""
        scheduled_file = 'scheduled_posts.json'
        
        try:
            if os.path.exists(scheduled_file):
                with open(scheduled_file, 'r') as f:
                    scheduled_posts = json.load(f)
            else:
                scheduled_posts = []
            
            scheduled_posts.append(post_data)
            
            with open(scheduled_file, 'w') as f:
                json.dump(scheduled_posts, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save scheduled post: {e}")
    
    def get_post_status(self, post_id: str) -> Dict[str, Any]:
        """Get Instagram post status"""
        try:
            url = f"https://graph.facebook.com/v18.0/{post_id}"
            params = {
                'fields': 'id,caption,timestamp,media_type,media_url',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'post_id': post_id,
                    'status': 'published',
                    'created_at': data.get('timestamp'),
                    'media_type': data.get('media_type'),
                    'platform': 'instagram'
                }
            else:
                return {
                    'success': False,
                    'error': response.text,
                    'platform': 'instagram'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': 'instagram'
            }

class SocialMediaPoster:
    """Main social media posting orchestrator"""
    
    def __init__(self):
        self.platforms = {}
        self.load_credentials()
    
    def load_credentials(self):
        """Load credentials from environment variables"""
        # Twitter credentials
        twitter_creds = {
            'consumer_key': os.getenv('TWITTER_CONSUMER_KEY'),
            'consumer_secret': os.getenv('TWITTER_CONSUMER_SECRET'),
            'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
            'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            'bearer_token': os.getenv('TWITTER_BEARER_TOKEN')
        }
        
        # Facebook credentials
        facebook_creds = {
            'access_token': os.getenv('FACEBOOK_ACCESS_TOKEN'),
            'page_id': os.getenv('FACEBOOK_PAGE_ID')
        }
        
        # Instagram credentials
        instagram_creds = {
            'access_token': os.getenv('FACEBOOK_ACCESS_TOKEN'),  # Same as Facebook
            'instagram_account_id': os.getenv('INSTAGRAM_ACCOUNT_ID')
        }
        
        # Initialize platforms
        if all(twitter_creds.values()):
            self.platforms[Platform.TWITTER] = TwitterPlatform(twitter_creds)
        
        if all(facebook_creds.values()):
            self.platforms[Platform.FACEBOOK] = FacebookPlatform(facebook_creds)
        
        if all(instagram_creds.values()):
            self.platforms[Platform.INSTAGRAM] = InstagramPlatform(instagram_creds)
    
    def authenticate_all(self) -> Dict[Platform, bool]:
        """Authenticate with all configured platforms"""
        results = {}
        for platform, instance in self.platforms.items():
            results[platform] = instance.authenticate()
        return results
    
    def post_now(self, text: str, platform: Platform, media_url: Optional[str] = None, 
                 post_type: PostType = PostType.TEXT, hashtags: Optional[List[str]] = None,
                 link: Optional[str] = None) -> Dict[str, Any]:
        """Quick post function for immediate posting"""
        
        if platform not in self.platforms:
            return {
                'success': False,
                'error': f'Platform {platform.value} not configured',
                'platform': platform.value
            }
        
        # Create media item if URL provided
        media = None
        if media_url:
            media = [MediaItem(url=media_url, type='image' if post_type == PostType.IMAGE else 'video')]
        
        # Create post data
        post_data = PostData(
            text=text,
            platform=platform,
            post_type=post_type,
            media=media,
            hashtags=hashtags,
            link=link
        )
        
        # Post immediately
        return self.platforms[platform].post_immediate(post_data)
    
    def schedule_post(self, text: str, platform: Platform, scheduled_time: datetime,
                     media_url: Optional[str] = None, post_type: PostType = PostType.TEXT,
                     hashtags: Optional[List[str]] = None, link: Optional[str] = None) -> Dict[str, Any]:
        """Schedule a post for later"""
        
        if platform not in self.platforms:
            return {
                'success': False,
                'error': f'Platform {platform.value} not configured',
                'platform': platform.value
            }
        
        # Create media item if URL provided
        media = None
        if media_url:
            media = [MediaItem(url=media_url, type='image' if post_type == PostType.IMAGE else 'video')]
        
        # Create post data
        post_data = PostData(
            text=text,
            platform=platform,
            post_type=post_type,
            media=media,
            scheduled_time=scheduled_time,
            hashtags=hashtags,
            link=link
        )
        
        # Schedule post
        return self.platforms[platform].schedule_post(post_data)
    
    def post_from_json(self, json_file: str) -> List[Dict[str, Any]]:
        """Post from JSON configuration file"""
        try:
            with open(json_file, 'r') as f:
                posts_config = json.load(f)
            
            results = []
            
            for post_config in posts_config:
                post_data = PostData.from_dict(post_config)
                
                if post_data.platform not in self.platforms:
                    results.append({
                        'success': False,
                        'error': f'Platform {post_data.platform.value} not configured',
                        'platform': post_data.platform.value
                    })
                    continue
                
                # Post immediately or schedule
                if post_data.scheduled_time and post_data.scheduled_time > datetime.now():
                    result = self.platforms[post_data.platform].schedule_post(post_data)
                else:
                    result = self.platforms[post_data.platform].post_immediate(post_data)
                
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to process JSON file: {e}")
            return [{
                'success': False,
                'error': str(e)
            }]
    
    def process_scheduled_posts(self):
        """Process any scheduled posts that are ready to publish"""
        scheduled_file = 'scheduled_posts.json'
        
        if not os.path.exists(scheduled_file):
            return []
        
        try:
            with open(scheduled_file, 'r') as f:
                scheduled_posts = json.load(f)
            
            current_time = datetime.now()
            published_posts = []
            remaining_posts = []
            
            for post in scheduled_posts:
                scheduled_time = datetime.fromisoformat(post['scheduled_time'])
                
                if scheduled_time <= current_time:
                    # Time to publish
                    post_data = PostData.from_dict(post['post_data'])
                    
                    if post_data.platform in self.platforms:
                        result = self.platforms[post_data.platform].post_immediate(post_data)
                        result['original_scheduled_time'] = post['scheduled_time']
                        published_posts.append(result)
                    else:
                        logger.error(f"Platform {post_data.platform.value} not configured for scheduled post")
                else:
                    # Keep for later
                    remaining_posts.append(post)
            
            # Update scheduled posts file
            with open(scheduled_file, 'w') as f:
                json.dump(remaining_posts, f, indent=2)
            
            return published_posts
            
        except Exception as e:
            logger.error(f"Failed to process scheduled posts: {e}")
            return []

def create_sample_json():
    """Create a sample JSON file for batch posting"""
    sample_posts = [
        {
            "text": "🎉 Exciting news! Check out our latest holiday content!",
            "platform": "twitter",
            "post_type": "image",
            "media": [
                {
                    "url": "assets/images/holiday_2025_12_01_background_with_text.png",
                    "type": "image",
                    "alt_text": "World AIDS Day awareness image"
                }
            ],
            "hashtags": ["WorldAIDSDay", "Awareness", "Unity"],
            "scheduled_time": None
        },
        {
            "text": "Happy Thanksgiving! 🦃 Grateful for our amazing community!",
            "platform": "facebook",
            "post_type": "image",
            "media": [
                {
                    "url": "assets/images/holiday_2025_11_27_background_with_text.png",
                    "type": "image"
                }
            ],
            "hashtags": ["Thanksgiving", "Gratitude"],
            "scheduled_time": "2025-11-27T09:00:00"
        },
        {
            "text": "Starting the holiday season with hope and anticipation! ✨",
            "platform": "instagram",
            "post_type": "image",
            "media": [
                {
                    "url": "assets/images/holiday_2025_11_30_background_with_text.png",
                    "type": "image"
                }
            ],
            "hashtags": ["Advent", "Holidays", "Hope"],
            "scheduled_time": "2025-11-30T08:00:00"
        }
    ]
    
    with open('sample_posts.json', 'w') as f:
        json.dump(sample_posts, f, indent=2)
    
    logger.info("Created sample_posts.json with example post configurations")

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Social Media Poster')
    parser.add_argument('--text', help='Post text content')
    parser.add_argument('--platform', choices=['twitter', 'facebook', 'instagram'], 
                       help='Target platform')
    parser.add_argument('--media', help='URL or path to media file')
    parser.add_argument('--type', choices=['text', 'image', 'video', 'reel'], 
                       default='text', help='Post type')
    parser.add_argument('--hashtags', nargs='+', help='Hashtags (without #)')
    parser.add_argument('--link', help='Link to include')
    parser.add_argument('--schedule', help='Schedule time (YYYY-MM-DD HH:MM)')
    parser.add_argument('--json-file', help='Post from JSON file')
    parser.add_argument('--process-scheduled', action='store_true', 
                       help='Process scheduled posts')
    parser.add_argument('--create-sample', action='store_true', 
                       help='Create sample JSON file')
    parser.add_argument('--authenticate', action='store_true', 
                       help='Test authentication with all platforms')
    
    args = parser.parse_args()
    
    poster = SocialMediaPoster()
    
    if args.create_sample:
        create_sample_json()
        return
    
    if args.authenticate:
        results = poster.authenticate_all()
        for platform, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"{platform.value}: {status}")
        return
    
    if args.process_scheduled:
        results = poster.process_scheduled_posts()
        print(f"Processed {len(results)} scheduled posts")
        for result in results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result.get('platform', 'unknown')}: {result.get('post_id', result.get('error'))}")
        return
    
    if args.json_file:
        results = poster.post_from_json(args.json_file)
        for result in results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result.get('platform', 'unknown')}: {result.get('post_id', result.get('error'))}")
        return
    
    if not args.text or not args.platform:
        parser.print_help()
        return
    
    # Single post
    platform = Platform(args.platform)
    post_type = PostType(args.type)
    
    scheduled_time = None
    if args.schedule:
        scheduled_time = datetime.strptime(args.schedule, '%Y-%m-%d %H:%M')
    
    if scheduled_time and scheduled_time > datetime.now():
        result = poster.schedule_post(
            text=args.text,
            platform=platform,
            scheduled_time=scheduled_time,
            media_url=args.media,
            post_type=post_type,
            hashtags=args.hashtags,
            link=args.link
        )
    else:
        result = poster.post_now(
            text=args.text,
            platform=platform,
            media_url=args.media,
            post_type=post_type,
            hashtags=args.hashtags,
            link=args.link
        )
    
    status = "✅" if result['success'] else "❌"
    print(f"{status} {result.get('platform', 'unknown')}: {result.get('post_id', result.get('error'))}")

if __name__ == "__main__":
    main()
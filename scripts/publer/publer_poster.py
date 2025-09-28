#!/usr/bin/env python3
"""
Publer API Social Media Poster
Publishes posts to multiple social media platforms using Publer API
"""

import os
import requests
import json
import random
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

class PublerPoster:
    def __init__(self):
        self.api_key = os.getenv('PUBLER_API_KEY')
        self.base_url = "https://app.publer.com/api/v1"
        self.workspace_id = None
        self.accounts = {}

        if not self.api_key:
            raise ValueError("PUBLER_API_KEY not found in environment variables")

        # Set up session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer-API {self.api_key}',
            'Content-Type': 'application/json'
        })

    def get_workspaces(self):
        """Get all available workspaces"""
        try:
            response = self.session.get(f"{self.base_url}/workspaces")
            response.raise_for_status()
            workspaces = response.json()

            if workspaces and len(workspaces) > 0:
                self.workspace_id = workspaces[0]['id']
                print(f"✅ Using workspace: {workspaces[0]['name']} (ID: {self.workspace_id})")
                # Set workspace ID header for future requests
                self.session.headers['Publer-Workspace-Id'] = str(self.workspace_id)
                return workspaces
            else:
                raise Exception("No workspaces found")

        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting workspaces: {e}")
            return None

    def get_accounts(self):
        """Get all connected social media accounts"""
        if not self.workspace_id:
            print("❌ No workspace selected. Call get_workspaces() first.")
            return None

        try:
            response = self.session.get(f"{self.base_url}/accounts")
            response.raise_for_status()
            accounts = response.json()

            # Organize accounts by platform
            for account in accounts:
                # Map account types to platform names
                account_type = account.get('type', '')
                if account_type == 'fb_page':
                    platform = 'facebook'
                elif account_type == 'ig_business':
                    platform = 'instagram'
                elif account_type == 'twitter':
                    platform = 'twitter'
                elif account_type == 'linkedin':
                    platform = 'linkedin'
                else:
                    platform = account.get('platform', 'unknown')

                if platform not in self.accounts:
                    self.accounts[platform] = []
                self.accounts[platform].append(account)

            print(f"✅ Found accounts for platforms: {list(self.accounts.keys())}")
            return accounts

        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting accounts: {e}")
            return None

    def upload_media(self, file_path):
        """Upload media file to Publer"""
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None

        try:
            # Note: This is a placeholder - actual media upload endpoint may differ
            # Based on documentation, media upload might require different handling
            with open(file_path, 'rb') as f:
                files = {'file': f}
                # Remove Content-Type header for file upload
                headers = {k: v for k, v in self.session.headers.items() if k != 'Content-Type'}

                response = requests.post(
                    f"{self.base_url}/media/upload",
                    files=files,
                    headers=headers
                )

                if response.status_code == 200:
                    media_data = response.json()
                    print(f"✅ Media uploaded: {file_path}")
                    return media_data
                else:
                    print(f"❌ Media upload failed: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            print(f"❌ Error uploading media: {e}")
            return None

    def create_post(self, text, platforms=None, media_path=None, schedule_time=None):
        """
        Create a post for specified platforms

        Args:
            text (str): Post content text
            platforms (list): List of platforms to post to ['facebook', 'instagram', 'twitter', etc.]
            media_path (str): Path to media file (image/video)
            schedule_time (datetime): When to schedule the post (None for immediate)
        """
        if platforms is None:
            platforms = ['facebook']  # Default to Facebook

        # Build post networks configuration
        networks = {}
        for platform in platforms:
            if platform == 'facebook':
                networks['facebook'] = {
                    'type': 'photo' if media_path else 'status',
                    'text': text
                }
            elif platform == 'instagram':
                networks['instagram'] = {
                    'type': 'photo' if media_path else 'status',
                    'text': text
                }
            elif platform == 'twitter':
                networks['twitter'] = {
                    'type': 'photo' if media_path else 'status',
                    'text': text
                }
            elif platform == 'linkedin':
                networks['linkedin'] = {
                    'type': 'photo' if media_path else 'status',
                    'text': text
                }

        # Handle media upload if provided
        media_data = None
        if media_path:
            media_data = self.upload_media(media_path)
            if media_data:
                # Add media to networks (implementation depends on API response)
                for platform in networks:
                    networks[platform]['media'] = [media_data]

        # Get account IDs for the specified platforms
        post_accounts = []
        for platform in platforms:
            if platform in self.accounts:
                for account in self.accounts[platform]:
                    account_config = {'id': account['id']}

                    # Add scheduling if specified
                    if schedule_time:
                        account_config['scheduled_at'] = schedule_time.isoformat()

                    post_accounts.append(account_config)

        if not post_accounts:
            print(f"❌ No accounts found for platforms: {platforms}")
            return None

        # Build the post payload
        post_data = {
            'bulk': {
                'posts': [{
                    'networks': networks,
                    'accounts': post_accounts
                }]
            }
        }

        try:
            response = self.session.post(
                f"{self.base_url}/posts/schedule",
                json=post_data
            )
            response.raise_for_status()
            result = response.json()

            print(f"✅ Post created successfully!")
            if 'job_id' in result:
                job_status = self.check_job_status(result['job_id'])
                return result
            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating post: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None

    def create_post_with_media(self, text, platforms, media_id=None, post_type='post', schedule_time=None, immediate=True, auto_delete=None, signature_id=None):
        """
        Create a post with media for specified platforms

        Args:
            text (str): Post content text
            platforms (list): List of platforms ['facebook', 'instagram']
            media_id (str): Media ID from Publer library
            post_type (str): Type of post ('post', 'reel', 'story')
            schedule_time (datetime): When to schedule (None for immediate)
            immediate (bool): True for immediate publishing, False for scheduled
            auto_delete (dict): Auto-delete config {'duration': int, 'unit': str} (None for no auto-delete)
            signature_id (str): Signature ID to add to posts (None for no signature)
        """
        # Get account IDs for the specified platforms
        post_accounts = []
        for platform in platforms:
            if platform in self.accounts:
                for account in self.accounts[platform]:
                    account_config = {'id': account['id']}

                    # Add scheduling if specified (only for scheduled posts)
                    if schedule_time and not immediate:
                        # Ensure timezone is included in ISO format
                        if schedule_time.tzinfo is None:
                            # If no timezone, assume local timezone
                            import time
                            import datetime
                            local_offset = time.timezone if (time.daylight == 0) else time.altzone
                            local_offset = datetime.timedelta(seconds=-local_offset)
                            schedule_time = schedule_time.replace(tzinfo=datetime.timezone(local_offset))
                        account_config['scheduled_at'] = schedule_time.isoformat()

                    # Add auto-delete if specified (for both immediate and scheduled)
                    if auto_delete:
                        account_config['delete'] = {
                            'hide': False,
                            'delay': {
                                'duration': auto_delete['duration'],
                                'unit': auto_delete['unit']
                            }
                        }

                    # Add signature if specified (not supported on Twitter/X and Bluesky)
                    if signature_id and platform not in ['twitter', 'bluesky']:
                        account_config['signature'] = signature_id

                    post_accounts.append(account_config)

        if not post_accounts:
            print(f"❌ No accounts found for platforms: {platforms}")
            return None

        # Build networks configuration based on post type
        networks = {}
        for platform in platforms:
            if platform == 'facebook':
                if post_type == 'reel':
                    networks['facebook'] = {
                        'type': 'reel',
                        'text': text
                    }
                else:
                    # Facebook: 'video' for video media, 'photo' for images, 'status' for text-only
                    content_type = 'video' if media_id else 'status'
                    networks['facebook'] = {
                        'type': content_type,
                        'text': text
                    }
            elif platform == 'instagram':
                if post_type == 'reel':
                    networks['instagram'] = {
                        'type': 'reel',
                        'text': text
                    }
                else:
                    # Instagram: 'video' for video media, 'photo' for images (no 'status' type supported)
                    content_type = 'video' if media_id else 'photo'  # Default to 'photo' since Instagram doesn't support 'status'
                    networks['instagram'] = {
                        'type': content_type,
                        'text': text
                    }
            elif platform == 'twitter':
                # Twitter: 'video' for video media, 'photo' for images, 'status' for text-only
                content_type = 'video' if media_id else 'status'
                networks['twitter'] = {
                    'type': content_type,
                    'text': text
                }

        # Add media to networks if provided
        if media_id:
            for platform in networks:
                if 'media' not in networks[platform]:
                    networks[platform]['media'] = []
                # Include type field as required by API
                networks[platform]['media'].append({
                    'id': media_id,
                    'type': 'video'  # Assuming video since we're using branded videos
                })

        # Build the post payload
        post_data = {
            'bulk': {
                'posts': [{
                    'networks': networks,
                    'accounts': post_accounts
                }]
            }
        }

        # Choose endpoint and set state based on publishing mode
        if immediate:
            endpoint = f"{self.base_url}/posts/schedule/publish"
            post_data['bulk']['state'] = 'scheduled'  # Required even for immediate
        else:
            endpoint = f"{self.base_url}/posts/schedule"
            post_data['bulk']['state'] = 'scheduled'

        try:
            response = self.session.post(endpoint, json=post_data)
            response.raise_for_status()
            result = response.json()

            print(f"✅ {post_type.title()} post created successfully for {', '.join(platforms)}!")
            if auto_delete:
                print(f"⏰ Auto-delete scheduled for: {auto_delete['duration']} {auto_delete['unit']}(s) from post time")

            if 'job_id' in result:
                job_status = self.check_job_status(result['job_id'])
                return result
            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating {post_type} post: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None

    def check_job_status(self, job_id, max_wait=60):
        """Check the status of a scheduled post job"""
        print(f"🔄 Checking job status: {job_id}")

        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                response = self.session.get(f"{self.base_url}/job_status/{job_id}")
                response.raise_for_status()
                status = response.json()

                job_status = status.get('status', 'unknown')
                print(f"📊 Job status: {job_status}")

                if job_status in ['complete', 'completed', 'failed']:
                    return status

                time.sleep(5)  # Wait 5 seconds before checking again

            except requests.exceptions.RequestException as e:
                print(f"❌ Error checking job status: {e}")
                break

        print(f"⏰ Job status check timeout after {max_wait} seconds")
        return None

    def get_media(self, page=0, media_types=None, search=None):
        """Get media from library"""
        params = {
            'page': page,
            'used[]': ['false', 'true']  # Include both used and unused media
        }
        if media_types:
            for media_type in media_types:
                params[f'types[]'] = media_type
        if search:
            params['search'] = search

        try:
            response = self.session.get(f"{self.base_url}/media", params=params)
            print(f"🔍 Media API Status: {response.status_code}")
            print(f"🔍 Media API Headers: {dict(response.headers)}")

            if response.status_code == 403:
                print(f"❌ 403 Forbidden - API key may be missing 'media' scope")
                print(f"Response: {response.text}")
                return None

            response.raise_for_status()
            media_data = response.json()

            print(f"✅ Retrieved {len(media_data.get('media', []))} media items")
            print(f"📊 Total media count: {media_data.get('total', 0)}")
            return media_data

        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting media: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            return None

    def get_posts(self, limit=10, post_state=None):
        """Get recent posts"""
        params = {'limit': limit}
        if post_state:
            params['post_state'] = post_state

        try:
            response = self.session.get(f"{self.base_url}/posts", params=params)
            response.raise_for_status()
            posts = response.json()

            print(f"✅ Retrieved {len(posts)} posts")
            return posts

        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting posts: {e}")
            return None

    def get_signatures(self, account_ids=None):
        """Get available signatures for accounts"""
        if not self.workspace_id:
            print("❌ No workspace selected. Call get_workspaces() first.")
            return None

        try:
            url = f"{self.base_url}/workspaces/{self.workspace_id}/signatures"
            params = {}

            # Add account IDs filter if provided
            if account_ids:
                if isinstance(account_ids, str):
                    account_ids = [account_ids]
                for account_id in account_ids:
                    params[f'account_ids[]'] = account_id

            response = self.session.get(url, params=params)
            response.raise_for_status()
            signatures = response.json()

            print(f"✅ Retrieved {len(signatures)} signatures")
            return signatures

        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting signatures: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            return None

    def get_default_signature(self, platforms=None):
        """Get the first available signature for specified platforms"""
        if platforms is None:
            platforms = ['facebook', 'instagram']

        # Get account IDs for the platforms
        account_ids = []
        for platform in platforms:
            if platform in self.accounts:
                for account in self.accounts[platform]:
                    account_ids.append(account['id'])

        if not account_ids:
            print(f"❌ No accounts found for platforms: {platforms}")
            return None

        signatures = self.get_signatures(account_ids)
        if signatures and len(signatures) > 0:
            default_sig = signatures[0]
            print(f"✅ Using default signature: {default_sig.get('name', 'Unnamed')}")
            return default_sig['id']

        print("❌ No signatures found")
        return None


    def select_random_branded_video(self):
        """Select a random video from Publer library"""
        try:
            # Get video media from Publer
            media_data = self.get_media(page=0, media_types=['video'])
            if not media_data or len(media_data.get('media', [])) == 0:
                return None

            # Filter videos with naming convention
            video_pattern = re.compile(r'^\d+_.*\.mp4$')
            videos = []

            for media_item in media_data.get('media', []):
                filename = media_item.get('name', '') or media_item.get('filename', '')
                if video_pattern.match(filename):
                    videos.append(media_item)

            if videos:
                selected = random.choice(videos)
                return selected
            return None

        except Exception as e:
            print(f"⚠️ Could not select random video: {e}")
            return None

def main():
    """Example usage of PublerPoster"""
    try:
        # Initialize poster
        poster = PublerPoster()

        # Get workspaces and accounts
        workspaces = poster.get_workspaces()
        if not workspaces:
            return

        accounts = poster.get_accounts()
        if not accounts:
            return

        # Test media API access
        print("\n🎬 Testing media API access...")
        media = poster.get_media(page=0)

        # Try searching for uploaded videos
        if not media or len(media.get('media', [])) == 0:
            print("\n🔍 Searching for video files specifically...")
            video_media = poster.get_media(media_types=['video'])

        # Get recent posts
        recent_posts = poster.get_posts(limit=5)

    except Exception as e:
        print(f"❌ Error in main: {e}")

if __name__ == "__main__":
    main()
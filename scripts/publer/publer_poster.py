#!/usr/bin/env python3
"""
Publer API Social Media Poster
Publishes posts to multiple social media platforms using Publer API
"""

import os
import requests
import json
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

                if job_status in ['completed', 'failed']:
                    return status

                time.sleep(5)  # Wait 5 seconds before checking again

            except requests.exceptions.RequestException as e:
                print(f"❌ Error checking job status: {e}")
                break

        print(f"⏰ Job status check timeout after {max_wait} seconds")
        return None

    def get_media(self, page=0, media_types=None, search=None):
        """Get media from library"""
        params = {'page': page}
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

        # Example: Create a simple text post
        text_post = poster.create_post(
            text="Hello from MiCasa.Rentals! 🏖️ Experience the best of Pensacola Beach with our luxury vacation rentals.",
            platforms=['facebook'],  # Add more platforms as needed
            schedule_time=datetime.now() + timedelta(minutes=5)  # Schedule 5 minutes from now
        )

        # Example: Create a post with media
        # media_post = poster.create_post(
        #     text="Check out this amazing sunset view from our Pensacola Beach rental! 🌅",
        #     platforms=['facebook', 'instagram'],
        #     media_path='path/to/your/image.jpg',
        #     schedule_time=datetime.now() + timedelta(hours=1)
        # )

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
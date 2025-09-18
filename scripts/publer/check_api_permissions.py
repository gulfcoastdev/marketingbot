#!/usr/bin/env python3
"""
Publer API Permission Checker
Diagnoses API key permissions and provides setup instructions
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_publer_api_permissions():
    """Check what permissions the current API key has"""
    api_key = os.getenv('PUBLER_API_KEY')

    if not api_key:
        print("❌ PUBLER_API_KEY not found in environment variables")
        return False

    base_url = "https://app.publer.com/api/v1"
    headers = {
        'Authorization': f'Bearer-API {api_key}',
        'Content-Type': 'application/json'
    }

    print("🔑 Testing Publer API Key Permissions")
    print("=" * 50)

    # Test workspaces (should work)
    print("\n1. Testing 'workspaces' scope...")
    try:
        response = requests.get(f"{base_url}/workspaces", headers=headers)
        if response.status_code == 200:
            workspaces = response.json()
            print(f"✅ Workspaces: {len(workspaces)} found")
            if workspaces:
                workspace_id = workspaces[0]['id']
                headers['Publer-Workspace-Id'] = str(workspace_id)
                print(f"   Using workspace: {workspaces[0]['name']}")
        else:
            print(f"❌ Workspaces: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Workspaces error: {e}")

    # Test accounts (should work)
    print("\n2. Testing 'accounts' scope...")
    try:
        response = requests.get(f"{base_url}/accounts", headers=headers)
        if response.status_code == 200:
            accounts = response.json()
            print(f"✅ Accounts: {len(accounts)} found")
        else:
            print(f"❌ Accounts: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Accounts error: {e}")

    # Test posts (should work)
    print("\n3. Testing 'posts' scope...")
    try:
        response = requests.get(f"{base_url}/posts", headers=headers, params={'limit': 1})
        if response.status_code == 200:
            posts = response.json()
            print(f"✅ Posts: {len(posts)} found")
        else:
            print(f"❌ Posts: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Posts error: {e}")

    # Test media (likely to fail)
    print("\n4. Testing 'media' scope...")
    try:
        response = requests.get(f"{base_url}/media", headers=headers)
        if response.status_code == 200:
            media_data = response.json()
            media_count = len(media_data.get('media', []))
            total_count = media_data.get('total', 0)
            print(f"✅ Media: {media_count} items retrieved, {total_count} total")

            if media_count == 0 and total_count == 0:
                print("⚠️  No media found - this could mean:")
                print("   - No media uploaded to library")
                print("   - API key missing 'media' scope")
                print("   - Media in different workspace")
        elif response.status_code == 403:
            print(f"❌ Media: 403 Forbidden - API key missing 'media' scope")
        else:
            print(f"❌ Media: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Media error: {e}")

    print("\n" + "=" * 50)
    print("📋 API Key Setup Instructions:")
    print("1. Go to https://app.publer.com/account/api")
    print("2. Create a new API key or edit existing one")
    print("3. Make sure to select these scopes:")
    print("   ✓ workspaces")
    print("   ✓ accounts")
    print("   ✓ posts")
    print("   ✓ media  ← This scope is required for media access!")
    print("4. Copy the new API key to your .env file")
    print("5. Re-run this script to verify permissions")

if __name__ == "__main__":
    check_publer_api_permissions()
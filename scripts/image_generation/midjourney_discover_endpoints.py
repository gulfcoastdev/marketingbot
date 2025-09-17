#!/usr/bin/env python3
"""
Discover available Midjourney API endpoints
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('MIDJOURNEY_API_KEY')
headers = {
    "api-key": api_key,
    "Content-Type": "application/json"
}

base_url = "https://api.userapi.ai"

# Common API endpoint patterns to test
endpoints_to_discover = [
    "/midjourney",
    "/midjourney/v1",  
    "/midjourney/v2",
    "/midjourney/v2/info",
    "/midjourney/v2/status",
    "/midjourney/v2/queue",
    "/midjourney/v2/list",
    "/midjourney/v2/account",
    "/midjourney/info",
    "/info",
    "/status",
    "/account",
    "/balance"
]

print("🔍 Discovering available endpoints...")
print(f"Base URL: {base_url}")
print(f"API Key: {api_key[:8]}...")

for endpoint in endpoints_to_discover:
    url = f"{base_url}{endpoint}"
    print(f"\n🌐 Testing: {endpoint}")
    
    try:
        # Try GET first
        response = requests.get(url, headers=headers, timeout=10)
        print(f"  GET {response.status_code}: ", end="")
        
        if response.status_code == 200:
            print(f"✅ SUCCESS!")
            try:
                json_resp = response.json()
                print(f"      Response: {json_resp}")
            except:
                print(f"      Text: {response.text[:100]}")
        elif response.status_code == 404:
            print("404 Not Found")
        elif response.status_code == 405:
            print("405 Method Not Allowed (endpoint exists, wrong method)")
        else:
            print(f"Status {response.status_code}")
            print(f"      Response: {response.text[:100]}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "="*50)
print("Summary: Look for endpoints that returned 200 (success) or 405 (wrong method)")
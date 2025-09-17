#!/usr/bin/env python3
"""
Simple test script to understand the Midjourney API response
"""

import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('MIDJOURNEY_API_KEY')
print(f"API Key: {api_key}")

headers = {
    "api-key": api_key,
    "Content-Type": "application/json"
}

# Test the imagine endpoint
payload = {
    "prompt": "simple test image of a red apple"
}

print("🔗 Testing imagine endpoint...")
response = requests.post(
    "https://api.userapi.ai/midjourney/v2/imagine",
    headers=headers,
    json=payload,
    timeout=30
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    result = response.json()
    hash_id = result.get('hash')
    print(f"Hash ID: {hash_id}")
    
    # Test different result endpoints
    test_endpoints = [
        f"https://api.userapi.ai/midjourney/v2/result/{hash_id}",
        f"https://api.userapi.ai/midjourney/v2/result?hash={hash_id}",
        f"https://api.userapi.ai/midjourney/v2/status/{hash_id}",
        f"https://api.userapi.ai/midjourney/result/{hash_id}",
        f"https://api.userapi.ai/midjourney/v2/{hash_id}",
        f"https://api.userapi.ai/result/{hash_id}"
    ]
    
    print(f"\n🔍 Testing result endpoints with hash: {hash_id}")
    for endpoint in test_endpoints:
        print(f"Testing: {endpoint}")
        try:
            r = requests.get(endpoint, headers=headers, timeout=10)
            print(f"  Status: {r.status_code}")
            if r.status_code == 200:
                print(f"  ✅ SUCCESS! Response: {r.text[:200]}...")
                break
            elif r.status_code != 404:
                print(f"  ⚠️  Response: {r.text[:100]}...")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        print()
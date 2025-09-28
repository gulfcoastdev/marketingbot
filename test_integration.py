#!/usr/bin/env python3
"""
Integration test script - run before making changes to ensure functionality
"""
import os
import sys
import subprocess
from datetime import datetime

def run_test(command, description, timeout=30):
    """Run a test command and return result"""
    print(f"\n🧪 Testing: {description}")
    print(f"📝 Command: {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        if result.returncode == 0:
            print(f"✅ PASS: {description}")
            return True
        else:
            print(f"❌ FAIL: {description}")
            print(f"Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: {description} (exceeded {timeout}s)")
        return False
    except Exception as e:
        print(f"💥 ERROR: {description} - {str(e)}")
        return False

def main():
    print("🚀 Running Marketing Bot Integration Tests")
    print(f"⏰ Started at: {datetime.now()}")

    # Activate virtual environment first
    activate_cmd = "source pensacola_scraper_env/bin/activate"

    tests = [
        # Test 1: Basic imports
        (f"{activate_cmd} && python3 -c 'from scripts.social_media_automation import SocialMediaAutomation; print(\"Import OK\")'",
         "Import SocialMediaAutomation class", 10),

        # Test 2: Publer API connection
        (f"{activate_cmd} && python3 -c 'from scripts.publer.publer_poster import PublerPoster; p = PublerPoster(); p.get_workspaces(); print(\"Publer OK\")'",
         "Publer API connection", 15),

        # Test 3: Media selection
        (f"{activate_cmd} && python3 -c 'from scripts.social_media_automation import SocialMediaAutomation; s = SocialMediaAutomation(); m = s.select_random_media(); print(f\"Media: {{m.get(\"name\", \"None\") if m else \"None\"}}\")'",
         "Media selection", 20),

        # Test 4: Fact generation (dry run)
        (f"{activate_cmd} && python3 scripts/social_media_automation.py --fact --dry-run",
         "Fact generation (dry run)", 30),

        # Test 5: Events scraping (dry run)
        (f"{activate_cmd} && python3 scripts/social_media_automation.py --dry-run",
         "Events scraping (dry run)", 60),
    ]

    results = []
    for command, description, timeout in tests:
        success = run_test(command, description, timeout)
        results.append((description, success))

    # Summary
    print(f"\n📊 Test Results Summary:")
    passed = sum(1 for _, success in results if success)
    total = len(results)

    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {description}")

    print(f"\n📈 Score: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED - Safe to make changes!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - Do not make changes until fixed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
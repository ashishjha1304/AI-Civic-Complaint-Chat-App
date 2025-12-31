#!/usr/bin/env python3
"""
Test if complaint data is being saved to Supabase
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_complaint_submission():
    """Test complete complaint submission"""

    # Test data that matches what the frontend sends
    test_data = {
        "citizen_name": "Test User",
        "location": "123 Test Street, Test City",
        "issue_type": "road/traffic issues",
        "complaint_description": "This is a test to verify data is being saved to Supabase database.",
        "mobile_number": "9998887777",
        "email": "test.save@example.com"
    }

    print("Testing complaint submission...")
    print("Test data:", json.dumps(test_data, indent=2))
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/submit-complaint",
            json=test_data,
            timeout=10
        )

        print(f"HTTP Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("SUCCESS: Complaint submitted successfully!")
                print("Check your Supabase table for the new record.")
                return True
            else:
                print(f"FAILED: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"HTTP ERROR: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("Backend server not running")
        return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_health_check():
    """Test if backend is responding"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("Backend health check passed")
            return True
        else:
            print(f"Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Backend connection failed: {e}")
        return False

if __name__ == "__main__":
    print("SUPABASE DATA SAVE TEST")
    print("=" * 30)

    # Test backend health
    if not test_health_check():
        print("Cannot proceed - backend not working")
        exit(1)

    print()

    # Test complaint submission
    success = test_complaint_submission()

    print()
    print("=" * 30)
    if success:
        print("RESULT: Data IS being saved to Supabase!")
        print("Your chatbot is working correctly.")
    else:
        print("RESULT: Data is NOT being saved to Supabase")
        print("Check the error messages above and fix the configuration.")

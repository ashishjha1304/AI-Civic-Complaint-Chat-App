#!/usr/bin/env python3
"""
Simple test to check if data saves to Supabase
"""

import requests
import json
import os

BASE_URL = "http://localhost:8000"

def check_env():
    """Check if .env file exists"""
    env_path = "backend/.env"
    if os.path.exists(env_path):
        print("OK: .env file exists")
        with open(env_path, 'r') as f:
            content = f.read()
            if "SUPABASE_URL" in content and "SUPABASE_KEY" in content:
                print("OK: Supabase credentials appear to be configured")
                return True
            else:
                print("ERROR: Supabase credentials not found in .env")
                return False
    else:
        print("ERROR: .env file does not exist in backend/ directory")
        print("Please create it with your Supabase credentials:")
        print("SUPABASE_URL=https://your-project.supabase.co")
        print("SUPABASE_KEY=your-anon-key")
        return False

def test_backend():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("OK: Backend is running")
            return True
        else:
            print(f"ERROR: Backend returned status {response.status_code}")
            return False
    except:
        print("ERROR: Cannot connect to backend")
        print("Start it with: python backend/run.py")
        return False

def test_submission():
    """Test complaint submission"""
    test_data = {
        "citizen_name": "Test User",
        "location": "123 Test Street",
        "issue_type": "road/traffic issues",
        "complaint_description": "This is a test complaint to check if data saves to Supabase",
        "mobile_number": "9998887777",
        "email": "test@example.com"
    }

    print("Submitting test complaint...")
    try:
        response = requests.post(f"{BASE_URL}/submit-complaint", json=test_data, timeout=10)
        print(f"HTTP Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")

            if result.get("success"):
                print("SUCCESS: Complaint submitted and saved to Supabase!")
                print("Check your Supabase Table Editor for the new record")
                return True
            else:
                error = result.get("error", "Unknown error")
                print(f"FAILED: {error}")

                if "Database save failed" in error:
                    print("REASON: Supabase credentials not configured properly")
                    print("SOLUTION: Check your .env file and Supabase project")

                return False
        else:
            print(f"HTTP ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to backend server")
        return False
    except Exception as e:
        print(f"ERROR: Exception during test: {e}")
        return False

def main():
    print("SUPABASE DATA SAVING TEST")
    print("=" * 30)

    # Check environment
    env_ok = check_env()
    if not env_ok:
        return

    # Check backend
    backend_ok = test_backend()
    if not backend_ok:
        return

    # Test submission
    submission_ok = test_submission()

    print("\n" + "=" * 30)
    if submission_ok:
        print("RESULT: Data is being saved to Supabase successfully!")
        print("Your chatbot is working correctly.")
    else:
        print("RESULT: Data is NOT being saved to Supabase")
        print("Check the errors above and fix the configuration.")

if __name__ == "__main__":
    main()

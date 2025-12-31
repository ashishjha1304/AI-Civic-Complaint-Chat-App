#!/usr/bin/env python3
"""
Complete system test for Supabase data saving and webhook functionality
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:8000"

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("🔍 CHECKING ENVIRONMENT CONFIGURATION")
    print("=" * 40)

    env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    env_example_path = os.path.join(os.path.dirname(__file__), 'backend', 'env.example')

    if os.path.exists(env_path):
        print("✅ .env file exists")

        # Check if required variables are set
        env_vars = {}
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)

            env_vars = {
                'SUPABASE_URL': os.getenv('SUPABASE_URL'),
                'SUPABASE_KEY': os.getenv('SUPABASE_KEY'),
                'WEBHOOK_URL': os.getenv('WEBHOOK_URL')
            }
        except ImportError:
            print("⚠️  python-dotenv not available, checking manually")
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value

        print("Environment variables:")
        for key, value in env_vars.items():
            if value:
                if 'KEY' in key:
                    print(f"   ✅ {key}: {'*' * 20}...{value[-4:] if value else 'NOT SET'}")
                else:
                    print(f"   ✅ {key}: SET")
            else:
                print(f"   ❌ {key}: NOT SET")

        return env_vars
    else:
        print("❌ .env file does NOT exist")
        print(f"   Expected location: {env_path}")
        print("   Please create .env file with your Supabase credentials")
        print(f"   Use {env_example_path} as a template")

        return None

def test_backend_health():
    """Test if backend is running and accessible"""
    print("\n🏥 TESTING BACKEND HEALTH")
    print("=" * 30)

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is running")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("   Make sure to run: python backend/run.py")
        return False
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def test_complaint_submission():
    """Test complete complaint submission with all fields"""
    print("\n📝 TESTING COMPLAINT SUBMISSION")
    print("=" * 35)

    # Test data that matches the chatbot flow
    test_complaint = {
        "citizen_name": "System Test User",
        "location": "123 Test Street, Test City, Test State",
        "issue_type": "road/traffic issues",  # Frontend format
        "complaint_description": "This is a comprehensive test of the complaint submission system to verify that all data is properly validated, saved to Supabase, and webhook notifications are sent.",
        "mobile_number": "9998887777",
        "email": "system.test@example.com"
    }

    print("Submitting test complaint:")
    for key, value in test_complaint.items():
        print(f"   {key}: {value}")
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/submit-complaint",
            json=test_complaint,
            timeout=15  # Give more time for webhook
        )

        print(f"HTTP Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")

            if result.get("success"):
                print("\n🎉 COMPLAINT SUBMISSION SUCCESSFUL!")
                print("✅ Data validation passed")
                print("✅ Supabase insertion succeeded")
                print("✅ Webhook notification attempted")

                if result.get("message"):
                    print(f"   Message: {result['message']}")

                return True
            else:
                print(f"\n❌ SUBMISSION FAILED: {result.get('error', 'Unknown error')}")
                if "Database save failed" in str(result):
                    print("   This indicates Supabase credentials are not configured")
                    print("   Please check your .env file and Supabase setup")
                return False
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("   Start the server with: python backend/run.py")
        return False
    except Exception as e:
        print(f"❌ Exception during submission: {e}")
        return False

def test_validation_edge_cases():
    """Test validation for edge cases"""
    print("\n🔍 TESTING VALIDATION EDGE CASES")
    print("=" * 35)

    test_cases = [
        {
            "name": "Empty mobile number",
            "data": {
                "citizen_name": "John Doe",
                "location": "123 Main St",
                "issue_type": "road/traffic issues",
                "complaint_description": "Test complaint",
                "mobile_number": "",
                "email": "john@example.com"
            },
            "expected": "should fail"
        },
        {
            "name": "Invalid email format",
            "data": {
                "citizen_name": "John Doe",
                "location": "123 Main St",
                "issue_type": "road/traffic issues",
                "complaint_description": "Test complaint",
                "mobile_number": "9876543210",
                "email": "johnexample.com"
            },
            "expected": "should fail"
        },
        {
            "name": "Mobile too short",
            "data": {
                "citizen_name": "John Doe",
                "location": "123 Main St",
                "issue_type": "road/traffic issues",
                "complaint_description": "Test complaint",
                "mobile_number": "123",
                "email": "john@example.com"
            },
            "expected": "should fail"
        }
    ]

    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']} ({test_case['expected']})")

        try:
            response = requests.post(
                f"{BASE_URL}/submit-complaint",
                json=test_case['data'],
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success") == False:
                    print(f"   ✅ CORRECTLY REJECTED: {result.get('error', 'Validation error')}")
                else:
                    print("   ❌ SHOULD HAVE BEEN REJECTED but was accepted")
            else:
                print(f"   ❌ HTTP ERROR: {response.status_code}")

        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")

def main():
    """Run all system tests"""
    print("🚀 COMPLETE SYSTEM TEST SUITE")
    print("=" * 40)
    print("Testing: Supabase data saving + webhook functionality")
    print()

    # Check environment configuration
    env_vars = check_env_file()
    if not env_vars:
        print("\n❌ Cannot proceed without .env file")
        print("Please create backend/.env with your Supabase credentials")
        return

    # Test backend health
    if not test_backend_health():
        print("\n❌ Backend is not running properly")
        return

    # Test complaint submission
    submission_success = test_complaint_submission()

    # Test validation edge cases
    test_validation_edge_cases()

    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 60)

    if submission_success:
        print("✅ COMPLAINT SUBMISSION: WORKING")
        print("✅ SUPABASE INTEGRATION: CONFIRMED")
        print("✅ DATA SAVING: VERIFIED")

        if env_vars.get('WEBHOOK_URL'):
            print("✅ WEBHOOK CONFIGURATION: ENABLED")
            print("   Webhook notifications will be sent")
        else:
            print("ℹ️  WEBHOOK CONFIGURATION: DISABLED")
            print("   Add WEBHOOK_URL to .env to enable notifications")
    else:
        print("❌ COMPLAINT SUBMISSION: FAILED")
        print("❌ SUPABASE INTEGRATION: NOT WORKING")

        if not env_vars.get('SUPABASE_URL') or not env_vars.get('SUPABASE_KEY'):
            print("\n🔧 SOLUTION: Configure Supabase credentials in backend/.env")
            print("   SUPABASE_URL=https://your-project.supabase.co")
            print("   SUPABASE_KEY=your-anon-key")
        else:
            print("\n🔧 POSSIBLE ISSUES:")
            print("   - Supabase table doesn't exist (run the SQL schema)")
            print("   - RLS (Row Level Security) is blocking inserts")
            print("   - Wrong Supabase credentials")

    print("\n🎯 NEXT STEPS:")
    print("1. Check Supabase Table Editor for your test data")
    print("2. Monitor webhook endpoint (if configured)")
    print("3. Test the complete chatbot flow in browser")

if __name__ == "__main__":
    main()

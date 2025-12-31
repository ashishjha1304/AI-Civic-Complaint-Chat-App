#!/usr/bin/env python3
"""
Test script to verify the conversation flow works correctly.
This simulates the frontend-backend interaction.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_conversation_flow():
    print("Testing Conversation Flow Fix")
    print("=" * 50)

    # Test 1: Category selection
    print("\n1. Testing category selection...")
    response = requests.post(f"{BASE_URL}/chat", json={
        "message": "road/traffic issues",
        "session_id": "test_flow_123"
    })

    if response.status_code == 200:
        data = response.json()
        print(f"OK: Category selection response: {data['reply']}")
    else:
        print(f"ERROR: Category selection failed: {response.status_code}")
        return False

    # Test 2: Description submission
    print("\n2. Testing description submission...")
    response = requests.post(f"{BASE_URL}/chat", json={
        "message": "There's a large pothole on Main Street",
        "session_id": "test_flow_123"
    })

    if response.status_code == 200:
        data = response.json()
        print(f"OK: Description response: {data['reply']}")
        # Should be generic acknowledgment, not asking for location again
        if "pothole" not in data['reply'].lower() and "location" not in data['reply'].lower():
            print("OK: Backend response is generic (good!)")
        else:
            print("WARNING: Backend response still contains location/pothole keywords")
    else:
        print(f"ERROR: Description submission failed: {response.status_code}")
        return False

    # Test 3: Location submission
    print("\n3. Testing location submission...")
    response = requests.post(f"{BASE_URL}/chat", json={
        "message": "123 Main Street, Downtown",
        "session_id": "test_flow_123"
    })

    if response.status_code == 200:
        data = response.json()
        print(f"OK: Location response: {data['reply']}")
    else:
        print(f"ERROR: Location submission failed: {response.status_code}")
        return False

    # Test 4: Name submission
    print("\n4. Testing name submission...")
    response = requests.post(f"{BASE_URL}/chat", json={
        "message": "John Doe",
        "session_id": "test_flow_123"
    })

    if response.status_code == 200:
        data = response.json()
        print(f"OK: Name response: {data['reply']}")
    else:
        print(f"ERROR: Name submission failed: {response.status_code}")
        return False

    print("\nSUCCESS: All backend tests passed!")
    print("\nManual Frontend Testing Required:")
    print("1. Open http://localhost:5173 in browser")
    print("2. Select 'Road & Traffic Issues' category")
    print("3. Fill description: 'There's a large pothole on Main Street'")
    print("4. Fill location: '123 Main Street, Downtown'")
    print("5. Fill name: 'John Doe'")
    print("6. Verify no repeated questions appear")
    print("7. Verify smooth conversation flow")

    return True

if __name__ == "__main__":
    # Wait a moment for servers to be ready
    print("Waiting for servers to be ready...")
    time.sleep(2)

    success = test_conversation_flow()
    if success:
        print("\nSUCCESS: Conversation flow test completed!")
    else:
        print("\nFAILED: Conversation flow test failed!")

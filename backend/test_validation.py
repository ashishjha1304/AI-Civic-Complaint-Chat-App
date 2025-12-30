#!/usr/bin/env python3
"""
Test script for complaint data validation functions
"""

from database import validate_complaint_data

def test_validation():
    """Test various validation scenarios"""

    print("Testing Complaint Data Validation")
    print("=" * 50)

    # Test cases
    test_cases = [
        {
            "name": "Valid complaint",
            "data": {
                "citizen_name": "John Doe",
                "location": "123 Main Street, Downtown",
                "complaint_description": "The road has a large pothole that is causing traffic issues and potential damage to vehicles.",
                "issue_type": "road_issue",
                "contact_email": "john.doe@example.com",
                "contact_phone": "1234567890",
                "priority": "high"
            },
            "expected_valid": True
        },
        {
            "name": "Invalid name - too short",
            "data": {
                "citizen_name": "A",
                "location": "123 Main Street",
                "complaint_description": "Road has potholes",
                "issue_type": "road_issue"
            },
            "expected_valid": False
        },
        {
            "name": "Invalid name - test name",
            "data": {
                "citizen_name": "test",
                "location": "123 Main Street",
                "complaint_description": "Road has potholes",
                "issue_type": "road_issue"
            },
            "expected_valid": False
        },
        {
            "name": "Invalid location - placeholder",
            "data": {
                "citizen_name": "John Doe",
                "location": "location",
                "complaint_description": "Road has potholes",
                "issue_type": "road_issue"
            },
            "expected_valid": False
        },
        {
            "name": "Invalid description - too short",
            "data": {
                "citizen_name": "John Doe",
                "location": "123 Main Street",
                "complaint_description": "Bad",
                "issue_type": "road_issue"
            },
            "expected_valid": False
        },
        {
            "name": "Invalid email",
            "data": {
                "citizen_name": "John Doe",
                "location": "123 Main Street",
                "complaint_description": "The road has a large pothole that is causing traffic issues.",
                "issue_type": "road_issue",
                "contact_email": "invalid-email"
            },
            "expected_valid": False
        },
        {
            "name": "Invalid issue type",
            "data": {
                "citizen_name": "John Doe",
                "location": "123 Main Street",
                "complaint_description": "The road has a large pothole that is causing traffic issues.",
                "issue_type": "invalid_issue"
            },
            "expected_valid": False
        },
        {
            "name": "Minimal valid complaint",
            "data": {
                "citizen_name": "Jane Smith",
                "location": "Park Avenue",
                "complaint_description": "There is a broken water pipe causing flooding in the street. This needs immediate attention as it's affecting multiple households.",
                "issue_type": "water_issue"
            },
            "expected_valid": True
        }
    ]

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 40)

        is_valid, validation_results = validate_complaint_data(test_case['data'])

        print(f"Expected: {'[VALID]' if test_case['expected_valid'] else '[INVALID]'}")
        print(f"Actual:   {'[VALID]' if is_valid else '[INVALID]'}")

        if is_valid == test_case['expected_valid']:
            print("[PASS]")
            passed += 1
        else:
            print("[FAIL]")
            failed += 1

        # Show validation details
        print("Validation Results:")
        for field, result in validation_results.items():
            status = "[OK]" if result['valid'] else "[ERROR]"
            print(f"  {status} {field}: {result['message']}")

    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("All tests passed!")
        return True
    else:
        print("Some tests failed. Please review the validation logic.")
        return False

if __name__ == "__main__":
    test_validation()

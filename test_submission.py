#!/usr/bin/env python3
"""
Test script for the new complaint submission system.
"""

import requests
import json

# Test the new submit-complaint endpoint
test_data = {
    'citizen_name': 'John Doe',
    'email': 'john.doe@example.com',
    'mobile_number': '+1234567890',
    'issue_type': 'road/traffic issues',
    'complaint_description': 'There is a large pothole on Main Street causing traffic issues and potential vehicle damage.'
}

try:
    response = requests.post('http://localhost:8000/submit-complaint', json=test_data)
    print('Status Code:', response.status_code)
    print('Response:', response.json())
except Exception as e:
    print('Error:', e)


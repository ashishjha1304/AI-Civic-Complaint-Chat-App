#!/usr/bin/env python3
"""
Test if .env file is being loaded correctly
"""

import os
from dotenv import load_dotenv

# Change to backend directory
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
os.chdir(backend_dir)

print(f"Working directory: {os.getcwd()}")
print(f".env file exists: {os.path.exists('.env')}")

# Load environment variables
load_dotenv()

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
webhook_url = os.getenv('WEBHOOK_URL')

print(f"SUPABASE_URL loaded: {'Yes' if supabase_url else 'No'}")
print(f"SUPABASE_KEY loaded: {'Yes (' + supabase_key[:20] + '...)' if supabase_key else 'No'}")
print(f"WEBHOOK_URL loaded: {'Yes' if webhook_url else 'No'}")

if supabase_url:
    print(f"Supabase URL: {supabase_url}")
if webhook_url:
    print(f"Webhook URL: {webhook_url}")

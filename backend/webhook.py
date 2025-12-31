import os
import httpx
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")


def send_webhook(payload: Dict):
    """Send complaint data to webhook"""
    if not WEBHOOK_URL:
        print("WEBHOOK_URL not set. Skipping webhook call.")
        print(f"Would send payload: {payload}")
        return
    
    try:
        response = httpx.post(
            WEBHOOK_URL,
            json=payload,
            timeout=10.0
        )
        response.raise_for_status()
        print(f"Webhook sent successfully: {response.status_code}")
    except Exception as e:
        print(f"Error sending webhook: {e}")
        # Don't fail the complaint submission if webhook fails






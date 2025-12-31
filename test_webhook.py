#!/usr/bin/env python3
"""
Test webhook functionality for complaint submissions
"""

import requests
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Global variable to store received webhooks
received_webhooks = []

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            webhook_data = json.loads(post_data.decode('utf-8'))

            print(f"\n[WEBHOOK RECEIVED] {webhook_data}")
            received_webhooks.append(webhook_data)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())

        except Exception as e:
            print(f"[WEBHOOK ERROR] {e}")
            self.send_response(500)
            self.end_headers()

def start_test_webhook_server(port=8080):
    """Start a simple webhook test server"""
    server = HTTPServer(('localhost', port), WebhookHandler)
    print(f"Test webhook server started on port {port}")
    server.serve_request()  # Handle one request and stop

def test_webhook_integration():
    """Test the complete webhook flow"""
    print("WEBHOOK INTEGRATION TEST")
    print("=" * 40)

    # Start webhook server in background
    import socket
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()

    webhook_url = f"http://localhost:{port}/webhook"

    print(f"Using webhook URL: {webhook_url}")

    # Test data
    test_complaint = {
        "citizen_name": "Webhook Test User",
        "location": "456 Test Street, Test City",
        "issue_type": "road_traffic",
        "complaint_description": "Testing webhook functionality with sample complaint data",
        "mobile_number": "9998887777",
        "email": "webhook.test@example.com"
    }

    print(f"Test complaint data: {test_complaint}")

    # Simulate the webhook call that would happen after database save
    from database import send_webhook_notification

    # Set the webhook URL for testing
    import os
    os.environ['WEBHOOK_URL'] = webhook_url

    print("\nTesting webhook notification...")

    # Start webhook server in a separate thread
    server_thread = threading.Thread(target=start_test_webhook_server, args=(port,))
    server_thread.daemon = True
    server_thread.start()

    time.sleep(1)  # Give server time to start

    # Send webhook notification
    success = send_webhook_notification(test_complaint, "test-uuid-123")

    if success:
        print("Webhook notification sent successfully!")

        # Check if we received the webhook
        if received_webhooks:
            webhook_payload = received_webhooks[0]
            print(f"\nReceived webhook payload: {json.dumps(webhook_payload, indent=2)}")

            # Verify payload structure
            if (webhook_payload.get('event') == 'complaint_submitted' and
                'complaint' in webhook_payload and
                webhook_payload['complaint']['citizen_name'] == test_complaint['citizen_name']):
                print("✅ Webhook payload structure is correct!")
                return True
            else:
                print("❌ Webhook payload structure is incorrect")
                return False
        else:
            print("❌ No webhook was received")
            return False
    else:
        print("❌ Failed to send webhook notification")
        return False

if __name__ == "__main__":
    success = test_webhook_integration()
    if success:
        print("\n✅ WEBHOOK INTEGRATION TEST PASSED!")
    else:
        print("\n❌ WEBHOOK INTEGRATION TEST FAILED!")


import os
import re
from supabase import create_client, Client
from typing import Optional, Dict, Tuple
from dotenv import load_dotenv

# Load .env file from the backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(backend_dir, '.env')
load_dotenv(env_path)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Webhook configuration
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

# Debug: Print configuration status
print(f"[CONFIG] Loading .env from: {env_path}")
print(f"[CONFIG] .env file exists: {os.path.exists(env_path)}")
print(f"[CONFIG] SUPABASE_URL configured: {'Yes' if SUPABASE_URL else 'No'}")
print(f"[CONFIG] SUPABASE_KEY configured: {'Yes' if SUPABASE_KEY else 'No'}")
print(f"[CONFIG] WEBHOOK_URL configured: {'Yes' if WEBHOOK_URL else 'No'}")

supabase: Optional[Client] = None

# In-memory session storage (for demo purposes)
session_storage: Dict[str, Dict] = {}


def validate_citizen_name(name: str) -> Tuple[bool, str]:
    """Validate citizen name - basic validation"""
    if not name or not isinstance(name, str):
        return False, "Name is required"

    name = name.strip()
    if len(name) < 2:
        return False, "Name must be at least 2 characters long"

    return True, "Valid name"


def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email address format"""
    if not email or not isinstance(email, str):
        return False, "Email is required"

    email = email.strip()
    if len(email) < 3:
        return False, "Email must be at least 3 characters long"

    # Check for @ symbol
    if '@' not in email:
        return False, "Email must contain '@' symbol"

    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Please provide a valid email address"

    return True, "Valid email"


def validate_mobile_number(phone: str) -> Tuple[bool, str]:
    """Validate mobile number"""
    if not phone or not isinstance(phone, str):
        return False, "Mobile number is required"

    phone = phone.strip()
    if not phone:
        return False, "Mobile number cannot be empty"

    # Remove common separators for validation
    clean_phone = re.sub(r'[\s\-\(\)\.]', '', phone)

    # Check minimum length (at least 10 digits)
    digits_only = clean_phone.replace('+', '')
    if len(digits_only) < 10:
        return False, "Mobile number must be at least 10 digits long"

    # Allow flexible phone number formats
    if re.match(r'^(\+\d{1,3})?\d{10,15}$', clean_phone):
        # Should not be all same digits
        if len(set(digits_only)) <= 1 and len(digits_only) > 3:
            return False, "Please provide a valid phone number"
        return True, "Valid mobile number"

    return False, "Please provide a valid mobile number"


def validate_complaint_description(description: str) -> Tuple[bool, str]:
    """Validate complaint description"""
    if not description or not isinstance(description, str):
        return False, "Description is required"

    description = description.strip()
    if len(description) < 10:
        return False, "Description must be at least 10 characters long"

    return True, "Valid description"


def validate_issue_type(issue_type: str) -> Tuple[bool, str]:
    """Validate issue type"""
    if not issue_type or not isinstance(issue_type, str):
        return False, "Issue type is required"

    valid_types = ['road/traffic issues', 'electricity/power problems',
                   'water/plumbing issues', 'garbage/waste collection']

    # Map frontend values to database values
    type_mapping = {
        'road/traffic issues': 'road_traffic',
        'electricity/power problems': 'electricity_power',
        'water/plumbing issues': 'water_plumbing',
        'garbage/waste collection': 'garbage_waste'
    }

    if issue_type in valid_types:
        return True, "Valid issue type"
    else:
        return False, f"Issue type must be one of: {', '.join(valid_types)}"


def validate_location(location: str) -> Tuple[bool, str]:
    """Validate location - basic validation"""
    if not location or not isinstance(location, str):
        return False, "Location is required"

    location = location.strip()
    if len(location) < 3:
        return False, "Location must be at least 3 characters long"

    return True, "Valid location"


def validate_complaint_data(complaint_data: Dict) -> Tuple[bool, Dict[str, str]]:
    """Validate all complaint data fields"""
    validation_results = {}
    all_valid = True

    # Required fields
    required_fields = {
        'citizen_name': validate_citizen_name,
        'location': validate_location,
        'email': validate_email,
        'mobile_number': validate_mobile_number,
        'complaint_description': validate_complaint_description,
        'issue_type': validate_issue_type
    }

    # Validate all required fields
    for field, validator in required_fields.items():
        value = complaint_data.get(field)
        is_valid, message = validator(value)
        validation_results[field] = {'valid': is_valid, 'message': message}
        if not is_valid:
            all_valid = False

    return all_valid, validation_results


def prepare_complaint_for_db(complaint_data: Dict) -> Dict:
    """Prepare complaint data for database insertion"""
    # Map frontend issue types to database values
    type_mapping = {
        'road/traffic issues': 'road_traffic',
        'electricity/power problems': 'electricity_power',
        'water/plumbing issues': 'water_plumbing',
        'garbage/waste collection': 'garbage_waste'
    }

    db_data = complaint_data.copy()
    if db_data.get('issue_type'):
        db_data['issue_type'] = type_mapping.get(db_data['issue_type'], db_data['issue_type'])

    return db_data


def get_supabase_client() -> Optional[Client]:
    """Get or create Supabase client"""
    global supabase
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("Warning: Supabase credentials not configured. Database operations will be skipped.")
            return None
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            print(f"Error creating Supabase client: {e}")
            return None
    return supabase


def send_webhook_notification(complaint_data: Dict, complaint_id: str = None) -> bool:
    """Send webhook notification after complaint submission"""
    if not WEBHOOK_URL:
        print("[WEBHOOK] Webhook URL not configured, skipping notification")
        return True  # Not an error, just not configured

    try:
        # Prepare webhook payload
        webhook_payload = {
            "event": "complaint_submitted",
            "timestamp": complaint_data.get("created_at", "2024-01-01T00:00:00Z"),
            "complaint": {
                "id": complaint_id,
                "citizen_name": complaint_data.get("citizen_name"),
                "location": complaint_data.get("location"),
                "issue_type": complaint_data.get("issue_type"),
                "complaint_description": complaint_data.get("complaint_description"),
                "mobile_number": complaint_data.get("mobile_number"),
                "email": complaint_data.get("email")
            }
        }

        print(f"[WEBHOOK] Sending notification to: {WEBHOOK_URL}")
        print(f"[WEBHOOK] Payload: {webhook_payload}")

        # Send webhook request
        import requests
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code >= 200 and response.status_code < 300:
            print("[WEBHOOK] Notification sent successfully")
            return True
        else:
            print(f"[WEBHOOK] Failed to send notification. Status: {response.status_code}, Response: {response.text}")
            return False

    except Exception as e:
        print(f"[WEBHOOK] Exception during webhook notification: {e}")
        return False


def save_complaint(complaint_data: Dict):
    """Save complaint to Supabase database"""
    try:
        print("[VALIDATION] Validating complaint data...")
        is_valid, validation_results = validate_complaint_data(complaint_data)

        if not is_valid:
            print("[VALIDATION FAILED] Complaint data validation failed:")
            for field, result in validation_results.items():
                if not result['valid']:
                    print(f"   ERROR {field}: {result['message']}")
            print(f"   Complaint data: {complaint_data}")
            return None

        print("[VALIDATION PASSED] All complaint data is valid!")

        # Prepare data for database insertion
        db_data = prepare_complaint_for_db(complaint_data)

        if not SUPABASE_URL or not SUPABASE_KEY:
            print("[ERROR] Supabase credentials not configured!")
            print("   Please create a .env file in the backend directory with:")
            print("   SUPABASE_URL=your_supabase_project_url")
            print("   SUPABASE_KEY=your_supabase_anon_key")
            return None

        client = get_supabase_client()
        if client is None:
            print("[ERROR] Failed to create Supabase client")
            return None

        # Insert data with exact column names
        insert_data = {
            "citizen_name": db_data["citizen_name"],
            "location": db_data["location"],
            "issue_type": db_data["issue_type"],
            "complaint_description": db_data["complaint_description"],
            "mobile_number": db_data["mobile_number"],
            "email": db_data["email"]
        }

        print(f"[INSERT] Attempting to insert: {insert_data}")
        result = client.table("complaints").insert(insert_data).execute()

        print("[SUCCESS] Complaint saved successfully to Supabase!")
        print(f"   Citizen: {db_data['citizen_name']}")
        print(f"   Location: {db_data['location']}")
        print(f"   Issue: {db_data['issue_type']}")
        print(f"   Description: {db_data['complaint_description'][:50]}...")
        print(f"   Mobile: {db_data['mobile_number']}")
        print(f"   Email: {db_data['email']}")

        # Send webhook notification after successful database save
        try:
            # Extract the complaint ID from the result if available
            complaint_id = None
            if hasattr(result, 'data') and result.data:
                complaint_id = result.data[0].get('id') if isinstance(result.data, list) and len(result.data) > 0 else None

            webhook_success = send_webhook_notification(db_data, complaint_id)
            if webhook_success:
                print("[SUCCESS] Webhook notification sent successfully")
            else:
                print("[WARNING] Webhook notification failed, but complaint was saved")
        except Exception as webhook_error:
            print(f"[WARNING] Webhook notification failed: {webhook_error}")
            print("[INFO] Complaint was still saved successfully to database")

        return result

    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Failed to save complaint to database: {error_msg}")
        print(f"   Complaint data: {complaint_data}")

        if "row-level security policy" in error_msg.lower():
            print("   [RLS ERROR] Supabase Row Level Security policy violation!")
            print("   Solutions:")
            print("   1. Disable RLS for the 'complaints' table (not recommended for production)")
            print("   2. Create an INSERT policy that allows authenticated users")
            print("   3. Use a service role key instead of anon key")

        return None


def get_session_state(session_id: str) -> Dict:
    """Get session state from storage"""
    if session_id not in session_storage:
        session_storage[session_id] = {
            "messages": [],
            "citizen_name": None,
            "email": None,
            "mobile_number": None,
            "complaint_description": None,
            "issue_type": None,
            "session_id": session_id,
            "completed": False
        }
    return session_storage[session_id].copy()


def save_session_state(session_id: str, state: Dict):
    """Save session state to storage"""
    session_storage[session_id] = state.copy()


def reset_session(session_id: str):
    """Reset session state for a new complaint"""
    if session_id in session_storage:
        del session_storage[session_id]
    return get_session_state(session_id)


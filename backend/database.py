import os
import re
from supabase import create_client, Client
from typing import Optional, Dict, Tuple
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

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

    # Allow flexible phone number formats
    if re.match(r'^(\+\d{1,3})?\d{3,15}$', clean_phone):
        # Should not be all same digits
        if len(set(clean_phone.replace('+', ''))) <= 1 and len(clean_phone.replace('+', '')) > 3:
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


def validate_complaint_data(complaint_data: Dict) -> Tuple[bool, Dict[str, str]]:
    """Validate all complaint data fields"""
    validation_results = {}
    all_valid = True

    # Required fields
    required_fields = {
        'citizen_name': validate_citizen_name,
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
            "email": db_data["email"],
            "mobile_number": db_data["mobile_number"],
            "issue_type": db_data["issue_type"],
            "complaint_description": db_data["complaint_description"]
        }

        print(f"[INSERT] Attempting to insert: {insert_data}")
        result = client.table("complaints").insert(insert_data).execute()

        print("[SUCCESS] Complaint saved successfully to Supabase!")
        print(f"   Citizen: {db_data['citizen_name']}")
        print(f"   Email: {db_data['email']}")
        print(f"   Mobile: {db_data['mobile_number']}")
        print(f"   Issue: {db_data['issue_type']}")
        print(f"   Description: {db_data['complaint_description'][:50]}...")

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


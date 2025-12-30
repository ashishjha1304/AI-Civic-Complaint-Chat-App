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
# In production, you might want to use Redis or database
session_storage: Dict[str, Dict] = {}


# Validation functions
def validate_citizen_name(name: str) -> Tuple[bool, str]:
    """Validate citizen name - check if it's meaningful and not just random text"""
    if not name or not isinstance(name, str):
        return False, "Name is required and must be a string"

    name = name.strip()
    if len(name) < 2:
        return False, "Name must be at least 2 characters long"

    if len(name) > 100:
        return False, "Name must be less than 100 characters"

    # Check if name contains only valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        return False, "Name can only contain letters, spaces, hyphens, and apostrophes"

    # Check if name is not just a single repeated character
    if len(set(name.replace(" ", "").lower())) <= 2:
        return False, "Please provide a meaningful name"

    # Check for obvious test/placeholder names
    test_names = ['test', 'testing', 'abc', 'xyz', 'user', 'name', 'person']
    if name.lower().strip() in test_names:
        return False, "Please provide a real name"

    return True, "Valid name"


def validate_location(location: str) -> Tuple[bool, str]:
    """Validate location - check if it's meaningful and specific enough"""
    if not location or not isinstance(location, str):
        return False, "Location is required and must be a string"

    location = location.strip()
    if len(location) < 3:
        return False, "Location must be at least 3 characters long"

    if len(location) > 200:
        return False, "Location must be less than 200 characters"

    # Check for obvious placeholder locations
    placeholder_locations = ['location', 'place', 'area', 'somewhere', 'here', 'there', 'nowhere']
    if location.lower().strip() in placeholder_locations:
        return False, "Please provide a specific location (address, area, or landmark)"

    # Check if location contains at least some meaningful content
    # Should have at least one letter
    if not re.search(r'[a-zA-Z]', location):
        return False, "Location must contain at least one letter"

    return True, "Valid location"


def validate_complaint_description(description: str) -> Tuple[bool, str]:
    """Validate complaint description - must match database constraints exactly"""
    if not description or not isinstance(description, str):
        return False, "Complaint description is required and must be a string"

    description_trimmed = description.strip()

    # Database constraint: LENGTH(TRIM(description)) >= 10
    if len(description_trimmed) < 10:
        return False, "Complaint description must be at least 10 characters long"

    # Database constraint: no upper limit in schema, but reasonable limit
    if len(description_trimmed) > 1000:
        return False, "Complaint description must be less than 1000 characters"

    return True, "Valid complaint description"


def validate_issue_type(issue_type: str) -> Tuple[bool, str]:
    """Validate issue type - must be one of the predefined categories"""
    if not issue_type or not isinstance(issue_type, str):
        return False, "Issue type is required and must be a string"

    valid_issue_types = ['road_issue', 'electricity_issue', 'water_issue', 'garbage_issue']
    if issue_type not in valid_issue_types:
        return False, f"Issue type must be one of: {', '.join(valid_issue_types)}"

    return True, "Valid issue type"


def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email address format (if provided)"""
    if not email:  # Email is optional
        return True, "Email not provided (optional)"

    if not isinstance(email, str):
        return False, "Email must be a string"

    email = email.strip()
    if len(email) > 254:  # RFC 5321 limit
        return False, "Email address is too long"

    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Please provide a valid email address (e.g., user@example.com)"

    return True, "Valid email"


def validate_phone(phone: str) -> Tuple[bool, str]:
    """Validate phone number format (if provided) - more flexible validation"""
    if not phone:  # Phone is optional
        return True, "Phone not provided (optional)"

    if not isinstance(phone, str):
        return False, "Phone number must be a string"

    phone = phone.strip()
    if not phone:  # Empty after stripping
        return True, "Phone not provided (optional)"

    # Remove common separators for validation
    clean_phone = re.sub(r'[\s\-\(\)\.]', '', phone)

    # Allow flexible phone number formats:
    # - 10 digits (standard US/India format)
    # - +country code + 10 digits
    # - At least 3 digits for partial numbers (users might provide incomplete info)
    if re.match(r'^(\+\d{1,3})?\d{3,15}$', clean_phone):
        # Additional check: should not be all same digits (like '1111111111')
        if len(set(clean_phone.replace('+', ''))) <= 1 and len(clean_phone.replace('+', '')) > 3:
            return False, "Please provide a valid phone number"
        return True, "Valid phone number"

    return False, "Please provide a valid phone number (at least 3 digits, optionally with country code like +1)"


def validate_priority(priority: str) -> Tuple[bool, str]:
    """Validate priority level"""
    if not priority:  # Priority has default value
        return True, "Priority not provided (will use default)"

    if not isinstance(priority, str):
        return False, "Priority must be a string"

    valid_priorities = ['low', 'medium', 'high', 'urgent']
    if priority not in valid_priorities:
        return False, f"Priority must be one of: {', '.join(valid_priorities)}"

    return True, "Valid priority"


def validate_assigned_department(department: str) -> Tuple[bool, str]:
    """Validate assigned department"""
    if not department:  # Department is optional
        return True, "Department not assigned (optional)"

    if not isinstance(department, str):
        return False, "Department must be a string"

    valid_departments = ['roads', 'electricity', 'water', 'sanitation', 'general']
    if department not in valid_departments:
        return False, f"Department must be one of: {', '.join(valid_departments)}"

    return True, "Valid department"


def validate_source(source: str) -> Tuple[bool, str]:
    """Validate complaint source"""
    if not source:  # Source has default value
        return True, "Source not provided (will use default)"

    if not isinstance(source, str):
        return False, "Source must be a string"

    valid_sources = ['chat', 'web', 'mobile', 'api']
    if source not in valid_sources:
        return False, f"Source must be one of: {', '.join(valid_sources)}"

    return True, "Valid source"


def validate_feedback_rating(rating: int) -> Tuple[bool, str]:
    """Validate feedback rating"""
    if rating is None:  # Rating is optional
        return True, "Rating not provided (optional)"

    if not isinstance(rating, int):
        return False, "Rating must be an integer"

    if rating < 1 or rating > 5:
        return False, "Rating must be between 1 and 5"

    return True, "Valid rating"


def validate_complaint_data(complaint_data: Dict) -> Tuple[bool, Dict[str, str]]:
    """Validate all complaint data fields and return validation results"""
    validation_results = {}
    all_valid = True

    # Required fields
    required_fields = {
        'citizen_name': validate_citizen_name,
        'location': validate_location,
        'complaint_description': validate_complaint_description,
        'issue_type': validate_issue_type
    }

    # Optional fields
    optional_fields = {
        'contact_email': validate_email,
        'contact_phone': validate_phone,
        'priority': validate_priority
    }

    # Validate required fields
    for field, validator in required_fields.items():
        value = complaint_data.get(field)
        is_valid, message = validator(value)
        validation_results[field] = {'valid': is_valid, 'message': message}
        if not is_valid:
            all_valid = False

    # Validate optional fields (only if provided)
    for field, validator in optional_fields.items():
        value = complaint_data.get(field)
        if value is not None:
            is_valid, message = validator(value)
            validation_results[field] = {'valid': is_valid, 'message': message}
            if not is_valid:
                all_valid = False

    return all_valid, validation_results


def assign_department_by_issue_type(issue_type: str) -> str:
    """Automatically assign department based on issue type"""
    department_mapping = {
        'road_issue': 'roads',
        'electricity_issue': 'electricity',
        'water_issue': 'water',
        'garbage_issue': 'sanitation'
    }
    return department_mapping.get(issue_type, 'general')


def prepare_complaint_for_db(complaint_data: Dict) -> Dict:
    """Prepare complaint data for database insertion with auto-assignments"""
    # Create a copy to avoid modifying the original
    db_data = complaint_data.copy()

    # Auto-assign department if not provided
    if not db_data.get('assigned_department'):
        db_data['assigned_department'] = assign_department_by_issue_type(db_data['issue_type'])

    # Set default source if not provided
    if not db_data.get('source'):
        db_data['source'] = 'chat'

    # Ensure priority has a default
    if not db_data.get('priority'):
        db_data['priority'] = 'medium'

    # Ensure session_id has a default
    if not db_data.get('session_id'):
        db_data['session_id'] = 'default'

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


def init_database():
    """Initialize database tables if they don't exist"""
    # Note: In production, you should create tables via Supabase dashboard or migrations
    # This is a placeholder for the schema
    pass


def save_complaint(complaint_data: Dict):
    """Save complaint to Supabase database with validation"""
    try:
        # First, validate the complaint data
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
            print("   Get these from: https://supabase.com/dashboard -> Your Project -> Settings -> API")
            print(f"   Skipping database save for complaint: {complaint_data.get('citizen_name', 'Unknown')}")
            return None

        client = get_supabase_client()
        if client is None:
            print("[ERROR] Failed to create Supabase client")
            return None

        result = client.table("complaints").insert({
            "citizen_name": db_data["citizen_name"],
            "location": db_data["location"],
            "complaint_description": db_data["complaint_description"],
            "issue_type": db_data["issue_type"],
            "status": "pending",
            "priority": db_data.get("priority", "medium"),
            "contact_email": db_data.get("contact_email"),
            "contact_phone": db_data.get("contact_phone"),
            "assigned_department": db_data.get("assigned_department"),
            "session_id": db_data.get("session_id", "default"),
            "source": db_data.get("source", "chat")
        }).execute()

        print("[SUCCESS] Complaint saved successfully to Supabase!")
        print(f"   Citizen: {db_data['citizen_name']}")
        print(f"   Issue: {db_data['issue_type']}")
        print(f"   Location: {db_data['location']}")
        print(f"   Department: {db_data.get('assigned_department', 'Not assigned')}")
        print(f"   Priority: {db_data.get('priority', 'medium')}")
        print(f"   Source: {db_data.get('source', 'chat')}")
        if db_data.get('contact_email'):
            print(f"   Email: {db_data['contact_email']}")
        if db_data.get('contact_phone'):
            print(f"   Phone: {db_data['contact_phone']}")
        return result

    except Exception as e:
        error_msg = str(e)
        if "row-level security policy" in error_msg.lower():
            print("[ERROR] Supabase Row Level Security (RLS) policy violation!")
            print("   This means the table has RLS enabled but the API key lacks INSERT permissions.")
            print("   Solutions:")
            print("   1. Disable RLS for the 'complaints' table (not recommended for production)")
            print("   2. Create an INSERT policy that allows authenticated users")
            print("   3. Use a service role key instead of anon key")
            print("   4. Configure proper authentication")
        else:
            print(f"[ERROR] Failed to save complaint to database: {error_msg}")

        print(f"   Complaint data: {complaint_data}")
        # For demo purposes, we'll continue even if database save fails
        return None


def get_session_state(session_id: str) -> Dict:
    """Get session state from storage"""
    if session_id not in session_storage:
        session_storage[session_id] = {
            "messages": [],
            "citizen_name": None,
            "location": None,
            "complaint_description": None,
            "issue_type": None,
            "contact_email": None,
            "contact_phone": None,
            "priority": None,
            "session_id": session_id,
            "last_asked_field": None
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


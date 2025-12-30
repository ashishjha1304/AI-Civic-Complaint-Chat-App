from typing import TypedDict, Annotated, Optional, Dict, List, Tuple
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import operator
from database import save_complaint, get_session_state
from webhook import send_webhook
import re


# AI-Powered Complaint Validation Functions
def classify_complaint_validity(complaint_text: str) -> Tuple[bool, str, str]:
    """
    AI-powered complaint validation using intelligent keyword analysis and context understanding.
    Determines if a complaint is appropriate for this civic complaint system.

    Returns: (is_valid, reason, suggested_action)
    """
    complaint_lower = complaint_text.lower().strip()

    # Define valid complaint categories and their keywords
    valid_categories = {
        'road_traffic': [
            'road', 'street', 'pothole', 'traffic', 'lane', 'pavement', 'sidewalk',
            'asphalt', 'highway', 'intersection', 'signal', 'light', 'traffic light',
            'speed bump', 'parking', 'driveway', 'curb', 'crosswalk', 'zebra crossing',
            'bridge', 'overpass', 'underpass', 'construction', 'repair', 'damage'
        ],
        'electricity_power': [
            'electricity', 'power', 'electrical', 'electric', 'current', 'voltage',
            'outage', 'blackout', 'power cut', 'power failure', 'short circuit',
            'wiring', 'cable', 'pole', 'transformer', 'meter', 'fuse', 'switch',
            'socket', 'plug', 'light', 'lighting', 'bulb', 'fan', 'ac', 'heater'
        ],
        'water_plumbing': [
            'water', 'plumbing', 'pipe', 'leak', 'leakage', 'tap', 'faucet',
            'drainage', 'sewer', 'sewage', 'toilet', 'bathroom', 'kitchen sink',
            'pressure', 'supply', 'burst', 'broken', 'repair', 'maintenance',
            'flood', 'overflow', 'blockage', 'clog', 'drain'
        ],
        'garbage_waste': [
            'garbage', 'waste', 'trash', 'rubbish', 'bin', 'dustbin', 'collection',
            'pickup', 'dumpster', 'landfill', 'recycling', 'compost', 'litter',
            'overflow', 'spill', 'dirty', 'filthy', 'unhygienic', 'pest', 'rat',
            'mosquito', 'smell', 'odor', 'sanitation'
        ],
        'public_safety': [
            'broken', 'damaged', 'unsafe', 'dangerous', 'hazard', 'risk',
            'accident', 'injury', 'public safety', 'emergency', 'urgent'
        ]
    }

    # Define invalid complaint categories (things we don't handle)
    invalid_categories = {
        'crime_law': [
            'robbery', 'theft', 'burglary', 'assault', 'murder', 'rape', 'violence',
            'crime', 'criminal', 'police', 'law enforcement', 'court', 'legal',
            'arrest', 'jail', 'prison', 'suspect', 'victim', 'evidence'
        ],
        'personal_business': [
            'job', 'employment', 'salary', 'boss', 'colleague', 'workplace',
            'business', 'company', 'contract', 'agreement', 'payment', 'money',
            'financial', 'bank', 'loan', 'debt', 'tax', 'insurance', 'medical',
            'health', 'doctor', 'hospital', 'medicine', 'treatment'
        ],
        'relationship_family': [
            'marriage', 'divorce', 'family', 'children', 'parent', 'spouse',
            'girlfriend', 'boyfriend', 'friend', 'neighbor', 'argument', 'fight',
            'relationship', 'love', 'breakup', 'affair', 'cheating'
        ],
        'technology_communication': [
            'internet', 'wifi', 'mobile', 'phone', 'cellphone', 'computer',
            'laptop', 'software', 'app', 'website', 'social media', 'facebook',
            'whatsapp', 'email', 'spam', 'virus', 'hack', 'password'
        ],
        'education_school': [
            'school', 'college', 'university', 'teacher', 'student', 'exam',
            'grade', 'class', 'lesson', 'homework', 'tuition', 'education',
            'admission', 'fee', 'scholarship'
        ],
        'government_admin': [
            'government', 'ministry', 'department', 'official', 'bureaucracy',
            'corruption', 'bribery', 'scam', 'fraud', 'complaint against',
            'petition', 'application', 'license', 'permit', 'certificate'
        ]
    }

    # Check for invalid categories first (higher priority)
    for category, keywords in invalid_categories.items():
        if any(keyword in complaint_lower for keyword in keywords):
            if category == 'crime_law':
                return False, "Crime and law enforcement issues", "Please contact your local police station or emergency services at 911/100/112"
            elif category == 'personal_business':
                return False, "Personal, business, or employment matters", "This system handles only civic infrastructure complaints. For personal/business issues, contact relevant authorities or HR department"
            elif category == 'relationship_family':
                return False, "Personal relationship or family matters", "This system is for reporting civic infrastructure problems only"
            elif category == 'technology_communication':
                return False, "Technology or communication issues", "For tech/communication issues, contact your service provider or IT support"
            elif category == 'education_school':
                return False, "Education or school-related matters", "Please contact your educational institution administration"
            elif category == 'government_admin':
                return False, "Government administration complaints", "For government service complaints, use the appropriate government portal or contact the relevant department directly"

    # Check for valid categories
    valid_matches = []
    for category, keywords in valid_categories.items():
        matches = [keyword for keyword in keywords if keyword in complaint_lower]
        if matches:
            valid_matches.extend(matches)

    # If we found valid keywords, it's a valid complaint
    if valid_matches:
        # Determine the primary category
        if any(k in complaint_lower for k in valid_categories['road_traffic']):
            primary_category = "road/traffic infrastructure"
        elif any(k in complaint_lower for k in valid_categories['electricity_power']):
            primary_category = "electricity/power supply"
        elif any(k in complaint_lower for k in valid_categories['water_plumbing']):
            primary_category = "water/plumbing services"
        elif any(k in complaint_lower for k in valid_categories['garbage_waste']):
            primary_category = "garbage/waste management"
        else:
            primary_category = "public infrastructure"

        return True, f"Valid {primary_category} complaint", "Your complaint will be processed and forwarded to the relevant department"

    # If no clear category matches, it's ambiguous
    return False, "Unclear or unrelated complaint", "Please provide details about civic infrastructure issues like roads, electricity, water, or garbage problems"


def validate_complaint_appropriateness(complaint_data: Dict) -> Tuple[bool, str, str]:
    """
    Comprehensive validation to ensure complaint is appropriate for this system.
    Combines AI classification with content analysis.

    Returns: (is_appropriate, reason, suggested_action)
    """
    complaint_description = complaint_data.get('complaint_description', '')

    # First, check if the complaint is about a valid civic issue
    is_valid, reason, action = classify_complaint_validity(complaint_description)

    if not is_valid:
        return False, reason, action

    # Additional checks for appropriateness
    description_lower = complaint_description.lower()

    # Check for spam or test complaints
    spam_indicators = [
        'test', 'testing', 'abc', 'xyz', '123', 'sample', 'demo',
        'lorem ipsum', 'dummy', 'fake', 'placeholder'
    ]

    if any(indicator in description_lower for indicator in spam_indicators):
        return False, "Test or placeholder complaint", "Please submit a real civic infrastructure complaint"

    # Check for very brief complaints and offer category selection instead
    words = complaint_description.split()
    if len(words) < 3:
        # For very brief complaints, suggest category selection instead of rejection
        return False, "Brief complaint detected", "Would you like to select a complaint category instead? Please choose:\n• Road/traffic issues\n• Electricity/power problems\n• Water/plumbing issues\n• Garbage/waste collection"

    # Check for excessive repetition
    if len(set(words)) / len(words) < 0.5 and len(words) > 5:  # Less than 50% unique words, but only for longer texts
        return False, "Excessive word repetition", "Please describe your complaint clearly without repeating words unnecessarily"

    return True, reason, action


class State(TypedDict):
    messages: Annotated[list, add_messages]
    citizen_name: Optional[str]
    location: Optional[str]
    complaint_description: Optional[str]
    issue_type: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    priority: Optional[str]
    session_id: str
    last_asked_field: Optional[str]  # Track what we last asked for


def classify_issue(message: str) -> Optional[str]:
    """Classify complaint into issue category based on keywords"""
    message_lower = message.lower()
    
    # English keywords
    road_keywords = ['road', 'street', 'pothole', 'traffic', 'lane', 'pavement', 'sidewalk', 'asphalt', 'gaddha', 'gaddhe', 'sadak', 'rasta']
    electricity_keywords = ['electricity', 'power', 'light', 'outage', 'blackout', 'electrical', 'wire', 'pole', 'bijli', 'current']
    water_keywords = ['water', 'pipe', 'leak', 'supply', 'drainage', 'sewer', 'tap', 'faucet', 'paani', 'pani', 'nali']
    garbage_keywords = ['garbage', 'trash', 'waste', 'bin', 'collection', 'dump', 'rubbish', 'litter', 'kachra', 'kachre', 'waste']
    
    if any(keyword in message_lower for keyword in road_keywords):
        return "road_issue"
    elif any(keyword in message_lower for keyword in electricity_keywords):
        return "electricity_issue"
    elif any(keyword in message_lower for keyword in water_keywords):
        return "water_issue"
    elif any(keyword in message_lower for keyword in garbage_keywords):
        return "garbage_issue"
    
    return None


def extract_info_from_message(message: str, field: str) -> Optional[str]:
    """Try to extract field information from user message"""
    message_lower = message.lower()
    
    if field == "citizen_name":
        # Look for patterns like "I am", "my name is", "this is"
        patterns = [
            r"(?:i'?m|i am|my name is|this is|name is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:here|speaking)"
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
    
    elif field == "location":
        # Look for location indicators
        patterns = [
            r"(?:at|in|near|on)\s+([A-Z][a-zA-Z\s,]+?)(?:\.|,|$)",
            r"location[:\s]+([A-Z][a-zA-Z\s,]+?)(?:\.|,|$)",
            r"address[:\s]+([A-Z][a-zA-Z\s,]+?)(?:\.|,|$)"
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
    
    return None


def start_node(state: State) -> State:
    """Initial node that receives user message"""
    return state


def router_node(state: State) -> State:
    """Classify issue and route to appropriate node"""
    if not state.get("messages"):
        return state

    last_message_obj = state["messages"][-1]
    if isinstance(last_message_obj, dict):
        last_message = last_message_obj.get("content", "")
        is_user = last_message_obj.get("role") == "user"
    else:
        last_message = getattr(last_message_obj, "content", "")
        # Check if it's a user message (HumanMessage has type="human")
        message_type = getattr(last_message_obj, "type", "")
        is_user = message_type == "human"
    
    # Only process user messages
    if not is_user:
        return state
    
    # Check if issue type is already set
    if not state.get("issue_type"):
        # Check for category selections FIRST (before validation)
        message_lower = last_message.lower().strip()

        # Check for category selections (more flexible matching)
        # These are the exact phrases we offer in category selection
        print(f"DEBUG: Checking category selection for: {message_lower}")
        if "road/traffic issues" in message_lower or "road/traffic" in message_lower:
            print("DEBUG: Setting issue_type to road_issue")
            state["issue_type"] = "road_issue"
        elif "electricity/power problems" in message_lower or "electricity/power" in message_lower:
            print("DEBUG: Setting issue_type to electricity_issue")
            state["issue_type"] = "electricity_issue"
        elif "water/plumbing issues" in message_lower or "water/plumbing" in message_lower:
            print("DEBUG: Setting issue_type to water_issue")
            state["issue_type"] = "water_issue"
        elif "garbage/waste collection" in message_lower or "garbage/waste" in message_lower:
            print("DEBUG: Setting issue_type to garbage_issue")
            state["issue_type"] = "garbage_issue"
            print(f"DEBUG: issue_type after category check: {state.get('issue_type')}")

        # If category was selected, skip validation and proceed
        if state.get("issue_type"):
            print(f"DEBUG: Category selected, skipping validation")
        else:
            # If no category was selected, reject any text input and force category selection
            if "messages" not in state:
                state["messages"] = []

            response_message = "Please select a complaint category first by clicking one of the buttons above. You cannot type your complaint until you choose a category.\n\n"
            response_message += "Available categories:\n"
            response_message += "• Road/Traffic Issues\n"
            response_message += "• Electricity/Power Problems\n"
            response_message += "• Water/Plumbing Issues\n"
            response_message += "• Garbage/Waste Collection"

            state["messages"].append({
                "role": "assistant",
                "content": response_message
            })
            return state

    # If we reach here, category was selected - proceed normally
    
    return state


def check_missing_fields(state: State) -> list:
    """Check which required fields are missing in the order: Issue → Description → Location → Name"""
    missing = []
    # First priority: issue_type (what is the problem - selected via buttons)
    if not state.get("issue_type"):
        missing.append("issue_type")
    # Second priority: complaint_description (brief explanation about the problem)
    if not state.get("complaint_description"):
        missing.append("complaint_description")
    # Third priority: location (where is the issue)
    if not state.get("location"):
        missing.append("location")
    # Fourth priority: citizen_name (who is reporting)
    if not state.get("citizen_name"):
        missing.append("citizen_name")
    # Contact information is now truly optional - no longer required
    return missing


def ask_question(field: str, issue_type: str = None) -> str:
    """Generate contextual question for missing or invalid field based on complaint type"""

    # Get complaint type context
    complaint_context = {
        "road_issue": "road/traffic",
        "electricity_issue": "electricity/power",
        "water_issue": "water/plumbing",
        "garbage_issue": "garbage/waste collection"
    }.get(issue_type, "general")

    questions = {
        "issue_type": "What type of issue are you reporting? Please choose from:\n• Road problems (potholes, traffic issues)\n• Electricity issues (power outages, electrical problems)\n• Water problems (leaks, supply issues)\n• Garbage/waste issues (collection problems)",

        "location": {
            "road_issue": "Where is the road/traffic issue located? Please provide the street address or area (e.g., '123 Main Street' or 'Downtown intersection of Oak and Pine').",
            "electricity_issue": "Where is the electricity/power issue occurring? Please provide the address or location (e.g., '456 Oak Avenue, Apartment 3B' or 'Building 5, Floor 2').",
            "water_issue": "Where is the water/plumbing problem? Please provide the address or location (e.g., '789 Pine Road' or 'Community Center bathroom').",
            "garbage_issue": "Where do you need garbage/waste collection? Please provide the address or area (e.g., '234 Elm Street' or 'Community Park pavilion')."
        }.get(issue_type, "Where is this issue located? Please provide a specific address or area (at least 3 characters)."),

        "citizen_name": "What is your full name? Please provide your complete name (at least 2 characters, e.g., 'John Smith' or 'Maria Gonzalez').",

        "complaint_description": {
            "road_issue": "Please provide a brief explanation of the road/traffic problem (at least 10 characters). For example: 'Large pothole causing vehicle damage' or 'Traffic light malfunctioning at intersection'.",
            "electricity_issue": "Please provide a brief explanation of the electricity/power issue (at least 10 characters). For example: 'Power outage in apartment for 2 hours' or 'Sparking electrical panel in hallway'.",
            "water_issue": "Please provide a brief explanation of the water/plumbing problem (at least 10 characters). For example: 'Leaking pipe under kitchen sink' or 'No water pressure on 2nd floor'.",
            "garbage_issue": "Please provide a brief explanation of the garbage/waste issue (at least 10 characters). For example: 'Garbage not collected for 3 days' or 'Overflowing waste bins in area'."
        }.get(issue_type, "Please provide a brief explanation of the problem (at least 10 characters)."),

        "contact_info": "How can we contact you about this complaint? Please provide a valid email address (like 'john@example.com') or phone number (like '555-0123').",

        "contact_email": "Please provide your email address so we can contact you about this complaint (e.g., 'john.smith@gmail.com' or 'maria.jones@company.com').",

        "contact_phone": "Please provide your phone number for contact (at least 3 digits, e.g., '555-0123', '123-456-7890', or '+1-555-012-3456').",

        "priority": "How urgent is this issue? Please choose: low, medium, high, or urgent."
    }

    # Handle nested questions for location and description
    question = questions.get(field)
    if isinstance(question, dict):
        question = question.get(issue_type, f"Please provide valid information for {field.replace('_', ' ')}.")

    return question or f"Please provide valid information for {field.replace('_', ' ')}."


def process_issue_node(state: State) -> State:
    """Process issue node - collect missing information"""
    print("DEBUG: process_issue_node called")
    if not state.get("messages"):
        return state
    
    last_message_obj = state["messages"][-1]
    if isinstance(last_message_obj, dict):
        last_message = last_message_obj.get("content", "")
        is_user = last_message_obj.get("role") == "user"
    else:
        last_message = getattr(last_message_obj, "content", "")
        # Check if it's a user message (HumanMessage has type="human")
        message_type = getattr(last_message_obj, "type", "")
        is_user = message_type == "human"
    
    # Only process if this is a user message
    if is_user:
        # If we asked for a specific field, try to extract it from the response
        last_asked = state.get("last_asked_field")
        print(f"DEBUG: last_asked_field = {last_asked}, message = {last_message}")
        
        if last_asked == "citizen_name":
            extracted = extract_info_from_message(last_message, "citizen_name")
            if extracted:
                state["citizen_name"] = extracted
            else:
                # Simple name extraction - if short and doesn't contain issue keywords
                words = last_message.split()
                if len(words) <= 3 and not any(keyword in last_message.lower() for keyword in ['issue', 'problem', 'complaint', 'road', 'water', 'electricity', 'garbage', 'location', 'address']):
                    state["citizen_name"] = last_message.strip()

        elif last_asked == "location":
            extracted = extract_info_from_message(last_message, "location")
            if extracted:
                state["location"] = extracted
            else:
                # Accept the message as location if it's substantial
                if len(last_message.strip()) > 3:  # Reduced from 5 to 3 to be more lenient
                    state["location"] = last_message.strip()
        
        elif last_asked == "complaint_description":
            # Accept the message as complaint description
            print(f"DEBUG: Setting complaint_description to: {last_message.strip()} (length: {len(last_message.strip())})")
            if len(last_message.strip()) > 10:
                state["complaint_description"] = last_message.strip()
                print(f"DEBUG: complaint_description set successfully")
            else:
                print(f"DEBUG: complaint_description too short, not set")

        elif last_asked in ["contact_info", "contact_email", "contact_phone"]:
            # Contact info is optional - try to extract if provided, otherwise proceed
            message_lower = last_message.lower().strip()

            # Check if user explicitly says no contact info
            if message_lower in ['no contact info provided', 'no contact', 'none', 'skip', 'optional', 'no email', 'no phone']:
                # User explicitly chose not to provide contact info - proceed without contact fields
                pass
            else:
                # Try to extract email or phone from the message
                import re
                # Email pattern
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                email_match = re.search(email_pattern, last_message)
                if email_match:
                    state["contact_email"] = email_match.group()
                else:
                    # Phone pattern (various formats)
                    phone_pattern = r'\b\d{10}\b|\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|\+\d{1,3}[-.]?\d{10}\b|\b\d{3,15}\b'
                    phone_match = re.search(phone_pattern, last_message)
                    if phone_match:
                        state["contact_phone"] = phone_match.group()
                    else:
                        # If no email/phone found and message looks like contact info, try to infer
                        if "@" in last_message or "email" in last_message.lower():
                            # Looks like they tried to give email but it didn't match pattern
                            if len(last_message.strip()) > 3:
                                state["contact_email"] = last_message.strip()
                        elif any(char.isdigit() for char in last_message):
                            # Contains numbers, might be phone
                            if len(last_message.strip()) >= 3:
                                state["contact_phone"] = last_message.strip()
                        # If nothing matches, just proceed without contact info (it's optional)

        elif last_asked == "priority":
            # Extract priority level
            message_lower = last_message.lower().strip()
            if message_lower in ['low', 'medium', 'high', 'urgent']:
                state["priority"] = message_lower
            elif 'urgent' in message_lower or 'emergency' in message_lower:
                state["priority"] = 'urgent'
            elif 'high' in message_lower or 'important' in message_lower:
                state["priority"] = 'high'
            elif 'low' in message_lower or 'minor' in message_lower:
                state["priority"] = 'low'
            else:
                # Default to medium if unclear
                state["priority"] = 'medium'

        # Also try to extract complaint description from initial message if it's substantial
        # Only do this if we haven't asked for a specific field yet
        if not state.get("complaint_description") and len(last_message) > 30 and not last_asked:
            # Check if it contains complaint-related content
            if any(keyword in last_message.lower() for keyword in ['problem', 'issue', 'broken', 'damaged', 'not working', 'need', 'help']):
                state["complaint_description"] = last_message.strip()
    
    # Check missing fields
    missing = check_missing_fields(state)

    if not missing:
        # All fields collected - validate and save
        complaint_data = {
            "citizen_name": state["citizen_name"],
            "location": state["location"],
            "complaint_description": state["complaint_description"],
            "issue_type": state["issue_type"],
            "contact_email": state.get("contact_email"),
            "contact_phone": state.get("contact_phone"),
            "priority": state.get("priority", "medium"),
            "session_id": state.get("session_id", "default")
        }

        # Validate the complaint data before saving
        from database import validate_complaint_data
        is_valid, validation_results = validate_complaint_data(complaint_data)

        if not is_valid:
            # Validation failed - show specific, helpful errors to user and continue conversation
            if "messages" not in state:
                state["messages"] = []

            # Get complaint type for contextual guidance
            issue_type = complaint_data.get("issue_type", "")
            complaint_type_name = {
                "road_issue": "road/traffic",
                "electricity_issue": "electricity/power",
                "water_issue": "water/plumbing",
                "garbage_issue": "garbage/waste collection"
            }.get(issue_type, "general")

            error_messages = []
            first_invalid_field = None

            for field, result in validation_results.items():
                if not result['valid']:
                    if not first_invalid_field:
                        first_invalid_field = field

                    # Create more specific, helpful error messages
                    if field == "citizen_name":
                        error_messages.append("• Name: Please provide your full name (at least 2 characters, e.g., 'John Smith')")
                    elif field == "location":
                        if issue_type == "road_issue":
                            error_messages.append("• Location: Please provide the street address or area (at least 3 characters, e.g., '123 Main Street' or 'Downtown Area')")
                        elif issue_type == "electricity_issue":
                            error_messages.append("• Location: Please provide where the power issue is occurring (at least 3 characters, e.g., '456 Oak Avenue, Apartment 3B')")
                        elif issue_type == "water_issue":
                            error_messages.append("• Location: Please provide where the water problem is (at least 3 characters, e.g., '789 Pine Road' or 'Building 5, Floor 2')")
                        elif issue_type == "garbage_issue":
                            error_messages.append("• Location: Please provide where garbage collection is needed (at least 3 characters, e.g., '234 Elm Street' or 'Community Park')")
                        else:
                            error_messages.append("• Location: Please provide the address or area (at least 3 characters)")
                    elif field == "complaint_description":
                        if issue_type == "road_issue":
                            error_messages.append("• Description: Please describe the road/traffic issue in detail (at least 10 characters, e.g., 'There is a large pothole causing damage to vehicles')")
                        elif issue_type == "electricity_issue":
                            error_messages.append("• Description: Please describe the electricity/power problem (at least 10 characters, e.g., 'Power has been out for 2 hours, affecting multiple apartments')")
                        elif issue_type == "water_issue":
                            error_messages.append("• Description: Please describe the water/plumbing issue (at least 10 characters, e.g., 'Water is leaking from the pipe under the sink')")
                        elif issue_type == "garbage_issue":
                            error_messages.append("• Description: Please describe the garbage/waste issue (at least 10 characters, e.g., 'Garbage has not been collected for 3 days and bins are overflowing')")
                        else:
                            error_messages.append("• Description: Please provide more details about your complaint (at least 10 characters)")
                    elif field == "contact_email":
                        error_messages.append("• Email: Please provide a valid email address for contact (e.g., 'john@example.com' or 'mary.smith@gmail.com')")
                    elif field == "contact_phone":
                        error_messages.append("• Phone: Please provide a valid phone number (at least 3 digits, e.g., '555-0123' or '+1-555-012-3456')")

            # Create contextual error message
            error_text = f"I found some issues with your {complaint_type_name} complaint information that need to be corrected:\n\n"
            error_text += "\n".join(error_messages)
            error_text += f"\n\nPlease provide the corrected information for the items above, and I'll submit your {complaint_type_name} complaint right away. Let's fix these together:"

            state["messages"].append({
                "role": "assistant",
                "content": error_text
            })

            # Set last_asked_field to the first invalid field for targeted questioning
            if first_invalid_field:
                state["last_asked_field"] = first_invalid_field

            return state

        # Validation passed - save and send webhook
        # Save to database
        save_complaint(complaint_data)

        # Send webhook
        webhook_payload = {
            "citizen_name": state["citizen_name"],
            "location": state["location"],
            "complaint": state["complaint_description"],
            "issue_type": state["issue_type"].replace("_issue", "")
        }
        send_webhook(webhook_payload)

        if "messages" not in state:
            state["messages"] = []
        state["messages"].append({
            "role": "assistant",
            "content": "Thank you! Your complaint has been recorded and submitted. We will look into this issue and get back to you soon."
        })
        state["last_asked_field"] = None
        return state

    # Ask for the first missing field
    field_to_ask = missing[0]
    issue_type = state.get("issue_type")
    question = ask_question(field_to_ask, issue_type)
    
    if "messages" not in state:
        state["messages"] = []
    state["messages"].append({
        "role": "assistant",
        "content": question
    })
    state["last_asked_field"] = field_to_ask
    
    return state


def road_issue_node(state: State) -> State:
    """Handle road issue complaints"""
    return process_issue_node(state)


def electricity_issue_node(state: State) -> State:
    """Handle electricity issue complaints"""
    return process_issue_node(state)


def water_issue_node(state: State) -> State:
    """Handle water issue complaints"""
    return process_issue_node(state)


def garbage_issue_node(state: State) -> State:
    """Handle garbage issue complaints"""
    return process_issue_node(state)


# Build the graph
def create_graph():
    workflow = StateGraph(State)
    
    workflow.add_node("start", start_node)
    workflow.add_node("router", router_node)
    workflow.add_node("road_issue", road_issue_node)
    workflow.add_node("electricity_issue", electricity_issue_node)
    workflow.add_node("water_issue", water_issue_node)
    workflow.add_node("garbage_issue", garbage_issue_node)
    
    workflow.set_entry_point("start")
    workflow.add_edge("start", "router")
    
    def route_after_classification(state: State):
        issue_type = state.get("issue_type")
        print(f"DEBUG: route_after_classification - issue_type = {issue_type}")
        if not issue_type:
            # If we just asked for clarification, end and wait for next user message
            # (which will go through the graph again)
            print("DEBUG: No issue_type, returning END")
            return END

        if issue_type == "road_issue":
            print("DEBUG: Routing to road_issue")
            return "road_issue"
        elif issue_type == "electricity_issue":
            print("DEBUG: Routing to electricity_issue")
            return "electricity_issue"
        elif issue_type == "water_issue":
            print("DEBUG: Routing to water_issue")
            return "water_issue"
        elif issue_type == "garbage_issue":
            print("DEBUG: Routing to garbage_issue")
            return "garbage_issue"
        print(f"DEBUG: Unknown issue_type {issue_type}, returning END")
        return END
    
    workflow.add_conditional_edges("router", route_after_classification)
    workflow.add_edge("road_issue", END)
    workflow.add_edge("electricity_issue", END)
    workflow.add_edge("water_issue", END)
    workflow.add_edge("garbage_issue", END)
    
    return workflow.compile()


# Global graph instance
graph = create_graph()


async def process_message(user_message: str, session_id: str = "default") -> str:
    """Process user message through LangGraph workflow"""
    try:
        # Get or create session state
        state = get_session_state(session_id)
        
        # Add user message
        if "messages" not in state:
            state["messages"] = []
        
        state["messages"].append({
            "role": "user",
            "content": user_message
        })
        
        # Run graph
        result = graph.invoke(state)
        
        # Save session state
        from database import save_session_state
        save_session_state(session_id, result)
        
        # Get last assistant message
        if result.get("messages"):
            last_assistant_msg = None
            for msg in reversed(result["messages"]):
                if isinstance(msg, dict) and msg.get("role") == "assistant":
                    last_assistant_msg = msg.get("content")
                    break
                elif hasattr(msg, "content") and hasattr(msg, "role") and msg.role == "assistant":
                    last_assistant_msg = msg.content
                    break
                elif hasattr(msg, "content") and hasattr(msg, "type") and msg.type == "ai":
                    # LangGraph uses AIMessage with type="ai" for assistant messages
                    last_assistant_msg = msg.content
                    break
            
            if last_assistant_msg:
                return last_assistant_msg
        
        return "I'm here to help you file a complaint. Please describe your issue."
    except Exception as e:
        import traceback
        print(f"Error in process_message: {e}")
        print(traceback.format_exc())
        return f"I encountered an error processing your message. Please try again. Error: {str(e)}"


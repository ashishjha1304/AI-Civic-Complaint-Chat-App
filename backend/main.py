from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Stateless message processor - let frontend control conversation flow
async def process_message(message: str, session_id: str = "default") -> str:
    """
    Simple stateless processor that acknowledges input.
    Conversation flow is managed entirely by the frontend.
    Backend responses are generic and don't determine conversation flow.
    """
    # Generic acknowledgment for all inputs
    # Frontend manages the actual conversation logic
    return "Information received. Processing your request..."

load_dotenv()

app = FastAPI()

# CORS middleware - Local development configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Additional CORS headers for all responses
@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    response.headers["Access-Control-Allow-Credentials"] = "false"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        reply = await process_message(request.message, request.session_id)
        return ChatResponse(reply=reply)
    except Exception as e:
        import traceback
        print(f"Error in chat endpoint: {e}")
        print(traceback.format_exc())
        return ChatResponse(reply="Sorry, I encountered an error. Please try again or start a new complaint.")

# CORS test endpoint - bypasses CORS middleware
@app.options("/chat")
async def chat_options():
    return {"message": "CORS preflight handled"}

@app.post("/chat-test")
async def chat_test_endpoint(request: ChatRequest):
    """Test endpoint that explicitly sets CORS headers"""
    try:
        reply = await process_message(request.message, request.session_id)
        response = ChatResponse(reply=reply)
        # Manually add CORS headers
        response.__dict__.update({
            "access_control_allow_origin": "*",
            "access_control_allow_credentials": "false",
            "access_control_allow_methods": "GET, POST, PUT, DELETE, OPTIONS",
            "access_control_allow_headers": "*"
        })
        return response
    except Exception as e:
        import traceback
        print(f"Error in test endpoint: {e}")
        print(traceback.format_exc())
        return ChatResponse(reply="Test endpoint error")


@app.post("/submit-complaint")
async def submit_complaint_endpoint(complaint_data: dict):
    """Submit a complete complaint to the database"""
    try:
        from database import save_complaint, validate_complaint_data

        print(f"[SUBMIT] Received complaint submission: {complaint_data}")

        # Validate the complaint data
        is_valid, validation_results = validate_complaint_data(complaint_data)

        if not is_valid:
            print("[VALIDATION FAILED] Complaint data validation failed")
            return {"success": False, "error": "Validation failed", "details": validation_results}

        # Save to database
        result = save_complaint(complaint_data)

        if result:
            print("[SUCCESS] Complaint submitted successfully")
            return {"success": True, "message": "Complaint submitted successfully"}
        else:
            print("[ERROR] Failed to save complaint to database")
            return {"success": False, "error": "Database save failed"}

    except Exception as e:
        print(f"[ERROR] Exception in submit_complaint_endpoint: {e}")
        return {"success": False, "error": str(e)}


@app.post("/reset")
async def reset_session():
    """Reset the session for a new complaint"""
    # Simple session reset - no database for now
    return {"status": "success", "message": "Session reset successfully"}


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Civic Complaint Assistant API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "GET /": "API information",
            "GET /health": "Health check",
            "POST /chat": "Chat with AI assistant",
            "POST /reset": "Reset conversation session"
        },
        "docs": "/docs"  # FastAPI automatic docs
    }

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


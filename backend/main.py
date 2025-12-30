from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Simple fallback for process_message without langgraph
async def process_message(message: str, session_id: str = "default") -> str:
    """Simple message processor fallback"""
    if "pothole" in message.lower():
        return "I understand you have a pothole issue. Can you please provide the location of this pothole?"
    elif "location" in message.lower() or "address" in message.lower():
        return "Thank you for providing the location. What's your name so I can register this complaint?"
    elif any(word in message.lower() for word in ["john", "jane", "name"]):
        return "Thank you! Your complaint has been registered. We'll look into this issue."
    else:
        return "I understand you want to file a complaint. Can you please describe the issue you're facing?"

load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5177",
        "http://127.0.0.1:5177",
        "https://frontend-g4pbykyuo-ashish-jhas-projects-ff68ec28.vercel.app"  # Vercel frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    return {"status": "ok"}


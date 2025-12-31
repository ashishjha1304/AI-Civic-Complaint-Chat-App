"""
Simple script to run the FastAPI server
"""
import uvicorn
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    # Change to the backend directory to ensure .env file is found
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)

    # Load environment variables
    load_dotenv()

    print(f"[STARTUP] Working directory: {os.getcwd()}")
    print(f"[STARTUP] .env file exists: {os.path.exists('.env')}")

    # Check if environment variables are loaded
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    webhook_url = os.getenv('WEBHOOK_URL')

    print(f"[STARTUP] SUPABASE_URL loaded: {'Yes' if supabase_url else 'No'}")
    print(f"[STARTUP] SUPABASE_KEY loaded: {'Yes' if supabase_key else 'No'}")
    print(f"[STARTUP] WEBHOOK_URL loaded: {'Yes' if webhook_url else 'No'}")

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)






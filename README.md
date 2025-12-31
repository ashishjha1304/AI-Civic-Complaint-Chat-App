# Smart City Complaint Assistant

An AI-powered complaint management system that helps citizens file complaints by understanding natural language, classifying issues, and collecting required information step-by-step.

## Features

- Natural language complaint processing
- Automatic issue classification (road, electricity, water, garbage)
- Step-by-step data collection
- Supabase database integration
- Webhook notifications
- Clean chat-based UI

## Tech Stack

- **Frontend**: React + Vite
- **Backend**: Python + FastAPI
- **Database**: Supabase (PostgreSQL)

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Supabase account (free tier works)

### Backend Setup

1. Navigate to the backend directory and install dependencies:
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
```

2. (Optional) Configure Supabase for data persistence:
   - Create a Supabase project at https://supabase.com
   - Create a `.env` file with your credentials:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

3. Start the backend server:
```bash
python run.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory and install dependencies:
```bash
cd frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:5173`

### Testing the Application

1. Open `http://localhost:5173` in your browser
2. Select a complaint category (e.g., "Road & Traffic Issues")
3. Describe your complaint: "There's a pothole on Main Street"
4. The system will guide you through providing location and contact information
5. Once all information is collected, your complaint will be submitted

The system works without Supabase configuration - complaints are processed and stored in memory for demo purposes.

## API Endpoints

### POST /chat
Send a message to the complaint assistant.

**Request:**
```json
{
  "message": "There's a pothole on Main Street"
}
```

**Response:**
```json
{
  "reply": "Could you please provide the location or address of this issue?"
}
```

### GET /health
Health check endpoint.

## Issue Categories

- **road_issue**: Road, street, pothole, traffic, lane, pavement, sidewalk, asphalt
- **electricity_issue**: Electricity, power, light, outage, blackout, electrical, wire, pole
- **water_issue**: Water, pipe, leak, supply, drainage, sewer, tap, faucet
- **garbage_issue**: Garbage, trash, waste, bin, collection, dump, rubbish, litter

## Data Collection

The system collects the following information for each complaint:
- Citizen Name
- Location
- Complaint Description
- Issue Type

The system asks for missing information one field at a time and only submits the complaint when all fields are collected.

## Webhook Integration

When all required fields are collected, the system sends a POST request to the configured webhook URL with the following payload:

```json
{
  "citizen_name": "John Doe",
  "location": "123 Main Street",
  "complaint": "There's a large pothole causing traffic issues",
  "issue_type": "road"
}
```

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application with chat endpoints
│   ├── database.py          # Supabase integration (optional)
│   ├── run.py               # Server startup script
│   ├── requirements.txt     # Python dependencies
│   └── env.example          # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── main.jsx         # React entry point
│   │   └── index.css        # Global styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── test_frontend.html       # Standalone test interface
└── README.md
```

## Notes

- The system works out-of-the-box without any external dependencies for demonstration purposes
- Supabase integration is optional - add credentials to `backend/.env` for persistent storage
- The application is configured to run only on localhost for local development
- All cloud deployment configurations have been removed for clean local development






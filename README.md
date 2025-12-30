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
- **Backend**: Python + FastAPI + LangGraph
- **Database**: Supabase (PostgreSQL)

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the backend directory:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
WEBHOOK_URL=your_webhook_url
```

6. Set up Supabase:
   - Create a new Supabase project
   - Create a table named `complaints` with the following columns:
     - `id` (uuid, primary key, default: gen_random_uuid())
     - `citizen_name` (text)
     - `location` (text)
     - `complaint_description` (text)
     - `issue_type` (text)
     - `created_at` (timestamp, default: now())

7. Run the backend server:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

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
│   ├── main.py              # FastAPI application
│   ├── langgraph_flow.py    # LangGraph workflow
│   ├── database.py          # Supabase integration
│   ├── webhook.py           # Webhook sender
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── App.css          # Styles
│   │   ├── main.jsx         # React entry point
│   │   └── index.css        # Global styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Notes

- The system uses in-memory session storage for demo purposes. For production, consider using Redis or database-backed sessions.
- Make sure to configure your Supabase credentials and webhook URL in the `.env` file.
- The system will continue to work even if the webhook fails, ensuring complaints are still saved to the database.





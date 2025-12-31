# Quick Start Guide

## Prerequisites
- Python 3.8+
- Node.js 16+
- Supabase account (free tier works)

## Step 1: Backend Setup

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

## Step 2: Configure Environment

Create `backend/.env` file:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
WEBHOOK_URL=https://your-webhook-url.com/webhook
```

## Step 3: Set Up Supabase Database

1. Go to your Supabase project
2. Open SQL Editor
3. Run the SQL from `backend/supabase_schema.sql`

Or create the table manually:
- Table name: `complaints`
- Columns:
  - `id` (uuid, primary key)
  - `citizen_name` (text)
  - `location` (text)
  - `complaint_description` (text)
  - `issue_type` (text)
  - `created_at` (timestamp)

## Step 4: Start Backend

```bash
cd backend
python run.py
# or
uvicorn main:app --reload --port 8000
```

Backend will run on http://localhost:8000

## Step 5: Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on http://localhost:5173

## Testing

1. Open http://localhost:5173 in your browser
2. Try a complaint like: "There's a pothole on Main Street"
3. The system will ask for missing information step by step
4. Once all fields are collected, the complaint is saved and webhook is triggered

## Example Conversation Flow

**User**: "There's a pothole on Main Street"  
**Bot**: "May I have your name, please?"

**User**: "John Doe"  
**Bot**: "Could you please describe the complaint in detail?"

**User**: "There's a large pothole causing traffic issues"  
**Bot**: "Thank you! Your complaint has been recorded and submitted."

## Troubleshooting

- **Backend won't start**: Check that all dependencies are installed and .env file exists
- **Database errors**: Verify Supabase credentials and table exists
- **CORS errors**: Make sure backend allows frontend origin (already configured)
- **Webhook not working**: Check WEBHOOK_URL in .env (system continues even if webhook fails)







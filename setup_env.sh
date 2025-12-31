#!/bin/bash

# Setup Environment Variables for Vercel Deployment
# Run this script to configure environment variables for your deployed backend

echo "Setting up environment variables for AI Civic Complaint Backend..."
echo ""

# Change to backend directory
cd backend

echo "Adding SUPABASE_URL..."
echo "Please enter your Supabase project URL (e.g., https://your-project.supabase.co):"
read -r supabase_url
vercel env add SUPABASE_URL production <<< "$supabase_url"

echo ""
echo "Adding SUPABASE_KEY..."
echo "Please enter your Supabase anon key:"
read -r supabase_key
vercel env add SUPABASE_KEY production <<< "$supabase_key"

echo ""
echo "Adding WEBHOOK_URL (optional)..."
echo "Please enter your webhook URL (or press Enter to skip):"
read -r webhook_url
if [ -n "$webhook_url" ]; then
    vercel env add WEBHOOK_URL production <<< "$webhook_url"
fi

echo ""
echo "Redeploying backend with new environment variables..."
vercel --prod --yes

echo ""
echo "✅ Environment variables configured successfully!"
echo "Your backend is now fully functional with database connectivity."

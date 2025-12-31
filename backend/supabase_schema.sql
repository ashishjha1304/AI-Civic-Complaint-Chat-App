-- Clean and simple complaints table schema
-- Run this SQL in your Supabase SQL editor to create/replace the table

-- Drop existing table if it exists (be careful in production!)
DROP TABLE IF EXISTS complaints;

-- Create the clean complaints table
CREATE TABLE complaints (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    citizen_name TEXT NOT NULL,
    email TEXT NOT NULL,
    mobile_number TEXT NOT NULL,
    issue_type TEXT NOT NULL,
    complaint_description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create basic index for faster queries
CREATE INDEX idx_complaints_created_at ON complaints(created_at);


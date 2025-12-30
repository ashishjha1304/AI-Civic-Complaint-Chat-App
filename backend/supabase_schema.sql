-- Complete complaints table schema for fresh Supabase table
-- Use this when creating a NEW table from scratch
-- Run this SQL in your Supabase SQL editor

CREATE TABLE complaints (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    citizen_name TEXT NOT NULL CHECK (LENGTH(TRIM(citizen_name)) >= 2),
    location TEXT NOT NULL CHECK (LENGTH(TRIM(location)) >= 3),
    complaint_description TEXT NOT NULL CHECK (LENGTH(TRIM(complaint_description)) >= 10),
    issue_type TEXT NOT NULL CHECK (issue_type IN ('road_issue', 'electricity_issue', 'water_issue', 'garbage_issue')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_review', 'assigned', 'resolved', 'rejected', 'cancelled', 'duplicate')),
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    contact_email TEXT CHECK (contact_email IS NULL OR contact_email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    contact_phone TEXT CHECK (contact_phone IS NULL OR contact_phone ~ '^(\+\d{1,3})?\d{3,15}$'),
    assigned_department TEXT CHECK (assigned_department IS NULL OR assigned_department IN ('roads', 'electricity', 'water', 'sanitation', 'general')),
    assigned_to TEXT,
    resolution_notes TEXT,
    session_id TEXT,
    source TEXT DEFAULT 'chat' CHECK (source IN ('chat', 'web', 'mobile', 'api')),
    resolved_at TIMESTAMP WITH TIME ZONE,
    estimated_resolution_time INTERVAL,
    feedback_rating INTEGER CHECK (feedback_rating IS NULL OR feedback_rating BETWEEN 1 AND 5),
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX idx_complaints_issue_type ON complaints(issue_type);
CREATE INDEX idx_complaints_status ON complaints(status);
CREATE INDEX idx_complaints_priority ON complaints(priority);
CREATE INDEX idx_complaints_assigned_department ON complaints(assigned_department);
CREATE INDEX idx_complaints_assigned_to ON complaints(assigned_to);
CREATE INDEX idx_complaints_source ON complaints(source);
CREATE INDEX idx_complaints_resolved_at ON complaints(resolved_at);
CREATE INDEX idx_complaints_feedback_rating ON complaints(feedback_rating);
CREATE INDEX idx_complaints_created_at ON complaints(created_at);
CREATE INDEX idx_complaints_updated_at ON complaints(updated_at);
CREATE INDEX idx_complaints_session_id ON complaints(session_id);
CREATE INDEX idx_complaints_tags ON complaints USING GIN(tags);

-- Create triggers for automatic timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_complaints_updated_at
    BEFORE UPDATE ON complaints
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-set resolved_at when status changes to 'resolved'
CREATE OR REPLACE FUNCTION set_resolved_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'resolved' AND OLD.status != 'resolved' THEN
        NEW.resolved_at = NOW();
    ELSIF NEW.status != 'resolved' THEN
        NEW.resolved_at = NULL;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER set_resolved_at_trigger
    BEFORE UPDATE ON complaints
    FOR EACH ROW
    EXECUTE FUNCTION set_resolved_at();

-- Analytics views
CREATE VIEW complaint_stats AS
SELECT
    issue_type,
    status,
    priority,
    COUNT(*) as complaint_count,
    AVG(EXTRACT(EPOCH FROM (resolved_at - created_at))/86400) as avg_resolution_days
FROM complaints
WHERE status = 'resolved'
GROUP BY issue_type, status, priority;

CREATE VIEW department_workload AS
SELECT
    assigned_department,
    COUNT(*) as total_complaints,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_complaints,
    COUNT(CASE WHEN status = 'in_review' THEN 1 END) as in_review_complaints,
    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_complaints,
    AVG(feedback_rating) as avg_satisfaction
FROM complaints
WHERE assigned_department IS NOT NULL
GROUP BY assigned_department;


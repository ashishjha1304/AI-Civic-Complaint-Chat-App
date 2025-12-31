DROP TABLE IF EXISTS complaints;

CREATE TABLE complaints (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    citizen_name TEXT NOT NULL,
    email TEXT NOT NULL,
    mobile_number TEXT NOT NULL,
    issue_type TEXT NOT NULL,
    complaint_description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


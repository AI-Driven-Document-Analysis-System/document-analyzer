-- Migration to add Google OAuth support to users table
-- Run this script to add the necessary columns for Google authentication

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS google_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS is_oauth_user BOOLEAN DEFAULT FALSE;

-- Make password_hash optional for OAuth users
ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;

-- Create index on google_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);

-- Update existing users to have is_oauth_user = false
UPDATE users SET is_oauth_user = FALSE WHERE is_oauth_user IS NULL;

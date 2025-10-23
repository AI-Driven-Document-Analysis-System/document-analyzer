-- Migration: Add is_pinned column to conversations table
-- Created: 2025-10-20
-- Description: Adds a boolean column to track pinned conversations for dashboard display

-- Add is_pinned column with default value FALSE
ALTER TABLE conversations 
ADD COLUMN IF NOT EXISTS is_pinned BOOLEAN DEFAULT FALSE;

-- Create index for faster queries on pinned conversations
CREATE INDEX IF NOT EXISTS idx_conversations_is_pinned ON conversations(is_pinned);

-- Create index for user_id + is_pinned for efficient dashboard queries
CREATE INDEX IF NOT EXISTS idx_conversations_user_pinned ON conversations(user_id, is_pinned) WHERE is_pinned = TRUE;

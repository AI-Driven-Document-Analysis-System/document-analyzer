-- Database trigger to automatically cleanup empty conversations
-- This runs at the database level with zero application performance impact

-- Function to delete conversations that have no messages after 1 minutes
-- Excludes the newly created conversation to prevent immediate deletion
CREATE OR REPLACE FUNCTION cleanup_empty_conversations(exclude_conversation_id UUID DEFAULT NULL)
RETURNS void AS $$
BEGIN
    DELETE FROM conversations
    WHERE id NOT IN (
        SELECT DISTINCT conversation_id
        FROM chat_messages
        WHERE conversation_id IS NOT NULL
    )
    AND created_at < NOW() - INTERVAL '1 minute'
    AND (exclude_conversation_id IS NULL OR id != exclude_conversation_id);
END;
$$ LANGUAGE plpgsql;

-- Create a scheduled job that runs every hour to cleanup empty conversations
-- This uses pg_cron extension (install with: CREATE EXTENSION pg_cron;)
-- SELECT cron.schedule('cleanup-empty-conversations', '0 * * * *', 'SELECT cleanup_empty_conversations();');

-- Alternative: Manual trigger approach
-- This trigger runs whenever a conversation is updated and cleans up old empty ones
CREATE OR REPLACE FUNCTION trigger_cleanup_empty_conversations()
RETURNS TRIGGER AS $$
BEGIN
    -- Only run cleanup occasionally to avoid performance impact
    -- Options: 0.1 (10%), 0.2 (20%), 0.5 (50%), or remove IF statement for 100%
    IF random() < 0.3 THEN  -- 30% chance on each new conversation
        -- Pass the newly created conversation ID to exclude it from cleanup
        PERFORM cleanup_empty_conversations(NEW.id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger on conversations table INSERT (runs when new conversation is created)
-- This is more efficient - only runs once per new conversation, not on every message
DROP TRIGGER IF EXISTS cleanup_trigger ON conversations;
CREATE TRIGGER cleanup_trigger
    AFTER INSERT ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION trigger_cleanup_empty_conversations();

-- One-time cleanup of existing empty conversations
-- Run this once to clean up existing data
-- SELECT cleanup_empty_conversations();

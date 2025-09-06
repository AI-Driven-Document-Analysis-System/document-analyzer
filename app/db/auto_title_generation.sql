-- PostgreSQL trigger to automatically generate conversation titles
-- This runs at the database level when messages are added
-- Uses NOTIFY to signal the application to generate titles via Groq API

-- Function to generate title using NOTIFY pattern (no http extension needed)
CREATE OR REPLACE FUNCTION generate_title_with_notify(conversation_id UUID, first_message TEXT)
RETURNS VOID AS $$
BEGIN
    -- Send notification to application with conversation details
    PERFORM pg_notify('title_generation_request', 
        json_build_object(
            'conversation_id', conversation_id,
            'message', first_message,
            'timestamp', extract(epoch from now())
        )::text
    );
    
    -- Log the notification
    RAISE NOTICE 'Title generation requested for conversation %', conversation_id;
END;
$$ LANGUAGE plpgsql;

-- Fallback function for immediate simple titles
CREATE OR REPLACE FUNCTION generate_fallback_title(first_message TEXT)
RETURNS TEXT AS $$
DECLARE
    title TEXT;
    words TEXT[];
    meaningful_words TEXT[];
    word TEXT;
BEGIN
    -- Handle empty input
    IF first_message IS NULL OR LENGTH(TRIM(first_message)) = 0 THEN
        RETURN 'New Chat';
    END IF;
    
    -- Clean the message
    first_message := TRIM(first_message);
    
    -- Extract words (alphanumeric only)
    words := regexp_split_to_array(first_message, '\s+');
    
    -- Filter out common question words and short words
    meaningful_words := ARRAY[]::TEXT[];
    FOREACH word IN ARRAY words
    LOOP
        word := LOWER(TRIM(word));
        -- Skip common question starters and short words
        IF word NOT IN ('what', 'how', 'why', 'when', 'where', 'who', 'which', 'can', 'could', 'would', 'should', 'is', 'are', 'do', 'does', 'did', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'please', 'help', 'me', 'i', 'you', 'my', 'your') 
           AND LENGTH(word) > 2 
           AND word ~ '^[a-zA-Z0-9]+$' THEN
            meaningful_words := array_append(meaningful_words, INITCAP(word));
        END IF;
        
        -- Stop at 6 words max
        IF array_length(meaningful_words, 1) >= 6 THEN
            EXIT;
        END IF;
    END LOOP;
    
    -- Build title
    IF array_length(meaningful_words, 1) > 0 THEN
        title := array_to_string(meaningful_words, ' ');
        
        -- Add context-specific suffixes
        IF first_message ~* '(analyze|analysis|report|document)' THEN
            title := title || ' Analysis';
        ELSIF first_message ~* '(how to|how do|how can)' THEN
            title := 'How To ' || title;
        ELSIF first_message ~* '(what is|explain|tell me about)' THEN
            title := title || ' Explanation';
        ELSIF first_message ~* '(compare|difference|vs|versus)' THEN
            title := title || ' Comparison';
        ELSIF first_message ~* '(create|generate|make|build)' THEN
            title := title || ' Creation';
        END IF;
        
        -- Ensure reasonable length
        IF LENGTH(title) > 50 THEN
            title := LEFT(title, 47) || '...';
        END IF;
        
        RETURN title;
    ELSE
        RETURN 'New Chat';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to automatically generate title for conversations
CREATE OR REPLACE FUNCTION auto_generate_conversation_title()
RETURNS TRIGGER AS $$
DECLARE
    conv_id UUID;
    user_msg_count INTEGER;
    assistant_msg_count INTEGER;
    first_user_message TEXT;
    generated_title TEXT;
BEGIN
    -- Get conversation ID from the inserted message
    conv_id := NEW.conversation_id;
    
    -- Skip if conversation_id is null
    IF conv_id IS NULL THEN
        RETURN NEW;
    END IF;
    
    -- Count messages in this conversation
    SELECT 
        COUNT(*) FILTER (WHERE role = 'user'),
        COUNT(*) FILTER (WHERE role = 'assistant')
    INTO user_msg_count, assistant_msg_count
    FROM chat_messages 
    WHERE conversation_id = conv_id;
    
    -- Only generate title when we have exactly 1 user message and 1 assistant message
    -- (meaning this is the first complete conversation pair)
    IF user_msg_count = 1 AND assistant_msg_count = 1 THEN
        -- Check if conversation already has a title
        IF EXISTS (
            SELECT 1 FROM conversations 
            WHERE id = conv_id 
            AND (title IS NOT NULL AND title != '' AND title != 'New Chat')
        ) THEN
            -- Already has a meaningful title, skip
            RETURN NEW;
        END IF;
        
        -- Get the first user message
        SELECT content INTO first_user_message
        FROM chat_messages 
        WHERE conversation_id = conv_id 
        AND role = 'user' 
        ORDER BY timestamp ASC 
        LIMIT 1;
        
        -- Generate title using NOTIFY pattern (triggers application-level Groq API call)
        IF first_user_message IS NOT NULL THEN
            -- Send notification for async title generation
            PERFORM generate_title_with_notify(conv_id, first_user_message);
            
            -- Use fallback title immediately for UI responsiveness
            generated_title := generate_fallback_title(first_user_message);
            
            -- Update conversation title
            UPDATE conversations 
            SET title = generated_title, updated_at = NOW()
            WHERE id = conv_id;
            
            -- Log the action (optional, for debugging)
            RAISE NOTICE 'Auto-generated title for conversation %: %', conv_id, generated_title;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger on chat_messages table
-- This fires after every message insert
DROP TRIGGER IF EXISTS auto_title_generation_trigger ON chat_messages;
CREATE TRIGGER auto_title_generation_trigger
    AFTER INSERT ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION auto_generate_conversation_title();

-- One-time cleanup: Generate titles for existing conversations that don't have them
-- Run this once to backfill existing conversations
DO $$
DECLARE
    conv_record RECORD;
    first_user_msg TEXT;
    generated_title TEXT;
BEGIN
    -- Find conversations without titles that have at least 1 message pair
    FOR conv_record IN 
        SELECT c.id, c.title
        FROM conversations c
        WHERE (c.title IS NULL OR c.title = '' OR c.title = 'New Chat')
        AND EXISTS (
            SELECT 1 FROM chat_messages m1 
            WHERE m1.conversation_id = c.id AND m1.role = 'user'
        )
        AND EXISTS (
            SELECT 1 FROM chat_messages m2 
            WHERE m2.conversation_id = c.id AND m2.role = 'assistant'
        )
    LOOP
        -- Get first user message
        SELECT content INTO first_user_msg
        FROM chat_messages 
        WHERE conversation_id = conv_record.id 
        AND role = 'user' 
        ORDER BY timestamp ASC 
        LIMIT 1;
        
        -- Generate and update title using NOTIFY pattern
        IF first_user_msg IS NOT NULL THEN
            -- Send notification for async title generation
            PERFORM generate_title_with_notify(conv_record.id, first_user_msg);
            
            -- Use fallback title immediately
            generated_title := generate_fallback_title(first_user_msg);
            
            UPDATE conversations 
            SET title = generated_title, updated_at = NOW()
            WHERE id = conv_record.id;
            
            RAISE NOTICE 'Backfilled title for conversation %: %', conv_record.id, generated_title;
        END IF;
    END LOOP;
END $$;

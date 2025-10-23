-- Create table for storing conversation document selections
-- This allows persisting which documents are selected for each conversation

CREATE TABLE IF NOT EXISTS conversation_document_selections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    document_id UUID NOT NULL,
    selected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_conversation_document_selections_conversation_id 
        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    CONSTRAINT fk_conversation_document_selections_document_id 
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    
    -- Unique constraint to prevent duplicate selections
    CONSTRAINT unique_conversation_document_selection 
        UNIQUE (conversation_id, document_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_conversation_document_selections_conversation_id 
    ON conversation_document_selections(conversation_id);

CREATE INDEX IF NOT EXISTS idx_conversation_document_selections_document_id 
    ON conversation_document_selections(document_id);

CREATE INDEX IF NOT EXISTS idx_conversation_document_selections_selected_at 
    ON conversation_document_selections(selected_at);

-- Add comments for documentation
COMMENT ON TABLE conversation_document_selections IS 'Stores which documents are selected for each conversation in Knowledge Base mode';
COMMENT ON COLUMN conversation_document_selections.conversation_id IS 'Reference to the conversation';
COMMENT ON COLUMN conversation_document_selections.document_id IS 'Reference to the selected document';
COMMENT ON COLUMN conversation_document_selections.selected_at IS 'When the document was selected for this conversation';
COMMENT ON COLUMN conversation_document_selections.created_at IS 'When this record was created';

-- Delete specific test documents from the documents table
-- Document IDs: 0a0019bc-2448-4a71-87ec-76ce0a3c9b97 and d5f85423-d7d5-4e73-a5e1-8dfd2a198acd

BEGIN;

-- First, check what columns exist in the documents table
\d documents;

-- Check if the documents exist (using likely column names)
SELECT id, title, created_at
FROM documents
WHERE id IN ('0a0019bc-2448-4a71-87ec-76ce0a3c9b97', 'd5f85423-d7d5-4e73-a5e1-8dfd2a198acd');

-- Delete the documents
DELETE FROM documents
WHERE id IN ('0a0019bc-2448-4a71-87ec-76ce0a3c9b97', 'd5f85423-d7d5-4e73-a5e1-8dfd2a198acd');

-- Verify deletion (should return 0 rows)
SELECT id, title, created_at
FROM documents
WHERE id IN ('0a0019bc-2448-4a71-87ec-76ce0a3c9b97', 'd5f85423-d7d5-4e73-a5e1-8dfd2a198acd');

-- Show how many documents remain
SELECT COUNT(*) as remaining_documents FROM documents;

COMMIT;

-- RAGAS Evaluation Database Schema
-- This database stores all data needed for RAGAS evaluation of the RAG chatbot

-- Table to track evaluation sessions
CREATE TABLE IF NOT EXISTS evaluation_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    llm_provider TEXT, -- groq, deepseek, etc.
    llm_model TEXT,    -- llama-3.1-8b-instant, etc.
    search_mode TEXT,  -- standard, rephrase, multiple_queries
    total_questions INTEGER DEFAULT 0,
    completed_questions INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active' -- active, completed, archived
);

-- Table to store questions and their metadata
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_type TEXT, -- factual, analytical, comparative, etc.
    complexity_level TEXT, -- simple, medium, complex
    expected_answer_type TEXT, -- short, detailed, list, etc.
    domain_category TEXT, -- finance, legal, technical, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES evaluation_sessions(id) ON DELETE CASCADE
);

-- Table to store LLM responses and related metadata
CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    conversation_id TEXT, -- UUID from chatbot
    llm_response TEXT NOT NULL,
    ground_truth_answer TEXT, -- Human-provided correct answer
    response_time_ms INTEGER, -- Time taken to generate response
    total_tokens_used INTEGER,
    search_mode_used TEXT,
    selected_document_ids TEXT, -- JSON array of document IDs if Knowledge Base mode
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    evaluated_at TIMESTAMP, -- When human evaluation was completed
    human_evaluator TEXT, -- Who provided the ground truth
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- Table to store actual document chunks retrieved and used by the chatbot
CREATE TABLE IF NOT EXISTS document_chunks_used (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id INTEGER NOT NULL,
    chunk_content TEXT NOT NULL,
    document_id TEXT, -- From metadata
    document_filename TEXT, -- From metadata
    chunk_metadata TEXT, -- JSON of all metadata
    relevance_score REAL, -- If available from retriever
    chunk_order INTEGER, -- Order in which chunk was retrieved (1st, 2nd, etc.)
    was_cited BOOLEAN DEFAULT FALSE, -- Whether this chunk was actually cited in response
    citation_quote TEXT, -- Exact quote if cited
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (response_id) REFERENCES responses(id) ON DELETE CASCADE
);

-- Table to store human-annotated expected chunks that should have been retrieved
CREATE TABLE IF NOT EXISTS expected_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    chunk_content TEXT NOT NULL,
    document_id TEXT NOT NULL,
    document_filename TEXT NOT NULL,
    chunk_metadata TEXT, -- JSON of metadata
    relevance_level TEXT, -- high, medium, low
    is_essential BOOLEAN DEFAULT FALSE, -- Must-have chunk for correct answer
    annotated_by TEXT, -- Human annotator
    annotation_notes TEXT, -- Why this chunk is expected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- Table to store RAGAS evaluation metrics and scores
CREATE TABLE IF NOT EXISTS evaluation_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id INTEGER NOT NULL,
    
    -- RAGAS Core Metrics
    faithfulness_score REAL, -- How faithful is the answer to the context
    answer_relevancy_score REAL, -- How relevant is the answer to the question
    context_precision_score REAL, -- How precise is the retrieved context
    context_recall_score REAL, -- How much of the relevant context was retrieved
    
    -- Additional Metrics
    answer_similarity_score REAL, -- Similarity to ground truth answer
    answer_correctness_score REAL, -- Overall correctness score
    
    -- Retrieval Metrics
    chunks_retrieved_count INTEGER,
    chunks_expected_count INTEGER,
    chunks_overlap_count INTEGER, -- How many retrieved chunks match expected
    precision_at_k REAL, -- Precision@K for retrieval
    recall_at_k REAL, -- Recall@K for retrieval
    
    -- Human Evaluation Scores (1-5 scale)
    human_relevance_score INTEGER, -- Human rating of answer relevance
    human_accuracy_score INTEGER, -- Human rating of answer accuracy  
    human_completeness_score INTEGER, -- Human rating of answer completeness
    human_clarity_score INTEGER, -- Human rating of answer clarity
    
    -- Metadata
    evaluation_method TEXT, -- ragas_auto, human_manual, hybrid
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    evaluator TEXT, -- Who performed the evaluation
    evaluation_notes TEXT, -- Additional notes about evaluation
    
    FOREIGN KEY (response_id) REFERENCES responses(id) ON DELETE CASCADE
);

-- Table to store evaluation comments and feedback
CREATE TABLE IF NOT EXISTS evaluation_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id INTEGER NOT NULL,
    feedback_type TEXT, -- error_analysis, improvement_suggestion, observation
    feedback_text TEXT NOT NULL,
    category TEXT, -- retrieval, generation, factual_accuracy, etc.
    severity TEXT, -- critical, major, minor, info
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (response_id) REFERENCES responses(id) ON DELETE CASCADE
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_questions_session_id ON questions(session_id);
CREATE INDEX IF NOT EXISTS idx_responses_question_id ON responses(question_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_response_id ON document_chunks_used(response_id);
CREATE INDEX IF NOT EXISTS idx_expected_chunks_question_id ON expected_chunks(question_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_metrics_response_id ON evaluation_metrics(response_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_feedback_response_id ON evaluation_feedback(response_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON evaluation_sessions(status);
CREATE INDEX IF NOT EXISTS idx_responses_conversation_id ON responses(conversation_id);

-- Views for common queries
CREATE VIEW IF NOT EXISTS evaluation_summary AS
SELECT 
    es.session_name,
    es.llm_provider,
    es.llm_model,
    COUNT(q.id) as total_questions,
    COUNT(r.id) as answered_questions,
    COUNT(em.id) as evaluated_responses,
    AVG(em.faithfulness_score) as avg_faithfulness,
    AVG(em.answer_relevancy_score) as avg_relevancy,
    AVG(em.context_precision_score) as avg_precision,
    AVG(em.context_recall_score) as avg_recall,
    AVG(em.human_relevance_score) as avg_human_relevance,
    AVG(em.human_accuracy_score) as avg_human_accuracy
FROM evaluation_sessions es
LEFT JOIN questions q ON es.id = q.session_id
LEFT JOIN responses r ON q.id = r.question_id
LEFT JOIN evaluation_metrics em ON r.id = em.response_id
GROUP BY es.id;

CREATE VIEW IF NOT EXISTS retrieval_performance AS
SELECT 
    r.id as response_id,
    q.question_text,
    COUNT(dcu.id) as chunks_retrieved,
    COUNT(ec.id) as chunks_expected,
    SUM(CASE WHEN ec.document_id IS NOT NULL THEN 1 ELSE 0 END) as chunks_overlap,
    em.precision_at_k,
    em.recall_at_k
FROM responses r
JOIN questions q ON r.question_id = q.id
LEFT JOIN document_chunks_used dcu ON r.id = dcu.response_id
LEFT JOIN expected_chunks ec ON q.id = ec.question_id 
    AND dcu.document_id = ec.document_id 
    AND dcu.chunk_content = ec.chunk_content
LEFT JOIN evaluation_metrics em ON r.id = em.response_id
GROUP BY r.id;

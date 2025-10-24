"""
RAG Evaluation Metrics Calculator
Fetches data from SQLite and calculates all metrics
"""
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('ragas_evaluation.db')

print("="*80)
print("RAG EVALUATION METRICS SUMMARY")
print("="*80)

# 1. FAITHFULNESS by Document Type and Model
print("\n" + "="*80)
print("1. FAITHFULNESS SCORES")
print("="*80)

faithfulness_query = """
SELECT 
    q.document_type,
    r.model_name,
    AVG(em.faithfulness) as avg_faithfulness
FROM evaluation_metrics em
JOIN responses r ON em.response_id = r.id
JOIN questions q ON r.question_id = q.id
WHERE em.faithfulness IS NOT NULL
GROUP BY q.document_type, r.model_name
ORDER BY q.document_type, r.model_name
"""

df_faithfulness = pd.read_sql_query(faithfulness_query, conn)
print(df_faithfulness.to_string(index=False))

# 2. ANSWER CORRECTNESS by Document Type and Model
print("\n" + "="*80)
print("2. ANSWER CORRECTNESS SCORES")
print("="*80)

answer_correctness_query = """
SELECT 
    q.document_type,
    r.model_name,
    AVG(em.answer_correctness) as avg_answer_correctness
FROM evaluation_metrics em
JOIN responses r ON em.response_id = r.id
JOIN questions q ON r.question_id = q.id
WHERE em.answer_correctness IS NOT NULL
GROUP BY q.document_type, r.model_name
ORDER BY q.document_type, r.model_name
"""

df_answer_correctness = pd.read_sql_query(answer_correctness_query, conn)
print(df_answer_correctness.to_string(index=False))

# 3. CONTEXT PRECISION by Document Type
print("\n" + "="*80)
print("3. CONTEXT PRECISION SCORES")
print("="*80)

context_precision_query = """
SELECT 
    q.document_type,
    AVG(em.context_precision) as avg_context_precision
FROM evaluation_metrics em
JOIN responses r ON em.response_id = r.id
JOIN questions q ON r.question_id = q.id
WHERE em.context_precision IS NOT NULL
GROUP BY q.document_type
ORDER BY q.document_type
"""

df_context_precision = pd.read_sql_query(context_precision_query, conn)
print(df_context_precision.to_string(index=False))

# 4. CONTEXT RECALL by Document Type
print("\n" + "="*80)
print("4. CONTEXT RECALL SCORES")
print("="*80)

context_recall_query = """
SELECT 
    q.document_type,
    AVG(em.context_recall) as avg_context_recall
FROM evaluation_metrics em
JOIN responses r ON em.response_id = r.id
JOIN questions q ON r.question_id = q.id
WHERE em.context_recall IS NOT NULL
GROUP BY q.document_type
ORDER BY q.document_type
"""

df_context_recall = pd.read_sql_query(context_recall_query, conn)
print(df_context_recall.to_string(index=False))

# 5. OVERALL AVERAGES
print("\n" + "="*80)
print("5. OVERALL AVERAGE SCORES (ALL DOCUMENT TYPES)")
print("="*80)

overall_query = """
SELECT 
    AVG(em.faithfulness) as avg_faithfulness,
    AVG(em.answer_correctness) as avg_answer_correctness,
    AVG(em.context_precision) as avg_context_precision,
    AVG(em.context_recall) as avg_context_recall
FROM evaluation_metrics em
WHERE em.faithfulness IS NOT NULL 
  AND em.answer_correctness IS NOT NULL
  AND em.context_precision IS NOT NULL
  AND em.context_recall IS NOT NULL
"""

df_overall = pd.read_sql_query(overall_query, conn)
print(df_overall.to_string(index=False))

print("\n" + "="*80)
print("SUMMARY COMPLETE")
print("="*80)

conn.close()

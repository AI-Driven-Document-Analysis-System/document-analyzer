"""
Evaluate Context Precision metric using RAGAS and store in database
"""
import sqlite3
from ragas import evaluate
from ragas.metrics import context_precision
from datasets import Dataset
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize evaluator LLM
evaluator_llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com",
    temperature=0
)

# Connect to database
conn = sqlite3.connect('ragas_evaluation.db')
cursor = conn.cursor()

# Fetch all responses that need context precision evaluation
query = """
SELECT 
    r.id as response_id,
    q.question_text,
    r.retrieved_contexts,
    q.ground_truth_answer
FROM responses r
JOIN questions q ON r.question_id = q.id
WHERE r.id NOT IN (
    SELECT response_id FROM evaluation_metrics WHERE context_precision IS NOT NULL
)
"""

cursor.execute(query)
rows = cursor.fetchall()

print(f"Found {len(rows)} responses to evaluate for context precision")

if len(rows) == 0:
    print("No responses to evaluate. Exiting.")
    conn.close()
    exit(0)

# Prepare data for RAGAS
data = {
    'question': [],
    'contexts': [],
    'ground_truth': []
}

response_ids = []

for row in rows:
    response_id, question, contexts, ground_truth = row
    response_ids.append(response_id)
    
    # Parse contexts (assuming JSON array format)
    import json
    contexts_list = json.loads(contexts) if contexts else []
    
    data['question'].append(question)
    data['contexts'].append(contexts_list)
    data['ground_truth'].append(ground_truth)

# Create dataset
dataset = Dataset.from_dict(data)

# Evaluate context precision
print("Evaluating context precision...")
result = evaluate(
    dataset,
    metrics=[context_precision],
    llm=evaluator_llm
)

# Store results in database
print("Storing results in database...")
for i, response_id in enumerate(response_ids):
    precision_score = result['context_precision'][i]
    
    # Check if record exists
    cursor.execute("""
        SELECT id FROM evaluation_metrics WHERE response_id = ?
    """, (response_id,))
    
    existing = cursor.fetchone()
    
    if existing:
        # Update existing record
        cursor.execute("""
            UPDATE evaluation_metrics 
            SET context_precision = ?
            WHERE response_id = ?
        """, (precision_score, response_id))
    else:
        # Insert new record
        cursor.execute("""
            INSERT INTO evaluation_metrics (response_id, context_precision)
            VALUES (?, ?)
        """, (response_id, precision_score))

conn.commit()
print(f"✅ Stored context precision scores for {len(response_ids)} responses")

# Show summary
cursor.execute("""
    SELECT 
        q.document_type,
        AVG(em.context_precision) as avg_precision,
        COUNT(*) as count
    FROM evaluation_metrics em
    JOIN responses r ON em.response_id = r.id
    JOIN questions q ON r.question_id = q.id
    WHERE em.context_precision IS NOT NULL
    GROUP BY q.document_type
    ORDER BY q.document_type
""")

print("\nContext Precision Summary:")
print("-" * 80)
for row in cursor.fetchall():
    doc_type, avg_score, count = row
    print(f"{doc_type:20} | {avg_score:.4f} ({count} responses)")

conn.close()
print("\n✅ Context precision evaluation complete!")

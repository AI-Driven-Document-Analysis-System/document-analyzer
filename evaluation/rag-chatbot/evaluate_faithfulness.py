"""
Evaluate Faithfulness metric using RAGAS and store in database
"""
import sqlite3
from ragas import evaluate
from ragas.metrics import faithfulness
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

# Fetch all responses that need faithfulness evaluation
query = """
SELECT 
    r.id as response_id,
    q.question_text,
    r.response_text,
    r.retrieved_contexts
FROM responses r
JOIN questions q ON r.question_id = q.id
WHERE r.id NOT IN (
    SELECT response_id FROM evaluation_metrics WHERE faithfulness IS NOT NULL
)
"""

cursor.execute(query)
rows = cursor.fetchall()

print(f"Found {len(rows)} responses to evaluate for faithfulness")

if len(rows) == 0:
    print("No responses to evaluate. Exiting.")
    conn.close()
    exit(0)

# Prepare data for RAGAS
data = {
    'question': [],
    'answer': [],
    'contexts': []
}

response_ids = []

for row in rows:
    response_id, question, answer, contexts = row
    response_ids.append(response_id)
    
    # Parse contexts (assuming JSON array format)
    import json
    contexts_list = json.loads(contexts) if contexts else []
    
    data['question'].append(question)
    data['answer'].append(answer)
    data['contexts'].append(contexts_list)

# Create dataset
dataset = Dataset.from_dict(data)

# Evaluate faithfulness
print("Evaluating faithfulness...")
result = evaluate(
    dataset,
    metrics=[faithfulness],
    llm=evaluator_llm
)

# Store results in database
print("Storing results in database...")
for i, response_id in enumerate(response_ids):
    faithfulness_score = result['faithfulness'][i]
    
    # Check if record exists
    cursor.execute("""
        SELECT id FROM evaluation_metrics WHERE response_id = ?
    """, (response_id,))
    
    existing = cursor.fetchone()
    
    if existing:
        # Update existing record
        cursor.execute("""
            UPDATE evaluation_metrics 
            SET faithfulness = ?
            WHERE response_id = ?
        """, (faithfulness_score, response_id))
    else:
        # Insert new record
        cursor.execute("""
            INSERT INTO evaluation_metrics (response_id, faithfulness)
            VALUES (?, ?)
        """, (response_id, faithfulness_score))

conn.commit()
print(f"✅ Stored faithfulness scores for {len(response_ids)} responses")

# Show summary
cursor.execute("""
    SELECT 
        q.document_type,
        r.model_name,
        AVG(em.faithfulness) as avg_faithfulness,
        COUNT(*) as count
    FROM evaluation_metrics em
    JOIN responses r ON em.response_id = r.id
    JOIN questions q ON r.question_id = q.id
    WHERE em.faithfulness IS NOT NULL
    GROUP BY q.document_type, r.model_name
    ORDER BY q.document_type, r.model_name
""")

print("\nFaithfulness Summary:")
print("-" * 80)
for row in cursor.fetchall():
    doc_type, model, avg_score, count = row
    print(f"{doc_type:20} | {model:20} | {avg_score:.4f} ({count} responses)")

conn.close()
print("\n✅ Faithfulness evaluation complete!")

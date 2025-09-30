"""
RAGAS Evaluation Script
Evaluates chatbot responses using RAGAS metrics: Faithfulness, Answer Correctness, Answer Relevancy
"""

import os
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    answer_correctness
)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGASEvaluator:
    """Evaluates RAG chatbot responses using RAGAS metrics."""
    
    def __init__(self, db_path: str = None, api_key: str = None, use_deepseek: bool = True):
        """
        Initialize RAGAS evaluator.
        
        Args:
            db_path: Path to SQLite evaluation database
            api_key: API key (DeepSeek or OpenAI)
            use_deepseek: If True, uses DeepSeek API (default), else uses OpenAI
        """
        if db_path is None:
            db_path = Path(__file__).parent / "ragas_evaluation.db"
        
        self.db_path = str(db_path)
        
        if use_deepseek:
            # Use DeepSeek API (OpenAI-compatible)
            deepseek_key = api_key or os.getenv("DEEPSEEK_API_KEY")
            if not deepseek_key:
                raise ValueError("DeepSeek API key required. Set DEEPSEEK_API_KEY environment variable.")
            
            # DeepSeek uses OpenAI-compatible API
            self.llm = ChatOpenAI(
                model="deepseek-chat",
                api_key=deepseek_key,
                base_url="https://api.deepseek.com",
                temperature=0,
                model_kwargs={"n": 1}  # DeepSeek only supports n=1
            )
            
            # Use HuggingFace embeddings (free, local)
            from langchain_huggingface import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            logger.info("RAGAS Evaluator initialized with DeepSeek API")
        else:
            # Use OpenAI
            openai_key = api_key or os.getenv("OPENAI_API_KEY")
            if not openai_key:
                raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
            
            self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_key, temperature=0)
            self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_key)
            logger.info("RAGAS Evaluator initialized with OpenAI API")
    
    def fetch_responses_for_evaluation(self, response_ids: List[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch responses with ground truth and retrieved chunks from database.
        
        Args:
            response_ids: Optional list of specific response IDs to fetch. If None, fetches all.
        
        Returns:
            List of response data dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query with optional ID filter
        if response_ids:
            placeholders = ','.join('?' * len(response_ids))
            query = f"""
                SELECT 
                    r.id as response_id,
                    q.question_text,
                    r.llm_response,
                    r.ground_truth_answer
                FROM responses r
                JOIN questions q ON r.question_id = q.id
                WHERE r.ground_truth_answer IS NOT NULL
                AND r.id IN ({placeholders})
                ORDER BY r.id
            """
            cursor.execute(query, response_ids)
        else:
            cursor.execute("""
                SELECT 
                    r.id as response_id,
                    q.question_text,
                    r.llm_response,
                    r.ground_truth_answer
                FROM responses r
                JOIN questions q ON r.question_id = q.id
                WHERE r.ground_truth_answer IS NOT NULL
                ORDER BY r.created_at
            """)
        
        responses = []
        for row in cursor.fetchall():
            response_data = dict(row)
            
            # Fetch retrieved chunks (contexts) for this response
            cursor.execute("""
                SELECT chunk_content
                FROM document_chunks_used
                WHERE response_id = ?
                ORDER BY chunk_order
            """, (response_data['response_id'],))
            
            contexts = [chunk[0] for chunk in cursor.fetchall()]
            response_data['contexts'] = contexts
            
            responses.append(response_data)
        
        conn.close()
        logger.info(f"Fetched {len(responses)} responses for evaluation")
        return responses
    
    def prepare_ragas_dataset(self, responses: List[Dict[str, Any]]) -> Dataset:
        """
        Convert response data to RAGAS dataset format.
        
        Args:
            responses: List of response dictionaries
            
        Returns:
            HuggingFace Dataset for RAGAS evaluation
        """
        data = {
            'question': [],
            'answer': [],
            'contexts': [],
            'ground_truth': []
        }
        
        for resp in responses:
            data['question'].append(resp['question_text'])
            data['answer'].append(resp['llm_response'])
            data['contexts'].append(resp['contexts'])
            data['ground_truth'].append(resp['ground_truth_answer'])
        
        dataset = Dataset.from_dict(data)
        logger.info(f"Prepared RAGAS dataset with {len(dataset)} samples")
        return dataset
    
    def evaluate_responses(self, response_ids: List[int] = None, metrics_list: List[str] = None) -> Dict[str, Any]:
        """
        Run RAGAS evaluation on responses.
        
        Args:
            response_ids: Optional list of specific response IDs to evaluate. If None, evaluates all.
            metrics_list: Optional list of metric names to evaluate. Default: ['faithfulness', 'answer_correctness']
        
        Returns:
            Evaluation results dictionary
        """
        logger.info(f"Starting RAGAS evaluation{f' for {len(response_ids)} responses' if response_ids else ''}...")
        
        # Fetch data
        responses = self.fetch_responses_for_evaluation(response_ids)
        if not responses:
            logger.warning("No responses with ground truth found for evaluation")
            return {}
        
        # Prepare dataset
        dataset = self.prepare_ragas_dataset(responses)
        
        # Run RAGAS evaluation
        # Note: answer_relevancy requires n>1 which DeepSeek doesn't support
        # Using only faithfulness and answer_correctness
        if metrics_list:
            available_metrics = {
                'faithfulness': faithfulness,
                'answer_correctness': answer_correctness,
                'answer_relevancy': answer_relevancy
            }
            metrics = [available_metrics[m] for m in metrics_list if m in available_metrics]
        else:
            metrics = [faithfulness, answer_correctness]
        
        logger.info("Running RAGAS metrics evaluation...")
        
        # Wrap LLM to handle DeepSeek limitations
        from ragas.llms import LangchainLLMWrapper
        wrapped_llm = LangchainLLMWrapper(self.llm)
        
        result = evaluate(
            dataset,
            metrics=metrics,
            llm=wrapped_llm,
            embeddings=self.embeddings,
            raise_exceptions=False  # Continue on errors
        )
        
        logger.info("RAGAS evaluation completed")
        
        # Extract per-sample scores from the result dataset
        result_dict = {
            'faithfulness': result['faithfulness'] if 'faithfulness' in result else None,
            'answer_correctness': result['answer_correctness'] if 'answer_correctness' in result else None,
        }
        
        # Try to get per-sample scores from the dataset
        if hasattr(result, 'to_pandas'):
            df = result.to_pandas()
            if 'faithfulness' in df.columns:
                result_dict['faithfulness_per_sample'] = df['faithfulness'].tolist()
            if 'answer_correctness' in df.columns:
                result_dict['answer_correctness_per_sample'] = df['answer_correctness'].tolist()
        
        return result_dict
    
    def save_evaluation_results(self, results: Dict[str, Any]):
        """
        Save RAGAS evaluation results back to database.
        
        Args:
            results: RAGAS evaluation results
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Fetch response IDs in order
        cursor.execute("""
            SELECT r.id
            FROM responses r
            JOIN questions q ON r.question_id = q.id
            WHERE r.ground_truth_answer IS NOT NULL
            ORDER BY r.created_at
        """)
        response_ids = [row[0] for row in cursor.fetchall()]
        
        # Try to get per-sample scores first
        faithfulness_scores = results.get('faithfulness_per_sample', [])
        correctness_scores = results.get('answer_correctness_per_sample', [])
        
        # If no per-sample scores, use aggregate (will be same for all)
        faithfulness_agg = results.get('faithfulness') if not faithfulness_scores else None
        correctness_agg = results.get('answer_correctness') if not correctness_scores else None
        
        # Save to evaluation_metrics table
        for i, response_id in enumerate(response_ids):
            faithfulness_score = faithfulness_scores[i] if i < len(faithfulness_scores) else faithfulness_agg
            correctness_score = correctness_scores[i] if i < len(correctness_scores) else correctness_agg
            
            # Check if metrics already exist
            cursor.execute("""
                SELECT id FROM evaluation_metrics WHERE response_id = ?
            """, (response_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing
                cursor.execute("""
                    UPDATE evaluation_metrics
                    SET faithfulness_score = ?,
                        answer_correctness_score = ?,
                        evaluation_method = 'ragas_auto',
                        evaluated_at = CURRENT_TIMESTAMP
                    WHERE response_id = ?
                """, (faithfulness_score, correctness_score, response_id))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO evaluation_metrics (
                        response_id,
                        faithfulness_score,
                        answer_correctness_score,
                        evaluation_method
                    ) VALUES (?, ?, ?, 'ragas_auto')
                """, (response_id, faithfulness_score, correctness_score))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved evaluation results for {len(response_ids)} responses")
    
    def print_results_summary(self, results: Dict[str, Any]):
        """
        Print a summary of evaluation results.
        
        Args:
            results: RAGAS evaluation results
        """
        print("\n" + "="*80)
        print("RAGAS EVALUATION RESULTS (DeepSeek API)")
        print("="*80)
        
        if 'faithfulness' in results:
            print(f"\n📊 Faithfulness Score: {results['faithfulness']:.4f}")
            print("   (How factually grounded the answers are in the retrieved context)")
        
        if 'answer_correctness' in results:
            print(f"\n✅ Answer Correctness Score: {results['answer_correctness']:.4f}")
            print("   (Semantic similarity to ground truth answers)")
        
        print("\n" + "="*80)
        print("Scores range from 0.0 to 1.0 (higher is better)")
        print("Note: Answer Relevancy metric skipped (requires OpenAI API)")
        print("="*80 + "\n")
    
    def run_full_evaluation(self):
        """Run complete evaluation pipeline."""
        try:
            # Evaluate
            results = self.evaluate_responses()
            
            if not results:
                logger.warning("No evaluation results generated")
                return
            
            # Print summary
            self.print_results_summary(results)
            
            # Save to database
            self.save_evaluation_results(results)
            
            logger.info("✅ Full evaluation completed successfully")
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            raise


def main():
    """Main execution function."""
    # Initialize evaluator
    evaluator = RAGASEvaluator()
    
    # Run evaluation
    evaluator.run_full_evaluation()


if __name__ == "__main__":
    main()

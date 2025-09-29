"""
Evaluation API Endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict, Any
import os
import tempfile

from app.services.evaluation.ragas_evaluator import RAGASEvaluator

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])


@router.post("/run")
async def run_evaluation(csv_file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Run RAGAS evaluation with uploaded CSV file
    
    CSV Format:
    question,ground_truth_answer,expected_chunks,category
    """
    # Validate file type
    if not csv_file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as temp_file:
        content = await csv_file.read()
        temp_file.write(content)
        temp_csv_path = temp_file.name
    
    try:
        # Initialize evaluator and run evaluation
        evaluator = RAGASEvaluator()
        results = evaluator.run_hybrid_evaluation(temp_csv_path)
        
        # Remove detailed results for API response (too large)
        api_results = {
            "timestamp": results["timestamp"],
            "num_questions": results["num_questions"],
            "automated": results["automated"],
            "ground_truth": results["ground_truth"],
            "overall_score": results["overall_score"]
        }
        
        return {
            "success": True,
            "message": "Evaluation completed successfully",
            "results": api_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_csv_path):
            os.unlink(temp_csv_path)


@router.get("/latest")
async def get_latest_evaluation() -> Dict[str, Any]:
    """Get the most recent evaluation results"""
    evaluator = RAGASEvaluator()
    results = evaluator.get_latest_results()
    
    if not results:
        raise HTTPException(status_code=404, detail="No evaluation results found")
    
    # Remove detailed results for API response
    api_results = {
        "timestamp": results["timestamp"],
        "num_questions": results["num_questions"],
        "automated": results["automated"],
        "ground_truth": results["ground_truth"],
        "overall_score": results["overall_score"]
    }
    
    return {
        "success": True,
        "results": api_results
    }


@router.get("/status")
async def get_evaluation_status() -> Dict[str, Any]:
    """Get evaluation system status"""
    evaluator = RAGASEvaluator()
    latest_results = evaluator.get_latest_results()
    
    return {
        "success": True,
        "status": {
            "evaluation_available": latest_results is not None,
            "last_evaluation": latest_results["timestamp"] if latest_results else None,
            "results_directory": str(evaluator.results_dir)
        }
    }

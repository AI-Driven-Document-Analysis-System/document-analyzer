#!/usr/bin/env python3
"""
ROUGE Evaluation System for Summarization
Evaluates generated summaries against reference summaries using ROUGE metrics
"""

import os
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime
import re

# Install required packages if not available
try:
    from rouge_score import rouge_scorer
    from rouge_score.scoring import BootstrapAggregator
except ImportError:
    print("Installing required packages...")
    os.system("pip install rouge-score")
    from rouge_score import rouge_scorer
    from rouge_score.scoring import BootstrapAggregator

try:
    import nltk
    from nltk.tokenize import sent_tokenize
    nltk.download('punkt', quiet=True)
except ImportError:
    print("Installing NLTK...")
    os.system("pip install nltk")
    import nltk
    from nltk.tokenize import sent_tokenize
    nltk.download('punkt', quiet=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ROUGEEvaluator:
    """
    ROUGE Evaluation system for summarization models
    """
    
    def __init__(self, rouge_types=['rouge1', 'rouge2', 'rougeL'], use_stemmer=True):
        """
        Initialize ROUGE evaluator
        
        Args:
            rouge_types: List of ROUGE metrics to compute
            use_stemmer: Whether to use stemming for evaluation
        """
        self.rouge_types = rouge_types
        self.scorer = rouge_scorer.RougeScorer(rouge_types, use_stemmer=use_stemmer)
        self.aggregator = BootstrapAggregator()
        
    def clean_summary_text(self, text: str) -> str:
        """
        Clean summary text by removing formatting and extracting actual summary content
        
        Args:
            text: Raw summary text (may contain headers, formatting, etc.)
            
        Returns:
            Cleaned summary text
        """
        # Remove common headers and formatting
        headers_to_remove = [
            r'BRIEF OVERVIEW\n═+\n\n',
            r'COMPREHENSIVE ANALYSIS\n═+\n\n',
            r'EXECUTIVE SUMMARY\n═+\n\n',
            r'CASE OVERVIEW\n═+\n\n',
            r'DOCUMENT SUMMARY\n═+\n\n',
            r'CLINICAL OVERVIEW\n═+\n\n',
            r'LEGAL SUMMARY\n═+\n\n',
            r'SUMMARY\n═+\n\n',
            r'═+',
            r'▌[^:]+:\n',  # Remove entity type headers
            r'┌─[^─]+─┐\n',  # Remove insight boxes
            r'EXTRACTED ENTITIES\n[^┌]*(?=┌|$)',  # Remove entity sections
        ]
        
        cleaned_text = text
        
        # Remove headers and formatting
        for pattern in headers_to_remove:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.MULTILINE | re.DOTALL)
        
        # Remove bullet points and entity lists
        lines = cleaned_text.split('\n')
        summary_lines = []
        
        skip_section = False
        for line in lines:
            line = line.strip()
            
            # Skip entity sections and similar
            if any(marker in line.lower() for marker in ['extracted entities', 'key insights', 'clinical overview']):
                skip_section = True
                continue
            
            # Skip bullet point lists and entity entries
            if line.startswith('•') or line.startswith('-') or line.startswith('▌'):
                continue
                
            # Skip empty lines and section separators
            if not line or line.startswith('═') or line.startswith('┌'):
                continue
                
            # If we hit a new content section, stop skipping
            if skip_section and len(line) > 20 and not line.startswith('•'):
                skip_section = False
                
            if not skip_section:
                summary_lines.append(line)
        
        # Join and clean up
        cleaned_text = ' '.join(summary_lines)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Normalize whitespace
        cleaned_text = cleaned_text.strip()
        
        return cleaned_text
    
    def load_summaries_from_file(self, file_path: str) -> List[str]:
        """
        Load summaries from a file (supports .txt, .json, .jsonl)
        
        Args:
            file_path: Path to the summaries file
            
        Returns:
            List of summary texts
        """
        file_path = Path(file_path)
        summaries = []
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    summaries = [str(item) if isinstance(item, str) else item.get('summary', item.get('text', str(item))) for item in data]
                elif isinstance(data, dict):
                    summaries = [data.get('summary', data.get('text', str(data)))]
                    
        elif file_path.suffix == '.jsonl':
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    item = json.loads(line.strip())
                    if isinstance(item, str):
                        summaries.append(item)
                    else:
                        summaries.append(item.get('summary', item.get('text', str(item))))
                        
        else:  # .txt or other text files
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Try to split by common delimiters
            if '\n\n---\n\n' in content:
                summaries = content.split('\n\n---\n\n')
            elif '\n---\n' in content:
                summaries = content.split('\n---\n')
            elif '\n\n' in content and len(content.split('\n\n')) > 1:
                summaries = content.split('\n\n')
            else:
                summaries = [content]
        
        # Clean each summary
        cleaned_summaries = []
        for summary in summaries:
            cleaned = self.clean_summary_text(str(summary))
            if cleaned.strip():  # Only add non-empty summaries
                cleaned_summaries.append(cleaned)
        
        logger.info(f"Loaded {len(cleaned_summaries)} summaries from {file_path}")
        return cleaned_summaries
    
    def evaluate_single_pair(self, generated_summary: str, reference_summary: str) -> Dict[str, Dict[str, float]]:
        """
        Evaluate a single generated-reference summary pair
        
        Args:
            generated_summary: Generated summary text
            reference_summary: Reference (gold standard) summary text
            
        Returns:
            Dictionary with ROUGE scores
        """
        # Clean both summaries
        generated_clean = self.clean_summary_text(generated_summary)
        reference_clean = self.clean_summary_text(reference_summary)
        
        if not generated_clean.strip() or not reference_clean.strip():
            logger.warning("Empty summary detected, skipping evaluation")
            return {rouge_type: {'precision': 0.0, 'recall': 0.0, 'fmeasure': 0.0} for rouge_type in self.rouge_types}
        
        # Compute ROUGE scores
        scores = self.scorer.score(reference_clean, generated_clean)
        
        # Convert to dictionary format
        result = {}
        for rouge_type in self.rouge_types:
            if rouge_type in scores:
                score = scores[rouge_type]
                result[rouge_type] = {
                    'precision': score.precision,
                    'recall': score.recall,
                    'fmeasure': score.fmeasure
                }
        
        return result
    
    def evaluate_batch(self, generated_summaries: List[str], reference_summaries: List[str]) -> Dict:
        """
        Evaluate a batch of summary pairs and compute aggregate statistics
        
        Args:
            generated_summaries: List of generated summaries
            reference_summaries: List of reference summaries
            
        Returns:
            Dictionary with detailed evaluation results
        """
        if len(generated_summaries) != len(reference_summaries):
            raise ValueError(f"Mismatch in number of summaries: {len(generated_summaries)} generated vs {len(reference_summaries)} reference")
        
        logger.info(f"Evaluating {len(generated_summaries)} summary pairs...")
        
        # Store individual scores
        individual_scores = []
        all_scores = {rouge_type: {'precision': [], 'recall': [], 'fmeasure': []} for rouge_type in self.rouge_types}
        
        # Evaluate each pair
        for i, (gen_sum, ref_sum) in enumerate(zip(generated_summaries, reference_summaries)):
            try:
                scores = self.evaluate_single_pair(gen_sum, ref_sum)
                individual_scores.append(scores)
                
                # Collect scores for aggregation
                for rouge_type in self.rouge_types:
                    if rouge_type in scores:
                        all_scores[rouge_type]['precision'].append(scores[rouge_type]['precision'])
                        all_scores[rouge_type]['recall'].append(scores[rouge_type]['recall'])
                        all_scores[rouge_type]['fmeasure'].append(scores[rouge_type]['fmeasure'])
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(generated_summaries)} pairs")
                    
            except Exception as e:
                logger.error(f"Error evaluating pair {i}: {e}")
                individual_scores.append({rouge_type: {'precision': 0.0, 'recall': 0.0, 'fmeasure': 0.0} for rouge_type in self.rouge_types})
        
        # Compute aggregate statistics
        aggregate_scores = {}
        for rouge_type in self.rouge_types:
            if rouge_type in all_scores and all_scores[rouge_type]['fmeasure']:
                aggregate_scores[rouge_type] = {
                    'precision': {
                        'mean': sum(all_scores[rouge_type]['precision']) / len(all_scores[rouge_type]['precision']),
                        'std': self._compute_std(all_scores[rouge_type]['precision']),
                        'min': min(all_scores[rouge_type]['precision']),
                        'max': max(all_scores[rouge_type]['precision'])
                    },
                    'recall': {
                        'mean': sum(all_scores[rouge_type]['recall']) / len(all_scores[rouge_type]['recall']),
                        'std': self._compute_std(all_scores[rouge_type]['recall']),
                        'min': min(all_scores[rouge_type]['recall']),
                        'max': max(all_scores[rouge_type]['recall'])
                    },
                    'fmeasure': {
                        'mean': sum(all_scores[rouge_type]['fmeasure']) / len(all_scores[rouge_type]['fmeasure']),
                        'std': self._compute_std(all_scores[rouge_type]['fmeasure']),
                        'min': min(all_scores[rouge_type]['fmeasure']),
                        'max': max(all_scores[rouge_type]['fmeasure'])
                    }
                }
        
        return {
            'individual_scores': individual_scores,
            'aggregate_scores': aggregate_scores,
            'summary_stats': {
                'total_pairs': len(generated_summaries),
                'successful_evaluations': len([s for s in individual_scores if any(s[rt]['fmeasure'] > 0 for rt in self.rouge_types)]),
                'evaluation_timestamp': datetime.now().isoformat()
            }
        }
    
    def _compute_std(self, values: List[float]) -> float:
        """Compute standard deviation"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def evaluate_from_files(self, generated_path: str, reference_path: str, output_path: Optional[str] = None) -> Dict:
        """
        Evaluate summaries from files
        
        Args:
            generated_path: Path to generated summaries file
            reference_path: Path to reference summaries file
            output_path: Optional path to save results
            
        Returns:
            Evaluation results dictionary
        """
        logger.info(f"Loading generated summaries from: {generated_path}")
        generated_summaries = self.load_summaries_from_file(generated_path)
        
        logger.info(f"Loading reference summaries from: {reference_path}")
        reference_summaries = self.load_summaries_from_file(reference_path)
        
        # Evaluate
        results = self.evaluate_batch(generated_summaries, reference_summaries)
        
        # Save results if output path provided
        if output_path:
            self.save_results(results, output_path)
        
        return results
    
    def save_results(self, results: Dict, output_path: str):
        """
        Save evaluation results to file
        
        Args:
            results: Results dictionary from evaluate_batch
            output_path: Path to save results
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to: {output_path}")
        
        # Also create a summary report
        report_path = output_path.parent / f"{output_path.stem}_summary.txt"
        self.create_summary_report(results, report_path)
    
    def create_summary_report(self, results: Dict, report_path: str):
        """
        Create a human-readable summary report
        
        Args:
            results: Results dictionary from evaluate_batch
            report_path: Path to save the summary report
        """
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("ROUGE EVALUATION SUMMARY REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            # Summary statistics
            stats = results['summary_stats']
            f.write(f"Evaluation Date: {stats['evaluation_timestamp']}\n")
            f.write(f"Total Summary Pairs: {stats['total_pairs']}\n")
            f.write(f"Successful Evaluations: {stats['successful_evaluations']}\n")
            f.write(f"Success Rate: {stats['successful_evaluations']/stats['total_pairs']*100:.1f}%\n\n")
            
            # Aggregate scores
            f.write("AGGREGATE ROUGE SCORES\n")
            f.write("-" * 30 + "\n\n")
            
            aggregate = results['aggregate_scores']
            for rouge_type in self.rouge_types:
                if rouge_type in aggregate:
                    f.write(f"{rouge_type.upper()}:\n")
                    scores = aggregate[rouge_type]
                    
                    f.write(f"  Precision: {scores['precision']['mean']:.4f} (±{scores['precision']['std']:.4f})\n")
                    f.write(f"  Recall:    {scores['recall']['mean']:.4f} (±{scores['recall']['std']:.4f})\n")
                    f.write(f"  F-measure: {scores['fmeasure']['mean']:.4f} (±{scores['fmeasure']['std']:.4f})\n")
                    f.write(f"  Range:     [{scores['fmeasure']['min']:.4f}, {scores['fmeasure']['max']:.4f}]\n\n")
            
            # Performance interpretation
            f.write("PERFORMANCE INTERPRETATION\n")
            f.write("-" * 30 + "\n\n")
            
            if 'rouge1' in aggregate:
                r1_f = aggregate['rouge1']['fmeasure']['mean']
                if r1_f >= 0.4:
                    interpretation = "Excellent"
                elif r1_f >= 0.3:
                    interpretation = "Good"
                elif r1_f >= 0.2:
                    interpretation = "Fair"
                else:
                    interpretation = "Needs Improvement"
                
                f.write(f"Overall Performance: {interpretation} (ROUGE-1 F-measure: {r1_f:.4f})\n\n")
            
            f.write("ROUGE Score Interpretation:\n")
            f.write("- ROUGE-1: Unigram overlap (word-level similarity)\n")
            f.write("- ROUGE-2: Bigram overlap (phrase-level similarity)\n")
            f.write("- ROUGE-L: Longest common subsequence (sequence similarity)\n\n")
            
            f.write("Typical Benchmarks:\n")
            f.write("- Excellent: ROUGE-1 > 0.40, ROUGE-2 > 0.20, ROUGE-L > 0.35\n")
            f.write("- Good:      ROUGE-1 > 0.30, ROUGE-2 > 0.15, ROUGE-L > 0.25\n")
            f.write("- Fair:      ROUGE-1 > 0.20, ROUGE-2 > 0.10, ROUGE-L > 0.18\n")
        
        logger.info(f"Summary report saved to: {report_path}")

def main():
    """
    Main function for command-line usage
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate summaries using ROUGE metrics")
    parser.add_argument("--generated", "-g", required=True, help="Path to generated summaries file")
    parser.add_argument("--reference", "-r", required=True, help="Path to reference summaries file")
    parser.add_argument("--output", "-o", help="Path to save evaluation results")
    parser.add_argument("--rouge-types", nargs="+", default=['rouge1', 'rouge2', 'rougeL'], 
                       help="ROUGE metrics to compute")
    parser.add_argument("--no-stemmer", action="store_true", help="Disable stemming")
    
    args = parser.parse_args()
    
    # Initialize evaluator
    evaluator = ROUGEEvaluator(
        rouge_types=args.rouge_types,
        use_stemmer=not args.no_stemmer
    )
    
    # Run evaluation
    try:
        results = evaluator.evaluate_from_files(
            generated_path=args.generated,
            reference_path=args.reference,
            output_path=args.output
        )
        
        # Print summary to console
        print("\n" + "="*60)
        print("ROUGE EVALUATION RESULTS")
        print("="*60)
        
        aggregate = results['aggregate_scores']
        for rouge_type in args.rouge_types:
            if rouge_type in aggregate:
                scores = aggregate[rouge_type]
                print(f"\n{rouge_type.upper()}:")
                print(f"  Precision: {scores['precision']['mean']:.4f} (±{scores['precision']['std']:.4f})")
                print(f"  Recall:    {scores['recall']['mean']:.4f} (±{scores['recall']['std']:.4f})")
                print(f"  F-measure: {scores['fmeasure']['mean']:.4f} (±{scores['fmeasure']['std']:.4f})")
        
        print(f"\nEvaluated {results['summary_stats']['total_pairs']} summary pairs")
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise

if __name__ == "__main__":
    main()

# Example usage for your summarization system:
"""
# 1. Save your generated summaries to a text file (one per line or separated by ---)
# 2. Save your reference summaries to another text file in the same format
# 3. Run evaluation:

from rouge_evaluator import ROUGEEvaluator

evaluator = ROUGEEvaluator()
results = evaluator.evaluate_from_files(
    generated_path="generated_summaries.txt",
    reference_path="reference_summaries.txt",
    output_path="evaluation_results.json"
)

print(f"ROUGE-1 F-measure: {results['aggregate_scores']['rouge1']['fmeasure']['mean']:.4f}")
print(f"ROUGE-2 F-measure: {results['aggregate_scores']['rouge2']['fmeasure']['mean']:.4f}")
print(f"ROUGE-L F-measure: {results['aggregate_scores']['rougeL']['fmeasure']['mean']:.4f}")
"""
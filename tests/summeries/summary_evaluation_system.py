# Fixed Summary Evaluation System - No Circular Imports
# Save this as: summary_evaluation_system.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from rouge_score import rouge_scorer
from bert_score import BERTScorer
import warnings
import os
from datetime import datetime

warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('default')
sns.set_palette("husl")

class SummaryEvaluator:
    """
    Comprehensive summary evaluation system using ROUGE and BERTScore metrics
    """
    
    def __init__(self):
        print("Initializing evaluation models...")
        
        # Initialize ROUGE scorer with multiple metrics
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ['rouge1', 'rouge2', 'rougeL'], 
            use_stemmer=True
        )
        
        # Initialize BERTScore with different models for robustness
        try:
            print("Loading DeBERTa model for BERTScore...")
            self.bert_scorer_en = BERTScorer(
                model_type="microsoft/deberta-xlarge-mnli",
                lang="en",
                rescale_with_baseline=True
            )
        except Exception as e:
            print(f"DeBERTa model failed, using fallback: {e}")
            self.bert_scorer_en = BERTScorer(
                model_type="distilbert-base-uncased",
                lang="en",
                rescale_with_baseline=True
            )
        
        # Alternative BERTScore model for comparison
        try:
            print("Loading RoBERTa model for BERTScore...")
            self.bert_scorer_roberta = BERTScorer(
                model_type="roberta-large",
                lang="en", 
                rescale_with_baseline=True
            )
        except Exception as e:
            print(f"RoBERTa model failed, using same as primary: {e}")
            self.bert_scorer_roberta = self.bert_scorer_en
        
        self.evaluation_results = []
        print("Evaluator initialized successfully!")
        
    def calculate_rouge_scores(self, generated_summary, reference_summary):
        """
        Calculate ROUGE scores (ROUGE-1, ROUGE-2, ROUGE-L)
        """
        scores = self.rouge_scorer.score(reference_summary, generated_summary)
        
        rouge_metrics = {
            'rouge1_precision': scores['rouge1'].precision,
            'rouge1_recall': scores['rouge1'].recall,
            'rouge1_f1': scores['rouge1'].fmeasure,
            'rouge2_precision': scores['rouge2'].precision,
            'rouge2_recall': scores['rouge2'].recall,
            'rouge2_f1': scores['rouge2'].fmeasure,
            'rougeL_precision': scores['rougeL'].precision,
            'rougeL_recall': scores['rougeL'].recall,
            'rougeL_f1': scores['rougeL'].fmeasure,
        }
        
        return rouge_metrics
    
    def calculate_bert_scores(self, generated_summary, reference_summary):
        """
        Calculate BERTScore using multiple models
        """
        # Primary BERTScore (DeBERTa)
        P1, R1, F1_1 = self.bert_scorer_en.score([generated_summary], [reference_summary])
        
        # Secondary BERTScore (RoBERTa) 
        P2, R2, F1_2 = self.bert_scorer_roberta.score([generated_summary], [reference_summary])
        
        bert_metrics = {
            'bert_precision_deberta': P1.item(),
            'bert_recall_deberta': R1.item(), 
            'bert_f1_deberta': F1_1.item(),
            'bert_precision_roberta': P2.item(),
            'bert_recall_roberta': R2.item(),
            'bert_f1_roberta': F1_2.item(),
            'bert_avg_precision': (P1.item() + P2.item()) / 2,
            'bert_avg_recall': (R1.item() + R2.item()) / 2,
            'bert_avg_f1': (F1_1.item() + F1_2.item()) / 2
        }
        
        return bert_metrics
    
    def calculate_consistency_score(self, generated_summary, reference_summary):
        """
        Calculate consistency score based on overlapping content
        """
        gen_words = set(generated_summary.lower().split())
        ref_words = set(reference_summary.lower().split())
        
        if len(ref_words) == 0:
            return 0.0
            
        overlap = len(gen_words.intersection(ref_words))
        consistency = overlap / len(ref_words)
        
        return consistency
    
    def calculate_relevancy_score(self, generated_summary, reference_summary):
        """
        Calculate relevancy using semantic similarity approach
        """
        gen_words = set(generated_summary.lower().split())
        ref_words = set(reference_summary.lower().split())
        
        if len(gen_words.union(ref_words)) == 0:
            return 0.0
            
        jaccard_similarity = len(gen_words.intersection(ref_words)) / len(gen_words.union(ref_words))
        return jaccard_similarity
    
    def calculate_accuracy_score(self, generated_summary, reference_summary):
        """
        Calculate accuracy as a combination of ROUGE-L and BERTScore F1
        """
        rouge_scores = self.calculate_rouge_scores(generated_summary, reference_summary)
        bert_scores = self.calculate_bert_scores(generated_summary, reference_summary)
        
        # Weighted combination of ROUGE-L F1 and BERTScore F1
        accuracy = (0.4 * rouge_scores['rougeL_f1'] + 
                   0.6 * bert_scores['bert_avg_f1'])
        
        return accuracy
    
    def evaluate_summary(self, generated_summary, reference_summary, summary_type, document_id=None):
        """
        Comprehensive evaluation of a single summary
        """
        print(f"Evaluating {summary_type} summary...")
        
        # Calculate all metrics
        rouge_metrics = self.calculate_rouge_scores(generated_summary, reference_summary)
        bert_metrics = self.calculate_bert_scores(generated_summary, reference_summary)
        
        consistency = self.calculate_consistency_score(generated_summary, reference_summary)
        relevancy = self.calculate_relevancy_score(generated_summary, reference_summary)
        accuracy = self.calculate_accuracy_score(generated_summary, reference_summary)
        
        # Combine all metrics
        evaluation_result = {
            'document_id': document_id or f"doc_{len(self.evaluation_results)}",
            'summary_type': summary_type,
            'generated_summary': generated_summary,
            'reference_summary': reference_summary,
            'consistency': consistency,
            'relevancy': relevancy,
            'accuracy': accuracy,
            **rouge_metrics,
            **bert_metrics
        }
        
        self.evaluation_results.append(evaluation_result)
        print(f"Completed evaluation for {summary_type}")
        return evaluation_result
    
    def evaluate_multiple_summaries(self, summary_data):
        """
        Evaluate multiple summaries and summary types
        
        summary_data format:
        [
            {
                'document_id': 'doc_1',
                'generated_summary': '...',
                'reference_summary': '...',
                'summary_type': 'brief'
            },
            ...
        ]
        """
        print(f"Starting batch evaluation of {len(summary_data)} summaries...")
        results = []
        
        for i, data in enumerate(summary_data):
            print(f"Processing summary {i+1}/{len(summary_data)}")
            result = self.evaluate_summary(
                generated_summary=data['generated_summary'],
                reference_summary=data['reference_summary'],
                summary_type=data['summary_type'],
                document_id=data.get('document_id', f"doc_{len(results)}")
            )
            results.append(result)
            
        print("Batch evaluation completed!")
        return results
    
    def get_results_dataframe(self):
        """
        Convert results to pandas DataFrame for analysis
        """
        return pd.DataFrame(self.evaluation_results)
    
    def create_comprehensive_visualization(self, save_path=None):
        """
        Create comprehensive visualization dashboard
        """
        if not self.evaluation_results:
            print("No evaluation results available. Please run evaluations first.")
            return
            
        df = self.get_results_dataframe()
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 15))
        fig.suptitle('Summary Evaluation Dashboard', fontsize=16, fontweight='bold', y=0.98)
        
        # 1. Overall Performance Heatmap
        plt.subplot(3, 4, 1)
        metrics_cols = ['consistency', 'relevancy', 'accuracy', 'rouge1_f1', 'rouge2_f1', 'rougeL_f1', 'bert_avg_f1']
        heatmap_data = df.groupby('summary_type')[metrics_cols].mean()
        sns.heatmap(heatmap_data.T, annot=True, cmap='YlOrRd', fmt='.3f', cbar_kws={'shrink': 0.8})
        plt.title('Performance Heatmap by Summary Type', fontsize=12, fontweight='bold')
        plt.ylabel('Metrics')
        
        # 2. ROUGE Scores Comparison
        plt.subplot(3, 4, 2)
        rouge_metrics = ['rouge1_f1', 'rouge2_f1', 'rougeL_f1']
        rouge_data = df.groupby('summary_type')[rouge_metrics].mean()
        rouge_data.plot(kind='bar', ax=plt.gca())
        plt.title('ROUGE Scores by Summary Type', fontsize=12, fontweight='bold')
        plt.ylabel('F1 Score')
        plt.xticks(rotation=45)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 3. BERTScore Comparison  
        plt.subplot(3, 4, 3)
        bert_metrics = ['bert_avg_precision', 'bert_avg_recall', 'bert_avg_f1']
        bert_data = df.groupby('summary_type')[bert_metrics].mean()
        bert_data.plot(kind='bar', ax=plt.gca(), color=['skyblue', 'lightcoral', 'lightgreen'])
        plt.title('BERTScore by Summary Type', fontsize=12, fontweight='bold')
        plt.ylabel('Score')
        plt.xticks(rotation=45)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 4. Custom Metrics (Consistency, Relevancy, Accuracy)
        plt.subplot(3, 4, 4)
        custom_metrics = ['consistency', 'relevancy', 'accuracy']
        custom_data = df.groupby('summary_type')[custom_metrics].mean()
        custom_data.plot(kind='bar', ax=plt.gca(), color=['gold', 'mediumpurple', 'tomato'])
        plt.title('Custom Evaluation Metrics', fontsize=12, fontweight='bold')
        plt.ylabel('Score')
        plt.xticks(rotation=45)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 5. Precision vs Recall Scatter
        plt.subplot(3, 4, 5)
        summary_types = df['summary_type'].unique()
        colors = plt.cm.Set1(np.linspace(0, 1, len(summary_types)))
        
        for i, summary_type in enumerate(summary_types):
            subset = df[df['summary_type'] == summary_type]
            plt.scatter(subset['rouge1_recall'], subset['rouge1_precision'], 
                       label=summary_type, alpha=0.7, s=100, color=colors[i])
        plt.xlabel('ROUGE-1 Recall')
        plt.ylabel('ROUGE-1 Precision')
        plt.title('Precision vs Recall (ROUGE-1)', fontsize=12, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 6. Overall Performance Ranking
        plt.subplot(3, 4, 6)
        df['overall_score'] = (0.25 * df['consistency'] + 0.25 * df['relevancy'] + 
                              0.25 * df['accuracy'] + 0.25 * df['bert_avg_f1'])
        
        overall_ranking = df.groupby('summary_type')['overall_score'].mean().sort_values(ascending=False)
        bars = plt.bar(range(len(overall_ranking)), overall_ranking.values, 
                      color=plt.cm.viridis(np.linspace(0, 1, len(overall_ranking))))
        plt.title('Overall Performance Ranking', fontsize=12, fontweight='bold')
        plt.xlabel('Summary Type')
        plt.ylabel('Overall Score')
        plt.xticks(range(len(overall_ranking)), overall_ranking.index, rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, overall_ranking.values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                    f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # 7. Distribution of Scores
        plt.subplot(3, 4, 7)
        df.boxplot(column='accuracy', by='summary_type', ax=plt.gca())
        plt.title('Accuracy Score Distribution', fontsize=12, fontweight='bold')
        plt.suptitle('')  # Remove default title
        plt.ylabel('Accuracy Score')
        
        # 8. Correlation Matrix
        plt.subplot(3, 4, 8)
        correlation_cols = ['consistency', 'relevancy', 'accuracy', 'rouge1_f1', 'rouge2_f1', 'rougeL_f1', 'bert_avg_f1']
        correlation_matrix = df[correlation_cols].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f', cbar_kws={'shrink': 0.8})
        plt.title('Metrics Correlation Matrix', fontsize=12, fontweight='bold')
        
        # 9. BERTScore Model Comparison
        plt.subplot(3, 4, 9)
        bert_comparison = df[['summary_type', 'bert_f1_deberta', 'bert_f1_roberta']].groupby('summary_type').mean()
        bert_comparison.plot(kind='bar', ax=plt.gca())
        plt.title('BERTScore: DeBERTa vs RoBERTa', fontsize=12, fontweight='bold')
        plt.ylabel('F1 Score')
        plt.xticks(rotation=45)
        plt.legend(['DeBERTa', 'RoBERTa'])
        
        # 10. Performance Trends (if multiple documents)
        plt.subplot(3, 4, 10)
        if len(df['document_id'].unique()) > 1:
            trend_data = df.groupby(['document_id', 'summary_type'])['accuracy'].mean().unstack(fill_value=0)
            trend_data.plot(ax=plt.gca(), marker='o')
            plt.title('Accuracy Trends Across Documents', fontsize=12, fontweight='bold')
            plt.xlabel('Document ID')
            plt.ylabel('Accuracy')
            plt.xticks(rotation=45)
            plt.legend(title='Summary Type', bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            # Show score breakdown instead
            score_breakdown = df.groupby('summary_type')[['rouge1_f1', 'rouge2_f1', 'bert_avg_f1']].mean()
            score_breakdown.plot(kind='area', ax=plt.gca(), alpha=0.7)
            plt.title('Score Composition by Type', fontsize=12, fontweight='bold')
            plt.ylabel('Score')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 11. Summary Statistics Table
        plt.subplot(3, 4, 11)
        plt.axis('off')
        summary_stats = df.groupby('summary_type')[['consistency', 'relevancy', 'accuracy', 'rouge1_f1', 'bert_avg_f1']].mean().round(3)
        
        # Create table
        table_data = []
        for summary_type in summary_stats.index:
            row = [summary_type]
            for col in summary_stats.columns:
                row.append(f"{summary_stats.loc[summary_type, col]:.3f}")
            table_data.append(row)
        
        table = plt.table(cellText=table_data,
                         colLabels=['Type', 'Consistency', 'Relevancy', 'Accuracy', 'ROUGE-1', 'BERTScore'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.5)
        plt.title('Performance Summary (Mean Scores)', fontsize=12, fontweight='bold', pad=20)
        
        # 12. Best vs Worst Comparison
        plt.subplot(3, 4, 12)
        best_type = overall_ranking.index[0]
        worst_type = overall_ranking.index[-1] if len(overall_ranking) > 1 else best_type
        
        if best_type != worst_type:
            comparison_data = df[df['summary_type'].isin([best_type, worst_type])]
            comparison_means = comparison_data.groupby('summary_type')[['consistency', 'relevancy', 'accuracy']].mean()
            comparison_means.plot(kind='bar', ax=plt.gca())
            plt.title(f'Best vs Worst Performance\n({best_type} vs {worst_type})', fontsize=12, fontweight='bold')
            plt.ylabel('Score')
            plt.xticks(rotation=45)
            plt.legend()
        else:
            # Single type - show metric breakdown
            single_type_data = df[df['summary_type'] == best_type][['consistency', 'relevancy', 'accuracy']].mean()
            single_type_data.plot(kind='bar', ax=plt.gca(), color='skyblue')
            plt.title(f'Metric Breakdown: {best_type}', fontsize=12, fontweight='bold')
            plt.ylabel('Score')
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Visualization saved to {save_path}")
            
        plt.show()
    
    def generate_detailed_report(self):
        """
        Generate detailed evaluation report
        """
        if not self.evaluation_results:
            print("No evaluation results available.")
            return None
            
        df = self.get_results_dataframe()
        
        print("="*80)
        print("COMPREHENSIVE SUMMARY EVALUATION REPORT")
        print("="*80)
        
        # Timestamp
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total summaries evaluated: {len(df)}")
        print(f"Summary types: {', '.join(df['summary_type'].unique())}")
        print()
        
        # Overall Statistics
        print("OVERALL STATISTICS")
        print("-"*50)
        overall_stats = df[['consistency', 'relevancy', 'accuracy', 'rouge1_f1', 'rouge2_f1', 'rougeL_f1', 'bert_avg_f1']].describe()
        print(overall_stats.round(4))
        print()
        
        # Performance by Summary Type
        print("PERFORMANCE BY SUMMARY TYPE")
        print("-"*50)
        type_performance = df.groupby('summary_type')[['consistency', 'relevancy', 'accuracy', 'rouge1_f1', 'bert_avg_f1']].mean()
        print(type_performance.round(4))
        print()
        
        # Best Performing Summary Type
        print("BEST PERFORMING SUMMARY TYPE")
        print("-"*50)
        df['overall_score'] = (0.25 * df['consistency'] + 0.25 * df['relevancy'] + 
                              0.25 * df['accuracy'] + 0.25 * df['bert_avg_f1'])
        best_type = df.groupby('summary_type')['overall_score'].mean().idxmax()
        best_score = df.groupby('summary_type')['overall_score'].mean().max()
        
        print(f"Best Summary Type: {best_type}")
        print(f"Overall Score: {best_score:.4f}")
        
        # Detailed Metrics Breakdown
        print(f"\nDetailed metrics for '{best_type.upper()}':")
        print("-"*30)
        best_metrics = df[df['summary_type'] == best_type][['consistency', 'relevancy', 'accuracy', 'rouge1_f1', 'rouge2_f1', 'rougeL_f1', 'bert_avg_f1']].mean()
        
        for metric, value in best_metrics.items():
            print(f"{metric.replace('_', ' ').title()}: {value:.4f}")
        
        # Recommendations
        print(f"\nRECOMMENDATIONS")
        print("-"*50)
        
        type_scores = df.groupby('summary_type')[['consistency', 'relevancy', 'accuracy', 'rouge1_f1', 'bert_avg_f1']].mean()
        
        for summary_type in type_scores.index:
            print(f"\n{summary_type.upper()} Summary:")
            scores = type_scores.loc[summary_type]
            
            # Find strengths and weaknesses
            strengths = scores.nlargest(2).index.tolist()
            weaknesses = scores.nsmallest(2).index.tolist()
            
            print(f"  Strengths: {', '.join([s.replace('_', ' ').title() for s in strengths])}")
            print(f"  Areas for improvement: {', '.join([w.replace('_', ' ').title() for w in weaknesses])}")
        
        print(f"\nOverall recommendation: Focus on improving '{best_type}' approach")
        print("as it shows the best performance across all metrics.")
        
        return df


def demo_evaluation():
    """
    Demonstration of the evaluation system
    """
    print("Starting demonstration of summary evaluation system...")
    
    # Create test directories
    os.makedirs('test', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    
    # Sample data for testing
    sample_summaries = [
        {
            'document_id': 'medical_doc_1',
            'summary_type': 'brief',
            'generated_summary': 'Patient has iron deficiency anaemia and beta thalassaemia trait. Blood tests show microcytic anaemia. Treatment includes iron supplementation.',
            'reference_summary': 'The patient was diagnosed with iron deficiency anaemia and beta thalassaemia trait based on blood test results showing microcytic anaemia. The treatment plan includes iron supplementation and follow-up monitoring.'
        },
        {
            'document_id': 'medical_doc_1', 
            'summary_type': 'detailed',
            'generated_summary': 'Patient K B Chunchaiah, age 45, was admitted with iron deficiency anaemia and beta thalassaemia trait. Laboratory results revealed microcytic anaemia with elevated Mentzer index. The patient presented with symptoms of fatigue and pallor. Current treatment includes ferrous sulfate 200mg daily with planned follow-up in 2 months to monitor hemoglobin levels.',
            'reference_summary': 'Patient K B Chunchaiah, 45 years old, was admitted to hospital with iron deficiency anaemia and beta thalassaemia trait. Blood tests showed microcytic anaemia with elevated Mentzer index. The patient has a history of fatigue and pallor. Current medications include Ferrous Sulfate 200mg daily. Treatment plan includes continuing iron supplementation and follow-up in 2 months with hemoglobin monitoring.'
        },
        {
            'document_id': 'medical_doc_1',
            'summary_type': 'domain_specific', 
            'generated_summary': 'Medical diagnosis: Iron deficiency anaemia with beta thalassaemia trait. Key findings: Microcytic anaemia, elevated Mentzer index (>13), symptoms of fatigue and pallor. Treatment protocol: Ferrous sulfate supplementation with 2-month follow-up schedule. Diagnostic note: HbA2 estimation remains gold standard for beta thalassaemia trait diagnosis.',
            'reference_summary': 'Primary diagnosis of iron deficiency anaemia complicated by beta thalassaemia trait in 45-year-old male patient. Laboratory findings include microcytic anaemia with Mentzer index >13. Clinical presentation includes fatigue and pallor. Treatment regimen consists of ferrous sulfate 200mg daily with scheduled follow-up in 2 months for hemoglobin monitoring. Note that HbA2 estimation is the gold standard for diagnosing beta thalassaemia trait.'
        }
    ]
    
    # Initialize evaluator
    evaluator = SummaryEvaluator()
    
    print(f"Starting evaluation process...")
    
    # Evaluate summaries
    results = evaluator.evaluate_multiple_summaries(sample_summaries)
    
    print(f"Evaluated {len(results)} summaries")
    
    # Generate visualizations
    print("Creating comprehensive visualizations...")
    evaluator.create_comprehensive_visualization(save_path='test/summary_evaluation_dashboard.png')
    
    # Generate detailed report
    print("Generating detailed report...")
    df_results = evaluator.generate_detailed_report()
    
    # Save results to CSV
    df_results.to_csv('test/evaluation_results.csv', index=False)
    print("Results saved to test/evaluation_results.csv")
    
    return evaluator, df_results


if __name__ == "__main__":
    # Run the demonstration
    print("Running Summary Evaluation System Demo...")
    print("="*60)
    
    try:
        evaluator, results_df = demo_evaluation()
        
        print("\n" + "="*60)
        print("EVALUATION SYSTEM DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("Files created:")
        print("  test/summary_evaluation_dashboard.png")
        print("  test/evaluation_results.csv")
        print()
        print("The evaluation system is ready for use!")
        print("You can now use:")
        print("  evaluator.evaluate_summary() - for single summaries")
        print("  evaluator.evaluate_multiple_summaries() - for batch evaluation")
        print("  evaluator.create_comprehensive_visualization() - for charts")
        print("  evaluator.generate_detailed_report() - for detailed analysis")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()
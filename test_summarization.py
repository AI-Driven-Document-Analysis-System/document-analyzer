#!/usr/bin/env python3
"""
Test script for the summarization service
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.summarization_service import summarize_with_options, get_summary_options

def test_summarization():
    """Test the summarization service with sample text"""
    
    # Sample text for testing
    sample_text = """
    Artificial intelligence has revolutionized many industries in recent years. 
    Machine learning algorithms can now process vast amounts of data to identify 
    patterns and make predictions. This technology is being used in healthcare 
    to diagnose diseases, in finance to detect fraud, and in transportation 
    to develop autonomous vehicles. However, there are also concerns about job 
    displacement and privacy issues that need to be addressed as AI continues to evolve.
    
    The development of AI has been driven by advances in computing power, 
    the availability of large datasets, and improvements in algorithms. 
    Deep learning, a subset of machine learning, has been particularly 
    successful in areas like computer vision, natural language processing, 
    and speech recognition. These advances have led to the creation of 
    systems that can perform tasks that were previously thought to be 
    impossible for machines.
    """
    
    print("Testing Summarization Service")
    print("=" * 50)
    
    # Get available options
    options = get_summary_options()
    print(f"Available summary options: {list(options.keys())}")
    
    # Test each option
    for option_id, option_config in options.items():
        print(f"\nTesting {option_id} summary...")
        try:
            summary = summarize_with_options(sample_text, option_config)
            print(f"✅ Success! Generated {len(summary.split())} words")
            print(f"Summary: {summary[:200]}...")
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_summarization()

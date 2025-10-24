#!/usr/bin/env python3
"""
Simple test runner script for ChromaDB tests
Run this file to execute all ChromaDB tests
"""

import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and run the main test runner
from test_runner import main

if __name__ == "__main__":
    print("Starting ChromaDB Test Suite...")
    print("=" * 60)
    main()

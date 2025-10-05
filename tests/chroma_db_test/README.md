# ChromaDB Test Suite

This directory contains comprehensive tests for ChromaDB functionality in the Document Analyzer system.

## Test Files

- `test_runner.py` - Main test runner that executes all tests
- `base_test.py` - Base class for all ChromaDB tests
- `metadata_filtering_test.py` - Tests document filtering by metadata
- `performance_test.py` - Tests insertion and query performance
- `concurrent_access_test.py` - Tests multiple simultaneous operations
- `corruption_recovery_test.py` - Tests system behavior with corrupted data
- `embedding_consistency_test.py` - Tests embedding determinism and consistency
- `integration_test.py` - Tests integration with other system components
- `run_tests.py` - Simple script to run all tests

## How to Run Tests

### Run All Tests
```bash
cd C:\Users\sahan\OneDrive\Desktop\document-analyzer\tests\chroma_db_test
python run_tests.py
```

### Run Individual Tests
```bash
python -c "from metadata_filtering_test import MetadataFilteringTest; MetadataFilteringTest().run()"
python -c "from performance_test import PerformanceTest; PerformanceTest().run()"
python -c "from concurrent_access_test import ConcurrentAccessTest; ConcurrentAccessTest().run()"
python -c "from corruption_recovery_test import CorruptionRecoveryTest; CorruptionRecoveryTest().run()"
python -c "from embedding_consistency_test import EmbeddingConsistencyTest; EmbeddingConsistencyTest().run()"
python -c "from integration_test import IntegrationTest; IntegrationTest().run()"
```

## Test Coverage

### 1. Metadata Filtering Test
- Tests filtering by single document ID
- Tests filtering by multiple document IDs
- Measures performance penalty of filtering
- Validates non-existent document ID handling

### 2. Performance Test
- Tests insertion performance at different scales (100, 500, 1000 docs)
- Measures query performance with various queries
- Monitors memory usage scaling
- Validates performance criteria (>100 docs/min insertion, <100ms queries)

### 3. Concurrent Access Test
- Tests multiple simultaneous read operations
- Tests multiple simultaneous write operations
- Tests mixed read/write operations
- Validates thread safety and data consistency

### 4. Corruption Recovery Test
- Tests behavior when database files are deleted
- Tests behavior when database files are corrupted
- Tests partial corruption scenarios (permission issues)
- Validates graceful error handling and recovery

### 5. Embedding Consistency Test
- Tests deterministic embedding generation
- Tests query result consistency across multiple runs
- Tests consistency after system restart
- Validates embedding stability

### 6. Integration Test
- Tests memory usage scaling with document count
- Tests handling of large documents
- Tests metadata validation with various data types
- Tests collection management and persistence

## Expected Results

All tests should PASS for a healthy ChromaDB installation. Common failure scenarios:

- **Metadata Filtering Failures**: Usually indicate issues with document_id field storage
- **Performance Failures**: May indicate system resource constraints or inefficient queries
- **Concurrent Access Failures**: Could indicate thread safety issues or file locking problems
- **Corruption Recovery Failures**: May indicate insufficient error handling in the application
- **Embedding Consistency Failures**: Could indicate non-deterministic behavior in the embedding model
- **Integration Failures**: May indicate memory leaks or metadata handling issues

## Performance Benchmarks

- Insertion Rate: > 100 documents/minute
- Query Time: < 100ms average
- Memory Usage: Linear scaling with document count
- Concurrent Operations: No failures with 5+ simultaneous operations
- Filter Performance: < 50ms penalty compared to unfiltered queries

## Troubleshooting

If tests fail:

1. Check that all dependencies are installed (langchain, chromadb, sentence-transformers)
2. Ensure sufficient disk space for temporary test databases
3. Verify no other processes are using ChromaDB files
4. Check system resources (memory, CPU) during test execution
5. Review test output for specific error messages

## Test Environment

Tests create temporary databases in system temp directories and clean up automatically. No permanent changes are made to your production ChromaDB instance.

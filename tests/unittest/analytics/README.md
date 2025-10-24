# Analytics Unit Tests

Comprehensive unit tests for analytics API endpoints using pytest.

## Test Coverage

### Analytics API Tests (`test_analytics_api.py`)
- **Document Uploads Over Time**: Test upload statistics for different periods (7d, 30d, 90d, 1y)
- **Document Types Distribution**: Test document type classification statistics
- **Upload Trends**: Test upload patterns by day of week and hour of day
- **Storage Usage**: Test storage quota and usage calculations
- **Model Usage**: Test summarization model usage statistics
- **OCR Confidence**: Test OCR confidence score distribution and binning
- **Chat Distribution**: Test chat conversation statistics by day
- **Error Handling**: Test database errors and invalid inputs
- **Period Validation**: Test different time period groupings
- **Edge Cases**: Empty data, null values, invalid users

## Test Statistics

- **Total Tests**: 30+
- **Test Categories**:
  - Document analytics: 8 tests
  - Distribution analytics: 5 tests
  - Trends analytics: 4 tests
  - Storage analytics: 3 tests
  - Model usage: 3 tests
  - OCR analytics: 4 tests
  - Chat analytics: 3 tests

## Running the Tests

### Run all analytics tests:
```bash
pytest tests/unittest/analytics/ -v
```

### Run specific test:
```bash
pytest tests/unittest/analytics/test_analytics_api.py::TestAnalyticsAPI::test_get_document_uploads_over_time_7d -v
```

### Run with coverage:
```bash
pytest tests/unittest/analytics/ --cov=app.api.analytics --cov-report=html
```

### Run async tests:
```bash
pytest tests/unittest/analytics/ -v --asyncio-mode=auto
```

## Test Structure

```
tests/unittest/analytics/
├── __init__.py
├── conftest.py                     # Shared fixtures
├── README.md                       # This file
└── test_analytics_api.py          # 30+ tests
```

## API Endpoints Tested

### 1. Document Uploads Over Time
**Endpoint**: `GET /analytics/document-uploads-over-time`
- Parameters: period (7d, 30d, 90d, 1y)
- Returns: Chart data and summary statistics
- Tests: Different periods, date grouping, summary calculations

### 2. Document Types Distribution
**Endpoint**: `GET /analytics/document-types-distribution`
- Returns: Count and average size per document type
- Tests: Multiple types, unknown types, empty data

### 3. Upload Trends
**Endpoint**: `GET /analytics/upload-trends`
- Returns: Uploads by day of week and hour of day
- Tests: Pattern detection, timezone handling

### 4. Storage Usage
**Endpoint**: `GET /analytics/storage-usage`
- Returns: Total, used, available storage and percentage
- Tests: Calculations, empty storage, percentage accuracy

### 5. Model Usage Over Time
**Endpoint**: `GET /analytics/model-usage-over-time`
- Parameters: period (7d, 30d, 90d, 1y)
- Returns: Usage statistics per model
- Tests: Model mapping, time series data

### 6. OCR Confidence Distribution
**Endpoint**: `GET /analytics/ocr-confidence-distribution`
- Returns: Confidence scores and distribution bins
- Tests: Binning logic, statistics, empty data

### 7. Chat Distribution by Day
**Endpoint**: `GET /analytics/chat-distribution-by-day`
- Returns: Chat counts per day for current month
- Tests: Daily aggregation, statistics

## Key Features Tested

### Time Period Handling
- **7d**: Daily grouping
- **30d**: Daily grouping
- **90d**: Weekly grouping
- **1y**: Monthly grouping

### Timezone Support
- All timestamps converted to Asia/Colombo timezone
- Proper date truncation for grouping

### Statistical Calculations
- Averages, min, max values
- Percentages and ratios
- Distribution binning
- Trend analysis

### Data Aggregation
- GROUP BY operations
- Date truncation
- COUNT, SUM, AVG functions
- Time-based filtering

## Fixtures

### Mock Data Fixtures
- `mock_upload_data`: Sample upload statistics
- `mock_document_types`: Document type distribution
- `mock_ocr_scores`: OCR confidence scores
- `mock_model_usage`: Model usage time series
- `mock_chat_distribution`: Chat activity data
- `mock_upload_trends`: Upload pattern data

### Configuration Fixtures
- `storage_limits`: Storage quota configuration
- `mock_user`: Authenticated user object
- `mock_db_connection`: Database connection mock

## OCR Confidence Bins

```python
{
    'low': < 0.5,           # Poor quality
    'medium': 0.5 - 0.7,    # Acceptable
    'good': 0.7 - 0.85,     # Good quality
    'very_good': 0.85 - 0.95, # Very good
    'excellent': >= 0.95    # Excellent quality
}
```

## Storage Limits

- **Total Storage**: 300MB per user
- **Warning Threshold**: 80% (240MB)
- **Critical Threshold**: 95% (285MB)

## Test Scenarios

### Success Cases
- ✅ Valid period parameters
- ✅ Multiple document types
- ✅ Various confidence scores
- ✅ Different time ranges
- ✅ Complete data sets

### Error Cases
- ✅ Invalid period parameter
- ✅ Invalid user token
- ✅ Database connection errors
- ✅ Query execution failures

### Edge Cases
- ✅ Empty data sets
- ✅ Null values in database
- ✅ Single data point
- ✅ Unknown document types
- ✅ Zero storage usage

## Dependencies

```
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-asyncio>=0.21.0
fastapi>=0.100.0
```

## Async Testing

All analytics endpoints are async:
```python
@pytest.mark.asyncio
async def test_get_document_uploads_over_time_7d():
    result = await get_document_uploads_over_time(
        period="7d",
        current_user=mock_user
    )
    assert "chartData" in result
```

## Database Mocking

Tests mock database connections:
```python
@patch('app.api.analytics.db_manager.get_connection')
async def test_endpoint(mock_get_conn, mock_user):
    conn, cursor = mock_db_connection
    mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
    cursor.fetchall.return_value = [...]
```

## Best Practices

1. **Mock Database**: All database calls are mocked
2. **Test All Periods**: Test 7d, 30d, 90d, 1y periods
3. **Validate Calculations**: Check percentages, averages, totals
4. **Test Edge Cases**: Empty data, null values
5. **Error Handling**: Test all error scenarios
6. **Async Support**: Use pytest-asyncio

## CI/CD Integration

These tests are designed for continuous integration:
- No database required (all mocked)
- Fast execution (< 5 seconds)
- Async test support
- Clear pass/fail indicators
- Coverage reporting

## Performance

- Single test: < 0.1 seconds
- Full suite: < 3 seconds
- With coverage: < 5 seconds

## Data Validation

Tests verify:
- Response structure
- Data types
- Value ranges
- Calculation accuracy
- Date formatting
- Timezone handling

## Future Enhancements

- [ ] Test real-time analytics
- [ ] Test data export functionality
- [ ] Test custom date ranges
- [ ] Test analytics caching
- [ ] Performance benchmarks
- [ ] Integration tests with real database

## Troubleshooting

### Common Issues

**Issue**: Async tests not running
**Solution**: Install pytest-asyncio: `pip install pytest-asyncio`

**Issue**: Mock not working
**Solution**: Ensure correct patch path: `app.api.analytics.db_manager`

**Issue**: Date formatting errors
**Solution**: Mock datetime objects properly with `.date()` method

## Contributing

When adding new analytics endpoints:
1. Write tests first (TDD)
2. Mock database connections
3. Test all time periods
4. Test error scenarios
5. Ensure >80% code coverage
6. Update this README

## Example Test

```python
@pytest.mark.asyncio
@patch('app.api.analytics.db_manager.get_connection')
async def test_get_document_uploads_over_time_7d(
    mock_get_conn, mock_user, mock_db_connection
):
    conn, cursor = mock_db_connection
    mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
    
    cursor.fetchall.side_effect = [
        [(datetime.now().date(), 5, 1024000)],
        [(10, 5120000, 512000, datetime.now(), datetime.now())]
    ]
    
    result = await get_document_uploads_over_time(
        period="7d",
        current_user=mock_user
    )
    
    assert "chartData" in result
    assert result["period"] == "7d"
    assert result["summary"]["totalDocuments"] == 10
```

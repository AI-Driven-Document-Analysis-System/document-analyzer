# Dynamic Summarization System

This document describes the implementation of a dynamic summarization system that fetches summaries from the database when available or generates new ones when needed.

## Overview

The system replaces the hardcoded summarization logic with a dynamic backend-driven approach that:

1. **Checks for existing summaries** in the database first
2. **Generates new summaries** only when needed using AI models
3. **Caches results** for future use
4. **Supports multiple models** (BART, Pegasus, T5) for different summary types

## Architecture

### Backend Components

#### 1. Summarization Service (`app/services/summarization_service.py`)
- **Model Management**: Handles BART, Pegasus, and T5 models
- **Text Processing**: Chunks long documents appropriately for each model
- **Error Handling**: Includes fallback mechanisms and robust error handling
- **Model Selection**: Automatically selects the best model for each summary type

#### 2. Summarization API (`app/api/summarization.py`)
- **Caching Logic**: Checks database for existing summaries before generation
- **Model Resolution**: Maps summary types to appropriate AI models
- **Database Integration**: Stores and retrieves summaries from PostgreSQL
- **User Authentication**: Ensures users can only access their own documents

#### 3. Database Schema
```sql
CREATE TABLE document_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    summary_text TEXT NOT NULL,
    key_points JSONB,
    model_version VARCHAR(20),
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Frontend Components

#### 1. SummaryModal (`frontend/src/components/summarization/SummaryModal.tsx`)
- **Dynamic Loading**: Fetches available summary options from backend
- **Caching Display**: Shows when summaries are retrieved from cache
- **Model Selection**: Allows users to choose between different summary types
- **Real-time Updates**: Displays generation progress and results

#### 2. Dashboard Integration (`frontend/src/components/dashboard/dashboard_merged.tsx`)
- **Seamless Integration**: Maintains existing UI/UX while adding dynamic functionality
- **Modal Integration**: Properly integrated SummaryModal component
- **Error Handling**: Graceful fallbacks when API calls fail

#### 3. API Service (`frontend/src/services/api.ts`)
- **Centralized API Calls**: All summarization requests go through this service
- **Error Handling**: Consistent error handling across all API calls
- **Type Safety**: TypeScript interfaces for all API responses

## Summary Types

### 1. Brief Summary (BART)
- **Model**: Facebook BART Large CNN
- **Length**: 50-150 words
- **Best For**: Quick overviews, executive summaries
- **Characteristics**: Concise, focused on key points

### 2. Detailed Summary (Pegasus)
- **Model**: Google Pegasus CNN DailyMail
- **Length**: 80-250 words
- **Best For**: Comprehensive analysis, detailed insights
- **Characteristics**: Thorough, context-rich summaries

### 3. Domain-Specific Summary (T5)
- **Model**: T5 Base (with domain-specific tuning)
- **Length**: 70-200 words
- **Best For**: Specialized content (medical, legal, financial)
- **Characteristics**: Adapts to document type and domain

## API Endpoints

### POST `/api/summarize/`
Generate a new summary or retrieve existing one.

**Request:**
```json
{
  "document_id": "uuid",
  "summary_type": "brief|detailed|domain_specific"
}
```

**Response:**
```json
{
  "success": true,
  "document_id": "uuid",
  "document_name": "filename.pdf",
  "summary_text": "Generated summary...",
  "word_count": 125,
  "model_used": "bart",
  "summary_type": "Brief Summary",
  "document_type": "financial",
  "created_at": "2024-01-01T00:00:00Z",
  "from_cache": false
}
```

### GET `/api/summarize/options`
Get available summary options and configurations.

### GET `/api/summarize/document/{document_id}`
Get all existing summaries for a specific document.

### GET `/api/summarize/document-types`
Get supported document types for domain-specific summaries.

## Caching Strategy

### 1. Database-Level Caching
- **Persistent Storage**: Summaries are stored in PostgreSQL
- **Model-Specific**: Each document can have multiple summaries (one per model)
- **Automatic Retrieval**: API checks for existing summaries before generation

### 2. Frontend Caching
- **Local State**: SummaryModal maintains local state of loaded summaries
- **Immediate Display**: Cached summaries are displayed instantly
- **Background Refresh**: New summaries are fetched only when needed

### 3. Cache Invalidation
- **Model-Based**: Each model type has its own cache entry
- **Document-Specific**: Caching is per-document and per-model
- **Manual Regeneration**: Users can force new summary generation

## Error Handling

### 1. Model Loading Failures
- **Fallback Models**: Automatically falls back to BART if other models fail
- **Graceful Degradation**: Continues operation with available models
- **User Notification**: Clear error messages for failed operations

### 2. API Failures
- **Retry Logic**: Automatic retries for transient failures
- **Offline Support**: Frontend gracefully handles API unavailability
- **User Feedback**: Loading states and error messages

### 3. Database Issues
- **Connection Pooling**: Robust database connection management
- **Transaction Safety**: Proper rollback on database errors
- **Logging**: Comprehensive logging for debugging

## Performance Optimizations

### 1. Model Loading
- **Lazy Loading**: Models are loaded only when needed
- **Connection Pooling**: Database connections are reused efficiently
- **Async Processing**: Non-blocking summary generation

### 2. Text Processing
- **Smart Chunking**: Documents are split optimally for each model
- **Length Optimization**: Summary lengths are tuned for each model type
- **Memory Management**: Large documents are processed in chunks

### 3. Caching Benefits
- **Instant Retrieval**: Cached summaries load immediately
- **Reduced API Calls**: Fewer requests to AI models
- **Cost Optimization**: Minimizes AI model usage costs

## Usage Examples

### 1. Generate Brief Summary
```typescript
const summary = await apiService.generateSummary(documentId, 'brief');
```

### 2. Check for Existing Summaries
```typescript
const summaries = await apiService.getDocumentSummaries(documentId);
```

### 3. Get Available Options
```typescript
const options = await apiService.getSummaryOptions();
```

## Installation and Setup

### 1. Backend Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Ensure PostgreSQL is running
# Run database initialization
python -m app.db.init_db
```

### 3. Environment Variables
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### 4. Frontend Dependencies
```bash
cd frontend
npm install
```

## Testing

### 1. Backend Testing
```bash
python test_summarization.py
```

### 2. API Testing
```bash
# Start the backend
uvicorn app.main:app --reload

# Test endpoints
curl -X POST "http://localhost:8000/api/summarize/" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "test", "summary_type": "brief"}'
```

### 3. Frontend Testing
```bash
cd frontend
npm run dev
```

## Troubleshooting

### Common Issues

1. **Model Loading Failures**
   - Check if transformers library is installed
   - Verify internet connection for model downloads
   - Check available disk space

2. **Database Connection Issues**
   - Verify DATABASE_URL environment variable
   - Check PostgreSQL service status
   - Verify database permissions

3. **Frontend Integration Issues**
   - Check browser console for errors
   - Verify API endpoint URLs
   - Check authentication token validity

### Debug Mode

Enable debug logging by setting:
```bash
export LOG_LEVEL=DEBUG
```

## Future Enhancements

1. **Advanced Caching**: Redis integration for faster cache access
2. **Model Fine-tuning**: Custom models for specific document types
3. **Batch Processing**: Generate summaries for multiple documents
4. **Quality Metrics**: Automatic summary quality assessment
5. **User Preferences**: Personalized summary styles and lengths

## Contributing

1. Follow the existing code style
2. Add tests for new functionality
3. Update documentation for API changes
4. Ensure backward compatibility
5. Test with multiple document types and sizes

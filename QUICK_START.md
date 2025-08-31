# Quick Start Guide - Dynamic Summarization System

Get the new summarization system up and running in 5 minutes!

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Set Up Environment
```bash
# Run the setup script
python setup_summarization.py

# Or manually create .env file
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Start the System
```bash
# Terminal 1: Start backend
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### 4. Test the System
```bash
# Test backend summarization
python test_summarization.py

# Open frontend in browser
# Navigate to http://localhost:3000
# Upload a document and try the summarize feature
```

## 🔧 What's New

### ✅ Dynamic Summarization
- **No more hardcoded summaries!**
- Automatically fetches existing summaries from database
- Generates new summaries only when needed
- Caches results for instant access

### ✅ Multiple AI Models
- **BART**: Best for brief, concise summaries
- **Pegasus**: Best for detailed, comprehensive summaries  
- **T5**: Best for domain-specific summaries

### ✅ Smart Caching
- Database-level caching for persistence
- Frontend caching for instant display
- Model-specific caching (each model has its own cache)

### ✅ Better UX
- Loading states and progress indicators
- Error handling with fallback options
- Cache status indicators
- Summary history view

## 📱 How to Use

### 1. Upload a Document
- Go to the dashboard
- Click "Upload Document"
- Wait for processing to complete

### 2. Generate Summary
- Click "Summarize" on any document
- Choose summary type (Brief, Detailed, Domain-Specific)
- View results instantly if cached, or wait for generation

### 3. View Summary History
- All generated summaries are saved
- Switch between different summary types
- Regenerate summaries if needed

## 🐛 Troubleshooting

### Common Issues

**"Model loading failed"**
```bash
# Check if transformers is installed
pip install transformers torch

# Check internet connection for model downloads
```

**"Database connection failed"**
```bash
# Check .env file
cat .env

# Verify PostgreSQL is running
sudo systemctl status postgresql
```

**"Frontend not loading"**
```bash
# Check if dependencies are installed
cd frontend
npm install

# Check for build errors
npm run build
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Start backend with debug
uvicorn app.main:app --reload --log-level debug
```

## 📚 API Endpoints

### Generate Summary
```bash
curl -X POST "http://localhost:8000/api/summarize/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"document_id": "uuid", "summary_type": "brief"}'
```

### Get Summary Options
```bash
curl "http://localhost:8000/api/summarize/options"
```

### Get Document Summaries
```bash
curl "http://localhost:8000/api/summarize/document/UUID"
```

## 🎯 Next Steps

1. **Customize Models**: Modify `app/services/summarization_service.py`
2. **Add New Summary Types**: Update the summary options
3. **Optimize Performance**: Add Redis caching
4. **Extend Frontend**: Add more summary visualization options

## 📖 Full Documentation

For complete details, see:
- `SUMMARIZATION_README.md` - Comprehensive system documentation
- `app/api/summarization.py` - API implementation details
- `frontend/src/components/summarization/SummaryModal.tsx` - Frontend component

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the logs in the `logs/` directory
3. Check the browser console for frontend errors
4. Verify all environment variables are set correctly

## 🎉 Success!

Once everything is working:
- ✅ Summaries are generated dynamically
- ✅ Caching works automatically  
- ✅ Multiple AI models are available
- ✅ Frontend displays results instantly
- ✅ Database stores all summaries

You now have a production-ready summarization system! 🚀

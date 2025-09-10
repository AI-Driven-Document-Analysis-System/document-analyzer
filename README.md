
## Project Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
```

### 2. Install Base Dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Install Feature-Specific Dependencies

**For RAG functionality:**
```bash
python -m pip install -e .[rag]
```

**For Summarization:**
```bash
python -m pip install -e .[summarization]
```

**For Classification:**
```bash
python -m pip install -e .[classification]
```

**Install multiple features:**
```bash
python -m pip install -e .[rag,summarization]
```

**Install everything:**
```bash
python -m pip install -e .[all]
```

### 4. Start MinIO Server
```bash
.\minio.exe server ./data --console-address ":9001"
```

**MinIO Access:**
- **API**: http://127.0.0.1:9000 (for application)
- **Web Console**: http://127.0.0.1:9001 (for management)
- **Default Credentials**: minioadmin / minioadmin

### 5. Setup Environment Variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

**Required API Keys:**
- **GEMINI_API_KEY**: Get your Google AI API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **GROQ_API_KEY**: Get your Groq API key from [Groq Console](https://console.groq.com/)

**Example .env configuration:**
```env
# LLM API Keys
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Other settings...
```

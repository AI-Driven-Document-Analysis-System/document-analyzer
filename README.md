
# AI-Driven Document Analysis System

A powerful document analysis platform with AWS Textract OCR, RAG capabilities, and intelligent document processing.

## Project Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv .venv
```

### 2. Activate Virtual Environment
```bash
.venv\Scripts\activate  

```

### 3. Download Required Binaries

**Download MinIO:**
- Download `minio.exe` from [MinIO Downloads](https://min.io/download)
- Place it in the project root directory

**Download Poppler (for PDF processing):**
- Download Poppler from [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases)
- Extract to `poppler/` folder in project root
- Required for AWS Textract PDF conversion

### 4. Install All Dependencies
```bash
pip install -r requirements.txt
```

### 5. Setup Environment Variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

**Required Configuration:**
- **AWS Credentials**: For Textract OCR processing
- **Database**: PostgreSQL connection
- **API Keys**: For LLM services (Gemini, Groq)

**Example .env configuration:**
```env
# AWS Textract Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
OCR_PROVIDER=aws_textract

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# LLM API Keys
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

### 6. Start MinIO Server
```bash
.\minio.exe server ./data --console-address ":9001"
```

**MinIO Access:**
- **API**: http://127.0.0.1:9000 (for application)
- **Web Console**: http://127.0.0.1:9001 (for management)
- **Default Credentials**: minioadmin / minioadmin

### 7. Start the Application

**Backend:**
```bash
python run.py
```

**Alternative (with Auto-Restart):**
```bash
powershell -ExecutionPolicy Bypass .\auto_restart.ps1
```
*Automatically restarts the server if it crashes. Use Ctrl+C to stop permanently.*

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Access the Application:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Features

- **Fast Cloud OCR**: AWS Textract for lightning-fast document processing
- **RAG System**: Intelligent document search and question answering
- **Multi-format Support**: PDFs, images, and various document types
- **Layout Analysis**: Advanced document structure understanding
- **Vector Database**: ChromaDB for semantic search
- **Modern UI**: React-based frontend with real-time processing

## AWS Textract Setup

This application uses AWS Textract for fast, cloud-based OCR processing. To set up:

1. **Create AWS Account** and get credentials
2. **Set up IAM user** with Textract permissions
3. **Add credentials** to your `.env` file
4. **Set OCR_PROVIDER=aws_textract** in environment

**Benefits:**
- **10x faster** than local OCR (seconds vs minutes)
- **Native PDF support** with multi-page processing
- **High accuracy** with layout analysis
- **No local memory issues** - cloud processing

## Architecture

- **Backend**: FastAPI with PostgreSQL database
- **OCR**: AWS Textract (primary) with Surya fallback
- **Storage**: MinIO for document files
- **Vector DB**: ChromaDB for semantic search
- **Frontend**: React with TypeScript

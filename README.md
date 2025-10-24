# AI-Driven Document Analysis System

An AI-driven document analysis system that provides comprehensive document processing and analysis capabilities through advanced machine learning models and intelligent automation. This system enables users to upload documents, extract text through OCR, classify documents automatically, generate summaries, and interact with document content through an intelligent RAG-based chatbot. The platform offers flexible model selection, interactive editing capabilities, and comprehensive analytics dashboards to track document processing activities and insights.

## Architecture
![architecture](https://github.com/user-attachments/assets/6ba17ef9-229b-4268-86a2-14ec8ab63b5e)


## Features

### Core Components

- **OCR (Optical Character Recognition)**: Extract text from documents with high accuracy
- **Classification**: Automatically categorize documents into predefined types
- **RAG Chatbot**: Retrieval-Augmented Generation chatbot for intelligent document Q&A
- **Summarization**: Generate concise summaries from document content

### Features

- **User-Selectable Models for Chatbot**: Choose from multiple LLM models to power your chatbot interactions
- **User-Selectable Models for Summarization**: Select different summarization models based on your needs (Brief, Detailed, Domain-Specific)
- **Interactive OCR Editing**: Edit and refine OCR results directly within the interface
- **Subscription-Based Plans**: Flexible pricing tiers with Stripe payment integration
- **Searchable Dashboards**: Powerful search functionality across all your documents
- **Analytics & Insights**: Comprehensive analytics showing user activities and document insights

## Technologies & Models

- **LLMs**: DeepSeek V3, Llama-3.1-8B-Instant
- **OCR**: Surya OCR
- **Summarization Models**: T5, BART, Pegasus
- **Vector Database**: ChromaDB
- **File Storage**: MinIO
- **Relational Database**: PostgreSQL
- **Payment Service**: Stripe
- **Backend Framework**: FastAPI
- **Frontend Framework**: React, Next.js

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
- Required for PDF processing

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
- **Database**: PostgreSQL connection
- **API Keys**: For LLM services (DeepSeek, Llama)
- **Storage**: MinIO configuration

**Example .env configuration:**
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# LLM API Keys
DEEPSEEK_API_KEY=your_deepseek_api_key_here
LLAMA_API_KEY=your_llama_api_key_here

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

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

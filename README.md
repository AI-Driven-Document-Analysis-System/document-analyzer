
## Project Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
```

### 2. Install Base Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Feature-Specific Dependencies

**For RAG functionality:**
```bash
pip install -e .[rag]
```

**For Summarization:**
```bash
pip install -e .[summarization]
```

**For Classification:**
```bash
pip install -e .[classification]
```

**Install multiple features:**
```bash
pip install -e .[rag,summarization]
```

**Install everything:**
```bash
pip install -e .[all]
```

### 4. Setup Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

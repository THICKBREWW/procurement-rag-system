# 🤝 Procurement Contract Compliance & Generation System

## 🚀 **Quick Start**

### **Web Application (Recommended)**
```bash
# Install dependencies
pip install -r requirements.txt

# Start the Flask API server
python app/api.py

# Open your browser to:
# http://localhost:5000
```

### **🌐 Global Access via Cloudflare Tunnel**
```bash
# Start the Flask API server
python app/api.py

# In another terminal, start Cloudflare tunnel
.\cloudflared tunnel --url http://127.0.0.1:5000

# Access globally via the provided tunnel URL
# Example: https://your-tunnel-url.trycloudflare.com
```

### **Streamlit UI (Alternative)**
```bash
# Start Streamlit interface
streamlit run app/streamlit_app.py
# Open: http://localhost:8501
```

### **Microsoft Office Script Lab Integration**
```bash
# Start the API server
python app/api.py

# Access Script Lab in Microsoft Office:
# 1. Open Word/Excel/PowerPoint
# 2. Go to Insert > Office Add-ins > Script Lab
# 3. Use the provided Script Lab code for Office integration
```

## ✨ **What's New - Latest Updates**

- ✅ **Global Access via Cloudflare Tunnel** - Access your system from anywhere in the world
- ✅ **Fixed API Key Configuration** - Frontend now correctly connects to tunnel
- ✅ **Working Document Upload** - PDF processing and chunking working perfectly
- ✅ **Compliance Check Working** - Full AI-powered compliance analysis
- ✅ **Persistent Storage** - Documents won't be lost on restart
- ✅ **Enhanced Error Handling** - Better user experience

## 🔧 **Configuration**

1. **Set API Key**: Use the web interface or set `ANTHROPIC_API_KEY` environment variable
2. **Upload Policies**: Add your procurement documents for compliance checking
3. **Start Using**: All features work seamlessly with the new fixes

## 📡 **API Endpoints**

- `POST /api/check-compliance` - Check contract compliance
- `POST /api/generate-contract` - Generate new contracts  
- `POST /api/grammar-check` - Fix grammar and spelling
- `POST /api/fix-contract` - Fix contracts with compliance
- `POST /api/suggest-clauses` - Find missing clauses

## 🔧 **Microsoft Office Script Lab Setup**

### **What is Script Lab?**
Script Lab is a Microsoft Office add-in that allows you to run JavaScript code directly within Word, Excel, and PowerPoint. It's perfect for integrating our procurement RAG system with Office documents.

### **Setup Instructions:**

#### **1. Install Script Lab**
1. Open Microsoft Word/Excel/PowerPoint
2. Go to **Insert** > **Office Add-ins**
3. Search for **"Script Lab"**
4. Click **Add** to install

#### **2. Configure Script Lab**
1. Open Script Lab from the **Insert** tab
2. Click **"Code"** in the Script Lab panel
3. Replace the default code with our integration code
4. Set the API server URL to your local server or Cloudflare tunnel

#### **3. Script Lab Integration Code**
```javascript
// Script Lab code for Procurement RAG System
const API_BASE_URL = 'https://oecd-edt-elvis-campbell.trycloudflare.com'; // or http://localhost:5000

async function checkCompliance() {
    try {
        const text = await Office.context.document.getSelectedDataAsync(Office.CoercionType.Text);
        
        const response = await fetch(`${API_BASE_URL}/api/check-compliance`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                text: text.value,
                api_key: 'YOUR_ANTHROPIC_API_KEY' // Set your API key here
            })
        });
        
        const result = await response.text();
        await Office.context.document.setSelectedDataAsync(result);
        
    } catch (error) {
        console.error('Error:', error);
    }
}

async function generateContract() {
    try {
        const requirements = await Office.context.document.getSelectedDataAsync(Office.CoercionType.Text);
        
        const response = await fetch(`${API_BASE_URL}/api/generate-contract`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contract_type: 'service',
                requirements: requirements.value,
                api_key: 'YOUR_ANTHROPIC_API_KEY'
            })
        });
        
        const result = await response.text();
        await Office.context.document.setSelectedDataAsync(result);
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// Add buttons to the Script Lab interface
Office.onReady(() => {
    // This will be called when Script Lab is ready
});
```

#### **4. Usage in Office**
1. **Select text** in your Word document
2. **Run the function** in Script Lab (checkCompliance, generateContract, etc.)
3. **Results will be inserted** into your document automatically

### **Available Script Lab Functions:**
- `checkCompliance()` - Check selected text for compliance
- `generateContract()` - Generate contract from requirements
- `fixGrammar()` - Fix grammar and spelling
- `suggestClauses()` - Find missing contract clauses

### **Benefits of Script Lab Integration:**
- ✅ **Direct Office integration** - No copy-paste needed
- ✅ **Real-time analysis** - Work directly in your documents
- ✅ **Seamless workflow** - Stay in Office environment
- ✅ **Easy to use** - Simple JavaScript functions
- ✅ **Customizable** - Modify code for your needs

## 🌐 **Cloudflare Tunnel Setup (Global Access)**

### **What is Cloudflare Tunnel?**
Cloudflare Tunnel allows you to expose your local development server to the internet without port forwarding or complex networking setup. Perfect for sharing your procurement RAG system globally.

### **Quick Setup:**
```bash
# 1. Install cloudflared
.\install-cloudflared.bat

# 2. Start the tunnel
.\start-tunnel.bat

# 3. Your app will be available at a public URL like:
# https://abc123.trycloudflare.com
```

### **Benefits:**
- ✅ **Global access** - Share with anyone worldwide
- ✅ **HTTPS encryption** - Secure by default
- ✅ **No port forwarding** - Works behind firewalls
- ✅ **Free** - No cost for basic usage
- ✅ **Easy setup** - One command deployment

### **Usage:**
1. **Start your API server:** `python app/api.py`
2. **Start the tunnel:** `.\start-tunnel.bat`
3. **Share the public URL** with others
4. **Use Script Lab** with the public URL for global access

[![Deploy to Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)

An intelligent RAG-based system for procurement contract compliance checking, missing clause detection, and automated contract generation powered by Claude AI and ChromaDB.

## 🌟 Features

- **📚 Policy Ingestion**: Store and index procurement policies, vendor guidelines, and compliance documents
- **🔍 Compliance Checking**: Automatically verify contracts against stored policies
- **💡 Missing Clause Detection**: Identify and suggest missing critical clauses
- **📝 Contract Generation**: Generate complete contracts from input parameters
- **🔄 Full Workflow**: End-to-end contract review and improvement pipeline
- **🎨 Web Interface**: Beautiful Streamlit UI for easy interaction
- **🚀 REST API**: Flask backend for system integration
- **📊 Analytics**: Track usage metrics and compliance scores
 - **✍️ Local Grammar Check (No RAG)**: Fix grammar, spelling, and formatting locally
 - **🛠️ Contract Fixing (Grammar + Compliance)**: Produce corrected, policy-aligned contracts

## 🏗️ Architecture

```
procurement-rag-system/
├── app/
│   ├── __init__.py
│   ├── rag_engine.py          # Core RAG system
│   ├── api.py                 # Flask REST API
│   └── streamlit_app.py       # Streamlit UI
├── data/
│   ├── policies/              # Store policy PDFs here
│   ├── contracts/             # Sample contracts
│   └── templates/             # Contract templates
├── chroma_db/                 # ChromaDB storage (auto-created)
├── pdf_artifacts/             # Docling artifacts (auto-created)
├── logs/                      # Application logs
├── tests/
│   ├── test_rag.py
│   └── test_api.py
├── .env                       # Environment variables
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
├── config.py                  # Configuration settings
├── README.md                  # This file
└── run.sh                     # Startup script

```

## 📋 Prerequisites

- Python 3.9 or higher
- Claude API key from Anthropic
- 4GB+ RAM recommended
- 2GB+ disk space for embeddings and database

## 🚀 Quick Start

### 1. Clone or Create Project

```bash
# Create project directory
mkdir procurement-rag-system
cd procurement-rag-system
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Claude API key
# ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### 5. Initialize Database

```bash
python -c "from app.rag_engine import ProcurementRAG; rag = ProcurementRAG(); print('Database initialized!')"
```

### 6. Upload Policies

```bash
# Place your policy PDFs in data/policies/
# Then run the import script
python scripts/import_policies.py
```

### 7. Run Applications

**Option A: Streamlit UI (Recommended for Users)**
```bash
streamlit run app/streamlit_app.py
```
Access at: http://localhost:8501

**Option B: Flask API (For Integrations)**
```bash
python app/api.py
```
Access at: http://localhost:5000

**Option C: Run Both (Separate Terminals)**
```bash
# Terminal 1
python app/api.py

# Terminal 2
streamlit run app/streamlit_app.py
```

## ☁️ One‑Click Deploy to Streamlit Cloud

1. Push this repo to GitHub.
2. Go to Streamlit Community Cloud → New app → pick this repo/branch.
3. App file path: `app/streamlit_app.py`.
4. Settings → Secrets:
   - `ANTHROPIC_API_KEY=your_key_here`
5. Deploy. Your public URL will be ready immediately.

Notes
- Grammar Check works locally (no external model). Fix Contract requires you to upload policies in the UI first.
- Keep `.env` out of the repo; use Streamlit Secrets instead.
 - Alternatively, you can paste the Claude API key directly in the Streamlit UI sidebar under “API Key” and click “Apply API Key”. This sets the key for the running session without needing Secrets.

## 📦 Installation Guide

### requirements.txt
```
# Core dependencies
anthropic==0.25.0
chromadb==0.4.22
sentence-transformers==2.5.1
docling==1.8.0
pypdf==3.17.4
langchain-text-splitters==0.0.1

# Web frameworks
flask==3.0.0
flask-cors==4.0.0
streamlit==1.31.1

# Utilities
python-dotenv==1.0.0
pydantic==2.6.0
numpy==1.26.4
pandas==2.2.0
language-tool-python==2.8.1

# Development
pytest==8.0.0
black==24.1.1
flake8==7.0.0
```

## 🔧 Configuration

### .env.example
```bash
# Claude API Configuration
ANTHROPIC_API_KEY=your-api-key-here
CLAUDE_MODEL=claude-sonnet-4-20250514
MAX_TOKENS=8000

# Database Configuration
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2

# API Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

# Streamlit Configuration
STREAMLIT_PORT=8501

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# File Upload
MAX_FILE_SIZE=10485760  # 10MB in bytes
ALLOWED_EXTENSIONS=pdf,docx,txt

# RAG Configuration
CHUNK_SIZE=800
CHUNK_OVERLAP=150
TOP_K_RESULTS=10
```

## 📖 Usage Examples

### Python API

```python
from app.rag_engine import ProcurementRAG

# Initialize
rag = ProcurementRAG()

# Store a policy
rag.store_document(
    "data/policies/procurement_policy.pdf",
    doc_type="policy",
    custom_metadata={"version": "2.1"}
)

# Check compliance
result = rag.check_compliance(
    input_text="Your contract text...",
    contract_type="service"
)
print(result["analysis"])

# Generate contract
contract = rag.generate_contract(
    contract_params={
        "parties": {...},
        "scope": "...",
        "value": "$100,000"
    },
    contract_type="service"
)
print(contract["contract"])

# Full workflow
workflow = rag.full_contract_workflow(
    initial_draft="Draft contract...",
    contract_type="service"
)
```

### REST API Endpoints

```bash
# Health check
curl http://localhost:5000/health

# Upload policy
curl -X POST http://localhost:5000/api/upload-policy \
  -F "file=@policy.pdf" \
  -F "doc_type=policy"

# Check compliance
curl -X POST http://localhost:5000/api/check-compliance \
  -H "Content-Type: application/json" \
  -d '{
    "contract_text": "Your contract...",
    "contract_type": "service"
  }'

# Generate contract
curl -X POST http://localhost:5000/api/generate-contract \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {...},
    "contract_type": "service"
  }'

# List policies
curl http://localhost:5000/api/list-documents

# Grammar check (local, no RAG/models)
curl -X POST http://localhost:5000/api/grammar-check \
  -H "Content-Type: application/json" \
  -d '{
    "contract_text": "This is a smaple agrement with erors.",
    "contract_type": "service"
  }'

# Fix contract (requires policies uploaded)
curl -X POST http://localhost:5000/api/fix-contract \
  -H "Content-Type: application/json" \
  -d '{
    "contract_text": "Your draft text here...",
    "contract_type": "service"
  }'
```

## 🎨 Streamlit UI Features

1. **📋 Compliance Checker**
   - Paste contract text
   - Select contract type
   - Get detailed compliance analysis
   - Download report

2. **📝 Contract Generator**
   - Fill in contract parameters
   - Choose contract type
   - Generate complete contract
   - Download as PDF/DOCX

3. **💡 Clause Analyzer**
   - Upload draft contract
   - Identify missing clauses
   - Get suggestions with templates

4. **📚 Policy Manager**
   - Upload policy documents
   - View stored policies
   - Delete/update policies
   - Search policies

5. **📊 Analytics Dashboard**
6. **✍️ Grammar & Clarity Check (Local)**
   - Paste or upload TXT
   - Local grammar/spell/style corrections (no RAG)
   - View issues and download corrected text

7. **🛠️ Fix Contract (Grammar + Compliance)**
   - Paste or upload TXT
   - Applies local grammar fixes and policy compliance using uploaded policies
   - Shows post-fix compliance analysis and lets you download the final contract
   - Usage statistics
   - Compliance trends
   - Common violations

## 🗂️ PyCharm Setup

### 1. Create New Project

1. Open PyCharm
2. File → New Project
3. Select location: `~/procurement-rag-system`
4. Choose "New environment using Virtualenv"
5. Base interpreter: Python 3.9+
6. Click "Create"

### 2. Configure Project Structure

```
Right-click on project root → Mark Directory as:
- app/ → Sources Root
- tests/ → Test Sources Root
- data/ → Excluded (optional)
- chroma_db/ → Excluded
```

### 3. Set Up Run Configurations

**Streamlit Configuration:**
- Run → Edit Configurations → Add New → Python
- Name: `Streamlit UI`
- Script path: `/path/to/venv/bin/streamlit`
- Parameters: `run app/streamlit_app.py`
- Working directory: Project root

**Flask Configuration:**
- Run → Edit Configurations → Add New → Python
- Name: `Flask API`
- Script path: `app/api.py`
- Working directory: Project root

### 4. Install Dependencies

```bash
# In PyCharm Terminal
pip install -r requirements.txt
```

### 5. Configure Environment Variables

1. Run → Edit Configurations
2. Select your configuration
3. Environment variables → Click 📝
4. Add: `ANTHROPIC_API_KEY=your-key-here`

### 6. Enable Code Quality Tools

```python
# Settings → Tools → Python Integrated Tools
# Docstring format: Google
# Test runner: pytest

# Settings → Editor → Inspections
# Enable: PEP 8 coding style violation
```

## 📁 Project File Organization

### Recommended Structure

```python
procurement-rag-system/
│
├── app/                          # Main application code
│   ├── __init__.py
│   ├── rag_engine.py            # Core RAG system (from artifact)
│   ├── api.py                   # Flask REST API
│   ├── streamlit_app.py         # Streamlit UI
│   └── utils/
│       ├── __init__.py
│       ├── logger.py            # Logging configuration
│       └── validators.py        # Input validation
│
├── data/                         # Data storage
│   ├── policies/                # Policy PDFs
│   │   ├── procurement_policy_2024.pdf
│   │   ├── vendor_guidelines.pdf
│   │   └── compliance_standards.pdf
│   ├── contracts/               # Sample contracts
│   │   ├── sample_service.txt
│   │   └── sample_procurement.txt
│   └── templates/               # Contract templates
│
├── chroma_db/                   # ChromaDB storage (auto-created)
│   ├── procurement_policies/
│   ├── vendor_information/
│   └── compliance_docs/
│
├── pdf_artifacts/               # Docling artifacts (auto-created)
│
├── logs/                        # Application logs
│   ├── app.log
│   └── error.log
│
├── tests/                       # Unit tests
│   ├── __init__.py
│   ├── test_rag_engine.py
│   ├── test_api.py
│   └── test_streamlit.py
│
├── scripts/                     # Utility scripts
│   ├── import_policies.py      # Bulk import policies
│   ├── backup_db.py            # Backup ChromaDB
│   └── cleanup.py              # Clean old data
│
├── docs/                        # Documentation
│   ├── API.md                  # API documentation
│   ├── DEPLOYMENT.md           # Deployment guide
│   └── USER_GUIDE.md           # User manual
│
├── .env                         # Environment variables (DO NOT COMMIT)
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore file
├── requirements.txt             # Python dependencies
├── config.py                    # Configuration settings
├── README.md                    # This file
└── run.sh                       # Startup script

```

## 🔒 Security Best Practices

1. **Never commit .env file**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use environment variables**
   ```python
   import os
   api_key = os.getenv("ANTHROPIC_API_KEY")
   ```

3. **Validate inputs**
   ```python
   from app.utils.validators import validate_contract_input
   ```

4. **Rate limiting**
   ```python
   # Implement in Flask API
   from flask_limiter import Limiter
   ```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_rag_engine.py

# Run with coverage
pytest --cov=app tests/

# Run in verbose mode
pytest -v
```

## 📊 Monitoring & Logging

```python
# View logs
tail -f logs/app.log

# Search for errors
grep ERROR logs/app.log

# Monitor API requests
grep "POST /api/" logs/app.log
```

## 🐛 Troubleshooting

### Common Issues

**1. Compliance Check Fails**
```bash
Error: "Claude API key not configured"
Solution: Set your API key in the web interface or environment variable
```

**2. Form Validation Errors**
```bash
Error: "Please fill in the buyerName field" (repeatedly)
Solution: Fixed in latest version - form validation now works correctly
```

**3. Documents Lost on Restart**
```bash
Issue: Uploaded documents disappear after server restart
Solution: Fixed - now uses persistent storage in ./chroma_db/
```

**4. ChromaDB Lock Error**
```bash
Error: Database is locked
Solution: Close all running instances, delete chroma_db/.chroma_lock
```

**5. Server Won't Start**
```bash
Error: "Cannot connect to API server"
Solution: Make sure Flask server is running on port 5000
```

**3. PDF Extraction Fails**
```bash
Error: Could not extract text from PDF
Solution: Ensure PDF is not encrypted, install tesseract for OCR
```

**4. Out of Memory**
```bash
Error: Memory allocation failed
Solution: Reduce CHUNK_SIZE or TOP_K_RESULTS in config
```

## 📈 Performance Optimization

1. **Use smaller embedding models** for faster indexing
2. **Implement caching** for frequent queries
3. **Batch process** multiple documents
4. **Use GPU** for embeddings if available
5. **Optimize chunk size** based on use case

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Authors

- SANJAY S
-SREE SNEHAN
-YUVA SHREE



---

**Made with ❤️ for Procurement Teams**
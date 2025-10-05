# 🏗️ Procurement RAG System - Architecture Documentation

## 📋 **Overview**

The Procurement RAG (Retrieval-Augmented Generation) System is a comprehensive AI-powered solution for contract analysis, compliance checking, and document generation. It combines multiple technologies to provide intelligent procurement assistance.

## 🎯 **System Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROCUREMENT RAG SYSTEM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   FRONTEND      │    │   BACKEND       │    │   AI/ML     │ │
│  │                 │    │                 │    │             │ │
│  │ • Web UI        │◄──►│ • Flask API     │◄──►│ • Anthropic │ │
│  │ • Script Lab    │    │ • RAG Engine    │    │ • Embeddings│ │
│  │ • Office Add-ins│    │ • Document Store│    │ • Vector DB  │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   DEPLOYMENT    │    │   INTEGRATION   │    │   STORAGE   │ │
│  │                 │    │                 │    │             │ │
│  │ • Local Server  │    │ • Microsoft     │    │ • ChromaDB  │ │
│  │ • Cloudflare    │    │   Office        │    │ • File      │ │
│  │ • Global Tunnel │    │ • Script Lab    │    │   System    │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 **Core Components**

### **1. Frontend Layer**

#### **Web Interface**
- **Technology**: HTML5, CSS3, JavaScript (Vanilla)
- **Purpose**: Primary user interface for document analysis
- **Features**:
  - Document upload and management
  - Real-time compliance checking
  - Contract generation and editing
  - Grammar and style analysis

#### **Microsoft Office Integration**
- **Script Lab**: JavaScript-based Office add-ins
- **Office Add-ins**: Native Word/Excel/PowerPoint integration
- **Purpose**: Direct document manipulation within Office

### **2. Backend Layer**

#### **Flask API Server**
```python
# Core Flask Application Structure
app/
├── api.py              # Main Flask application
├── rag_engine.py       # RAG processing engine
├── worker.py           # Cloudflare Worker entry point
└── streamlit_app.py    # Streamlit alternative UI
```

#### **RAG Engine**
- **Technology**: Python, Sentence Transformers, ChromaDB
- **Purpose**: Document processing and intelligent retrieval
- **Features**:
  - Document embedding generation
  - Semantic search capabilities
  - Context-aware retrieval
  - Compliance checking logic

### **3. AI/ML Layer**

#### **Language Model Integration**
- **Primary**: Anthropic Claude API
- **Purpose**: Natural language processing and generation
- **Capabilities**:
  - Contract analysis and generation
  - Compliance checking
  - Grammar and style correction
  - Missing clause detection

#### **Embedding System**
- **Model**: all-MiniLM-L6-v2 (Sentence Transformers)
- **Purpose**: Convert documents to vector representations
- **Storage**: ChromaDB vector database

## 📊 **Data Flow Architecture**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   USER      │    │  FRONTEND   │    │  BACKEND    │    │   AI/ML     │
│  INTERFACE  │    │             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       │ 1. Upload Doc     │                   │                   │
       ├──────────────────►│                   │                   │
       │                   │ 2. Send to API    │                   │
       │                   ├──────────────────►│                   │
       │                   │                   │ 3. Process Doc   │
       │                   │                   ├──────────────────►│
       │                   │                   │ 4. Generate      │
       │                   │                   │    Embeddings    │
       │                   │                   │◄──────────────────┤
       │                   │                   │ 5. Store in      │
       │                   │                   │    Vector DB     │
       │                   │                   │◄──────────────────┤
       │                   │ 6. Return Result  │                   │
       │                   │◄──────────────────┤                   │
       │ 7. Display Result │                   │                   │
       │◄──────────────────┤                   │                   │
```

## 🗄️ **Data Storage Architecture**

### **Vector Database (ChromaDB)**
```
┌─────────────────────────────────────────────────────────────┐
│                    CHROMADB STORAGE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  DOCUMENTS  │  │ EMBEDDINGS  │  │  METADATA   │        │
│  │             │  │             │  │             │        │
│  │ • PDF Files│  │ • 384-dim    │  │ • File Hash │        │
│  │ • Word Docs│  │ • Vectors    │  │ • Timestamp │        │
│  │ • Text     │  │ • Similarity │  │ • Type      │        │
│  │ • Policies │  │ • Search     │  │ • Size      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **File System Storage**
```
uploads/
├── corporate-procurement-policy.pdf
├── vendor-guidelines.docx
├── compliance-requirements.txt
└── contract-templates/
    ├── service-agreement.docx
    ├── procurement-contract.docx
    └── vendor-agreement.docx
```

## 🔄 **Processing Pipeline**

### **1. Document Ingestion**
```python
def process_document(file_path):
    # 1. Extract text from document
    text = extract_text(file_path)
    
    # 2. Generate embeddings
    embeddings = generate_embeddings(text)
    
    # 3. Store in vector database
    store_in_chromadb(text, embeddings, metadata)
    
    # 4. Index for search
    create_search_index(text, embeddings)
```

### **2. Query Processing**
```python
def process_query(user_query, context):
    # 1. Generate query embeddings
    query_embeddings = generate_embeddings(user_query)
    
    # 2. Search similar documents
    similar_docs = search_chromadb(query_embeddings, top_k=10)
    
    # 3. Build context for LLM
    context = build_context(similar_docs, user_query)
    
    # 4. Generate response with LLM
    response = call_anthropic_api(context, user_query)
    
    return response
```

## 🌐 **Deployment Architecture**

### **Local Development**
```
┌─────────────────────────────────────────────────────────────┐
│                    LOCAL DEVELOPMENT                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   BROWSER   │    │   FLASK     │    │   CHROMADB  │    │
│  │             │    │   SERVER    │    │             │    │
│  │ • Web UI    │◄──►│ • Port 5000 │◄──►│ • Local DB  │    │
│  │ • Script Lab│    │ • API       │    │ • Embeddings│    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **Cloudflare Deployment**
```
┌─────────────────────────────────────────────────────────────┐
│                    CLOUDFLARE DEPLOYMENT                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   GLOBAL    │    │ CLOUDFLARE  │    │   WORKER    │    │
│  │   USERS     │    │   TUNNEL    │    │             │    │
│  │             │    │             │    │ • Serverless│    │
│  │ • Worldwide │◄──►│ • HTTPS     │◄──►│ • Auto-scale│    │
│  │ • Office    │    │ • CDN       │    │ • Edge      │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🌐 **Global Deployment via Cloudflare Tunnel**

### **Cloudflare Tunnel Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                CLOUDFLARE TUNNEL DEPLOYMENT                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   GLOBAL    │    │ CLOUDFLARE  │    │   LOCAL     │    │
│  │   USERS     │    │   TUNNEL    │    │   SERVER    │    │
│  │             │    │             │    │             │    │
│  │ • Worldwide │◄──►│ • HTTPS     │◄──►│ • Flask API │    │
│  │ • Office    │    │ • CDN       │    │ • RAG Engine│    │
│  │ • Mobile    │    │ • Edge      │    │ • ChromaDB  │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **Tunnel Configuration**
- **Local Server**: `http://localhost:5000`
- **Tunnel Command**: `.\cloudflared tunnel --url http://127.0.0.1:5000`
- **Global URL**: `https://your-tunnel-url.trycloudflare.com`
- **Features**: HTTPS, CDN, Global Access, No Port Forwarding

## 🔌 **Integration Points**

### **Microsoft Office Integration**
```
┌─────────────────────────────────────────────────────────────┐
│                MICROSOFT OFFICE INTEGRATION                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   WORD      │    │  SCRIPT LAB │    │   API       │    │
│  │             │    │             │    │             │    │
│  │ • Documents │◄──►│ • JavaScript│◄──►│ • REST      │    │
│  │ • Selection │    │ • Functions │    │ • JSON     │    │
│  │ • Results   │    │ • Office API│    │ • CORS     │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **API Endpoints Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                    API ENDPOINTS                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   HEALTH    │  │   UPLOAD    │  │   ANALYSIS  │        │
│  │             │  │             │  │             │        │
│  │ • /health   │  │ • /upload   │  │ • /compliance│       │
│  │ • /status   │  │ • /list     │  │ • /grammar  │        │
│  │ • /docs     │  │ • /delete   │  │ • /generate │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **Performance Characteristics**

### **Scalability**
- **Local**: Single user, development environment
- **Cloudflare**: Global scale, auto-scaling workers
- **Vector DB**: Efficient similarity search with ChromaDB
- **API**: Stateless, horizontally scalable

### **Performance Metrics**
- **Document Processing**: ~2-5 seconds per document
- **Query Response**: ~1-3 seconds for compliance checks
- **Embedding Generation**: ~0.5-1 second per document
- **Vector Search**: ~100-500ms for similarity search

## 🔒 **Security Architecture**

### **Data Protection**
- **API Keys**: Secure storage and transmission
- **CORS**: Configured for cross-origin requests
- **HTTPS**: Encrypted communication (Cloudflare)
- **File Validation**: Type and size checking

### **Access Control**
- **Local**: Direct file system access
- **Cloudflare**: Worker-based access control
- **API**: Token-based authentication (Anthropic)

## 📈 **Monitoring and Logging**

### **Application Logs**
```
┌─────────────────────────────────────────────────────────────┐
│                    LOGGING SYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   FLASK     │  │   RAG       │  │   CHROMADB   │        │
│  │             │  │             │  │             │        │
│  │ • Requests  │  │ • Processing│  │ • Queries   │        │
│  │ • Errors    │  │ • Embeddings│  │ • Storage   │        │
│  │ • Performance│ │ • API Calls │  │ • Indexing  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ **Technology Stack**

### **Backend Technologies**
- **Python 3.9+**: Core programming language
- **Flask**: Web framework and API server
- **ChromaDB**: Vector database for embeddings
- **Sentence Transformers**: Text embedding generation
- **Anthropic API**: Large language model integration

### **Frontend Technologies**
- **HTML5/CSS3/JavaScript**: Web interface
- **Microsoft Office API**: Office integration
- **Script Lab**: Office add-in framework

### **Deployment Technologies**
- **Cloudflare Workers**: Serverless deployment
- **Cloudflare Tunnel**: Global access
- **Docker**: Containerization (optional)
- **Git**: Version control and deployment

## 🔄 **Development Workflow**

### **Local Development**
1. **Setup**: Install dependencies and configure environment
2. **Development**: Run Flask server locally
3. **Testing**: Use web interface and Script Lab
4. **Deployment**: Push to GitHub, deploy to Cloudflare

### **Production Deployment**
1. **Code**: Committed to GitHub repository
2. **Build**: Cloudflare Workers build process
3. **Deploy**: Automatic deployment to Cloudflare edge
4. **Monitor**: Cloudflare analytics and logging

## 📋 **Key Features Implementation**

### **Document Processing**
- **Multi-format Support**: PDF, Word, Text files
- **Text Extraction**: OCR and document parsing
- **Embedding Generation**: Vector representation
- **Storage**: Persistent vector database

### **AI Integration**
- **Context Retrieval**: Similar document finding
- **Prompt Engineering**: Optimized LLM prompts
- **Response Generation**: Natural language responses
- **Error Handling**: Graceful failure management

### **User Interface**
- **Responsive Design**: Works on all devices
- **Office Integration**: Native Office experience
- **Real-time Feedback**: Live processing updates
- **Error Handling**: User-friendly error messages

This architecture provides a robust, scalable, and user-friendly procurement RAG system that can be deployed locally or globally with minimal configuration.

"""
Configuration settings for the Procurement RAG System
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# ========================================
# API CONFIGURATION
# ========================================

# Claude API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8000"))

# ========================================
# DATABASE CONFIGURATION
# ========================================

# ChromaDB Configuration
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", str(BASE_DIR / "chroma_db"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# ========================================
# WEB SERVER CONFIGURATION
# ========================================

# Flask Configuration
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# Streamlit Configuration
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))

# ========================================
# FILE UPLOAD CONFIGURATION
# ========================================

# File Upload Settings
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB in bytes
ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", "pdf,docx,txt").split(","))
UPLOAD_FOLDER = BASE_DIR / "uploads"

# ========================================
# RAG SYSTEM CONFIGURATION
# ========================================

# Text Processing
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "10"))

# ========================================
# LOGGING CONFIGURATION
# ========================================

# Logging Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "app.log"))

# ========================================
# DIRECTORY STRUCTURE
# ========================================

# Data directories
DATA_DIR = BASE_DIR / "data"
POLICIES_DIR = DATA_DIR / "policies"
CONTRACTS_DIR = DATA_DIR / "contracts"
TEMPLATES_DIR = DATA_DIR / "templates"

# System directories
LOGS_DIR = BASE_DIR / "logs"
CHROMA_DB_DIR = BASE_DIR / "chroma_db"
PDF_ARTIFACTS_DIR = BASE_DIR / "pdf_artifacts"

# ========================================
# VALIDATION CONFIGURATION
# ========================================

# Contract types
CONTRACT_TYPES = [
    "service",
    "procurement", 
    "vendor",
    "software",
    "consulting",
    "construction",
    "general"
]

# Document types
DOCUMENT_TYPES = [
    "policy",
    "vendor", 
    "compliance"
]

# ========================================
# SECURITY CONFIGURATION
# ========================================

# Rate limiting (requests per minute)
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "60"))

# API key validation
REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", "False").lower() == "true"

# ========================================
# DEVELOPMENT CONFIGURATION
# ========================================

# Development settings
DEV_MODE = os.getenv("DEV_MODE", "False").lower() == "true"
ENABLE_CORS = os.getenv("ENABLE_CORS", "True").lower() == "true"

# Testing
TEST_MODE = os.getenv("TEST_MODE", "False").lower() == "true"

# ========================================
# HELPER FUNCTIONS
# ========================================

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        LOGS_DIR,
        UPLOAD_FOLDER,
        CHROMA_DB_DIR,
        PDF_ARTIFACTS_DIR,
        POLICIES_DIR,
        CONTRACTS_DIR,
        TEMPLATES_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_config_summary():
    """Get a summary of current configuration"""
    return {
        "api_key_configured": bool(ANTHROPIC_API_KEY),
        "chroma_db_path": CHROMA_DB_PATH,
        "embedding_model": EMBEDDING_MODEL,
        "flask_host": FLASK_HOST,
        "flask_port": FLASK_PORT,
        "streamlit_port": STREAMLIT_PORT,
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
        "allowed_extensions": list(ALLOWED_EXTENSIONS),
        "chunk_size": CHUNK_SIZE,
        "top_k_results": TOP_K_RESULTS,
        "log_level": LOG_LEVEL,
        "dev_mode": DEV_MODE
    }

# Initialize directories on import
ensure_directories()

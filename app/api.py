# Flask REST API
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
import logging
from functools import wraps
import os
import json

# Add parent directory to path for imports when running directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag_engine import ProcurementRAG

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)  # Enable CORS for all routes with no restrictions

# Add additional CORS headers for iframe embedding
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('X-Frame-Options', 'ALLOWALL')
    response.headers.add('X-Content-Type-Options', 'nosniff')
    response.headers.add('X-XSS-Protection', '0')
    return response

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'txt', 'docx'}

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize RAG system
rag_system = None

def init_rag():
    """Initialize RAG system on first request"""
    global rag_system
    if rag_system is None:
        logger.info("Initializing Procurement RAG System...")
        rag_system = ProcurementRAG()
        logger.info("RAG System initialized successfully")
    return rag_system

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('logs', exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def require_json(f):
    """Decorator to ensure request contains JSON"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json",
                "status": "error"
            }), 400
        return f(*args, **kwargs)
    return decorated_function

def handle_errors(f):
    """Decorator for consistent error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({
                "error": str(e),
                "status": "error",
                "endpoint": f.__name__
            }), 500
    return decorated_function

# ========================================
# CONFIGURATION ENDPOINTS
# ========================================

@app.route('/api/set-api-key', methods=['POST'])
@require_json
@handle_errors
def set_api_key():
    """Set Anthropic API key at runtime and reinitialize RAG instance."""
    global rag_system
    data = request.get_json()
    key = data.get('api_key')
    if not key:
        return jsonify({"status": "error", "error": "api_key is required"}), 400
    # Optionally validate prefix
    if not isinstance(key, str) or len(key) < 10:
        return jsonify({"status": "error", "error": "invalid api_key format"}), 400
    os.environ['ANTHROPIC_API_KEY'] = key
    rag_system = ProcurementRAG(api_key=key)
    logger.info("Anthropic API key updated via /api/set-api-key and RAG reinitialized")
    return jsonify({"status": "success"}), 200

# ========================================
# HEALTH & STATUS ENDPOINTS
# ========================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Procurement RAG API",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }), 200

@app.route('/api/status', methods=['GET'])
@handle_errors
def get_status():
    """Get system status and statistics"""
    rag = init_rag()
    docs = rag.get_document_list()
    
    status = {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "statistics": {
            "total_documents": len(docs),
            "policy_documents": len([d for d in docs if d.get('doc_type') == 'policy']),
            "vendor_documents": len([d for d in docs if d.get('doc_type') == 'vendor']),
            "compliance_documents": len([d for d in docs if d.get('doc_type') == 'compliance'])
        },
        "config": {
            "max_file_size": "10MB",
            "allowed_extensions": list(app.config['ALLOWED_EXTENSIONS']),
            "embedding_model": rag.embedding_model_name
        }
    }
    
    return jsonify(status), 200

# ========================================
# DOCUMENT MANAGEMENT ENDPOINTS
# ========================================

@app.route('/api/upload-policy', methods=['POST'])
@handle_errors
def upload_policy():
    """Upload a policy document"""
    rag = init_rag()
    
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({
            "error": "No file provided",
            "status": "error"
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            "error": "No file selected",
            "status": "error"
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            "error": f"File type not allowed. Allowed types: {app.config['ALLOWED_EXTENSIONS']}",
            "status": "error"
        }), 400
    
    # Get additional parameters
    doc_type = request.form.get('doc_type', 'policy')
    version = request.form.get('version')
    department = request.form.get('department')
    
    # Save file temporarily
    filename = secure_filename(file.filename)
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(temp_path)
    
    try:
        # Prepare metadata
        custom_metadata = {
            "uploaded_via": "api",
            "upload_timestamp": datetime.now().isoformat()
        }
        if version:
            custom_metadata["version"] = version
        if department:
            custom_metadata["department"] = department
        
        # Store in RAG system
        result = rag.store_document(
            temp_path,
            doc_type=doc_type,
            custom_metadata=custom_metadata
        )
        
        logger.info(f"Successfully uploaded {filename}: {result['chunks']} chunks")
        
        return jsonify({
            "status": "success",
            "message": f"Successfully uploaded {filename}",
            "filename": filename,
            "doc_type": result['doc_type'],
            "chunks_created": result['chunks'],
            "doc_hash": result['doc_hash']
        }), 201
        
    except Exception as e:
        logger.error(f"Error uploading {filename}: {e}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/api/list-documents', methods=['GET'])
@handle_errors
def list_documents():
    """List all stored documents"""
    rag = init_rag()
    
    # Optional filters
    doc_type = request.args.get('doc_type')
    
    docs = rag.get_document_list()
    
    # Apply filter if specified
    if doc_type:
        docs = [d for d in docs if d.get('doc_type') == doc_type]
    
    return jsonify({
        "status": "success",
        "count": len(docs),
        "documents": docs
    }), 200

@app.route('/api/delete-document/<doc_hash>', methods=['DELETE'])
@handle_errors
def delete_document(doc_hash):
    """Delete a document by hash"""
    rag = init_rag()
    
    deleted_count = rag.delete_document(doc_hash)
    
    if deleted_count > 0:
        logger.info(f"Deleted document {doc_hash}: {deleted_count} chunks")
        return jsonify({
            "status": "success",
            "message": f"Deleted {deleted_count} chunks",
            "doc_hash": doc_hash
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Document not found",
            "doc_hash": doc_hash
        }), 404

# ========================================
# SEARCH ENDPOINT
# ========================================

@app.route('/api/search', methods=['POST'])
@require_json
@handle_errors
def search_policies():
    """Search for relevant policies"""
    rag = init_rag()
    
    data = request.get_json()
    
    # Validate required fields
    if 'query' not in data:
        return jsonify({
            "error": "Query parameter is required",
            "status": "error"
        }), 400
    
    query = data['query']
    doc_type = data.get('doc_type')
    top_k = data.get('top_k', 5)
    filters = data.get('filters')
    
    # Perform search
    results = rag.search(
        query=query,
        doc_type=doc_type,
        top_k=top_k,
        filters=filters
    )
    
    return jsonify({
        "status": "success",
        "query": query,
        "results_count": len(results['results']),
        "results": results['results']
    }), 200

# ========================================
# COMPLIANCE & ANALYSIS ENDPOINTS
# ========================================

@app.route('/api/check-compliance', methods=['POST'])
@require_json
@handle_errors
def check_compliance():
    """Check contract compliance"""
    rag = init_rag()
    
    data = request.get_json()
    
    # Validate required fields
    if 'contract_text' not in data:
        return jsonify({
            "error": "contract_text parameter is required",
            "status": "error"
        }), 400
    
    contract_text = data['contract_text']
    contract_type = data.get('contract_type', 'general')
    
    logger.info(f"Checking compliance for {contract_type} contract")
    
    # Perform compliance check
    result = rag.check_compliance(
        input_text=contract_text,
        contract_type=contract_type
    )
    
    if result["status"] == "success":
        return jsonify({
            "status": "success",
            "contract_type": contract_type,
            "analysis": result["analysis"],
            "policies_checked": result["policies_checked"],
            "contract_length": result["contract_length"],
            "timestamp": datetime.now().isoformat()
        }), 200
    else:
        return jsonify({
            "status": "error",
            "error": result.get("error", "Unknown error")
        }), 500

@app.route('/api/grammar-check', methods=['POST'])
@require_json
@handle_errors
def grammar_check():
    """Grammar/spell check and clarity fix for a contract"""
    rag = init_rag()
    data = request.get_json()
    if 'contract_text' not in data:
        return jsonify({
            "error": "contract_text parameter is required",
            "status": "error"
        }), 400
    contract_text = data['contract_text']
    contract_type = data.get('contract_type', 'general')
    logger.info(f"Running grammar check for {contract_type} contract")
    result = rag.grammar_check(contract_text, contract_type)
    status_code = 200 if result.get("status") == "success" else 500
    return jsonify({
        **result,
        "timestamp": datetime.now().isoformat()
    }), status_code

@app.route('/api/fix-contract', methods=['POST'])
@require_json
@handle_errors
def fix_contract():
    """Produce an error-free, compliant contract based on uploaded policies"""
    rag = init_rag()
    data = request.get_json()
    if 'contract_text' not in data:
        return jsonify({
            "error": "contract_text parameter is required",
            "status": "error"
        }), 400
    contract_text = data['contract_text']
    contract_type = data.get('contract_type', 'general')
    logger.info(f"Fixing contract for compliance and grammar: {contract_type}")
    result = rag.fix_contract(contract_text, contract_type)
    status_code = 200 if result.get("status") == "success" else 500
    return jsonify({
        **result,
        "timestamp": datetime.now().isoformat()
    }), status_code

@app.route('/api/suggest-clauses', methods=['POST'])
@require_json
@handle_errors
def suggest_clauses():
    """Suggest missing clauses"""
    rag = init_rag()
    
    data = request.get_json()
    
    # Validate required fields
    if 'contract_text' not in data:
        return jsonify({
            "error": "contract_text parameter is required",
            "status": "error"
        }), 400
    
    contract_text = data['contract_text']
    contract_type = data.get('contract_type', 'general')
    
    logger.info(f"Analyzing missing clauses for {contract_type} contract")
    
    # Analyze missing clauses
    result = rag.suggest_missing_clauses(
        input_text=contract_text,
        contract_type=contract_type
    )
    
    if result["status"] == "success":
        return jsonify({
            "status": "success",
            "contract_type": contract_type,
            "suggestions": result["suggestions"],
            "policies_referenced": result["policies_referenced"],
            "timestamp": datetime.now().isoformat()
        }), 200
    else:
        return jsonify({
            "status": "error",
            "error": result.get("error", "Unknown error")
        }), 500

# ========================================
# CONTRACT GENERATION ENDPOINT
# ========================================

@app.route('/api/generate-contract', methods=['POST'])
@require_json
@handle_errors
def generate_contract():
    """Generate a complete contract"""
    rag = init_rag()
    
    data = request.get_json()
    
    # Validate required fields
    if 'parameters' not in data:
        return jsonify({
            "error": "parameters field is required",
            "status": "error"
        }), 400
    
    contract_params = data['parameters']
    contract_type = data.get('contract_type', 'general')
    include_optional = data.get('include_optional_clauses', True)
    
    logger.info(f"Generating {contract_type} contract")
    
    # Generate contract
    result = rag.generate_contract(
        contract_params=contract_params,
        contract_type=contract_type,
        include_optional_clauses=include_optional
    )
    
    if result["status"] == "success":
        return jsonify({
            "status": "success",
            "contract": result["contract"],
            "contract_type": result["contract_type"],
            "word_count": result["word_count"],
            "policies_referenced": result["policies_referenced"],
            "compliance_check": result.get("compliance_check"),
            "timestamp": datetime.now().isoformat()
        }), 200
    else:
        return jsonify({
            "status": "error",
            "error": result.get("error", "Unknown error")
        }), 500

# ========================================
# FULL WORKFLOW ENDPOINT
# ========================================

@app.route('/api/full-workflow', methods=['POST'])
@require_json
@handle_errors
def full_workflow():
    """Execute full contract workflow"""
    rag = init_rag()
    
    data = request.get_json()
    
    initial_draft = data.get('initial_draft')
    contract_params = data.get('contract_params')
    contract_type = data.get('contract_type', 'general')
    
    if not initial_draft and not contract_params:
        return jsonify({
            "error": "Either initial_draft or contract_params must be provided",
            "status": "error"
        }), 400
    
    logger.info(f"Executing full workflow for {contract_type} contract")
    
    # Execute workflow
    result = rag.full_contract_workflow(
        initial_draft=initial_draft,
        contract_params=contract_params,
        contract_type=contract_type
    )
    
    if result["status"] == "success":
        return jsonify({
            "status": "success",
            "workflow": result["workflow"],
            "steps": result["steps"],
            "final_contract": result["final_contract"],
            "improved_contract": result.get("improved_contract"),
            "timestamp": datetime.now().isoformat()
        }), 200
    else:
        return jsonify({
            "status": "error",
            "error": result.get("error", "Unknown error")
        }), 500

# ========================================
# BATCH OPERATIONS
# ========================================

@app.route('/api/batch-compliance', methods=['POST'])
@require_json
@handle_errors
def batch_compliance_check():
    """Check compliance for multiple contracts"""
    rag = init_rag()
    
    data = request.get_json()
    
    if 'contracts' not in data or not isinstance(data['contracts'], list):
        return jsonify({
            "error": "contracts field must be a list",
            "status": "error"
        }), 400
    
    contracts = data['contracts']
    results = []
    
    logger.info(f"Processing batch compliance check for {len(contracts)} contracts")
    
    for i, contract_data in enumerate(contracts):
        if 'text' not in contract_data:
            results.append({
                "index": i,
                "status": "error",
                "error": "Missing 'text' field"
            })
            continue
        
        try:
            result = rag.check_compliance(
                input_text=contract_data['text'],
                contract_type=contract_data.get('contract_type', 'general')
            )
            results.append({
                "index": i,
                "status": "success",
                "analysis": result["analysis"]
            })
        except Exception as e:
            results.append({
                "index": i,
                "status": "error",
                "error": str(e)
            })
    
    return jsonify({
        "status": "success",
        "total_contracts": len(contracts),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }), 200

# ========================================
# ERROR HANDLERS
# ========================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "status": "error",
        "code": 404
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "Method not allowed",
        "status": "error",
        "code": 405
    }), 405

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "error": "File too large. Maximum size is 10MB",
        "status": "error",
        "code": 413
    }), 413

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal server error",
        "status": "error",
        "code": 500
    }), 500

# ========================================
# API DOCUMENTATION ENDPOINT
# ========================================

@app.route('/api/docs', methods=['GET'])
def api_documentation():
    """API documentation"""
    docs = {
        "service": "Procurement Contract RAG API",
        "version": "1.0.0",
        "base_url": request.host_url + "api",
        "endpoints": {
            "health": {
                "path": "/health",
                "method": "GET",
                "description": "Health check endpoint"
            },
            "grammar_check": {
                "path": "/api/grammar-check",
                "method": "POST",
                "description": "Grammar/spell check and clarity fix (local, no RAG)",
                "body": {
                    "contract_text": "required: contract text",
                    "contract_type": "optional: contract type (default: general)"
                }
            },
            "fix_contract": {
                "path": "/api/fix-contract",
                "method": "POST",
                "description": "Correct grammar and apply policy compliance to return final contract",
                "body": {
                    "contract_text": "required: contract text",
                    "contract_type": "optional: contract type (default: general)"
                }
            },
            "status": {
                "path": "/api/status",
                "method": "GET",
                "description": "Get system status and statistics"
            },
            "upload_policy": {
                "path": "/api/upload-policy",
                "method": "POST",
                "description": "Upload a policy document",
                "parameters": {
                    "file": "PDF file (multipart/form-data)",
                    "doc_type": "optional: policy|vendor|compliance",
                    "version": "optional: document version",
                    "department": "optional: department name"
                }
            },
            "list_documents": {
                "path": "/api/list-documents",
                "method": "GET",
                "description": "List all stored documents",
                "parameters": {
                    "doc_type": "optional: filter by type"
                }
            },
            "delete_document": {
                "path": "/api/delete-document/<doc_hash>",
                "method": "DELETE",
                "description": "Delete a document by hash"
            },
            "search": {
                "path": "/api/search",
                "method": "POST",
                "description": "Search for relevant policies",
                "body": {
                    "query": "required: search query",
                    "doc_type": "optional: document type filter",
                    "top_k": "optional: number of results (default: 5)",
                    "filters": "optional: metadata filters"
                }
            },
            "check_compliance": {
                "path": "/api/check-compliance",
                "method": "POST",
                "description": "Check contract compliance",
                "body": {
                    "contract_text": "required: contract text",
                    "contract_type": "optional: contract type (default: general)"
                }
            },
            "suggest_clauses": {
                "path": "/api/suggest-clauses",
                "method": "POST",
                "description": "Suggest missing clauses",
                "body": {
                    "contract_text": "required: contract text",
                    "contract_type": "optional: contract type (default: general)"
                }
            },
            "generate_contract": {
                "path": "/api/generate-contract",
                "method": "POST",
                "description": "Generate a complete contract",
                "body": {
                    "parameters": "required: contract parameters object",
                    "contract_type": "optional: contract type (default: general)",
                    "include_optional_clauses": "optional: boolean (default: true)"
                }
            },
            "full_workflow": {
                "path": "/api/full-workflow",
                "method": "POST",
                "description": "Execute full contract workflow",
                "body": {
                    "initial_draft": "optional: existing contract text",
                    "contract_params": "optional: parameters for generation",
                    "contract_type": "optional: contract type (default: general)"
                }
            },
            "batch_compliance": {
                "path": "/api/batch-compliance",
                "method": "POST",
                "description": "Check compliance for multiple contracts",
                "body": {
                    "contracts": "required: array of contract objects"
                }
            }
        },
        "example_requests": {
            "check_compliance": {
                "url": "/api/check-compliance",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": {
                    "contract_text": "Your contract text here...",
                    "contract_type": "service"
                }
            },
            "generate_contract": {
                "url": "/api/generate-contract",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": {
                    "parameters": {
                        "parties": {
                            "buyer": {"name": "ABC Corp", "address": "123 Street"},
                            "vendor": {"name": "XYZ Ltd", "address": "456 Avenue"}
                        },
                        "scope": "Service description",
                        "value": "$100,000",
                        "duration": "1 year"
                    },
                    "contract_type": "service",
                    "include_optional_clauses": True
                }
            }
        }
    }
    
    return jsonify(docs), 200

# ========================================
# MAIN
# ========================================

if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Procurement RAG API on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info("API Documentation available at: /api/docs")
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )

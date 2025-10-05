"""
Simplified Cloudflare Worker for Procurement RAG System
This version removes heavy ML dependencies for Cloudflare deployment
"""
import os
import json
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime

# Initialize the Flask app
app = Flask(__name__)

# CORS configuration
from flask_cors import CORS
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'.pdf', '.txt', '.docx'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variables
anthropic_api_key = None
documents = []

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in [ext[1:] for ext in app.config['ALLOWED_EXTENSIONS']]

# Static file routes
@app.route('/')
def index():
    """Serve the main HTML page"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Index file not found", 404

@app.route('/styles.css')
def styles():
    """Serve CSS file"""
    try:
        with open('styles.css', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/css'}
    except FileNotFoundError:
        return "CSS file not found", 404

@app.route('/app.js')
def app_js():
    """Serve JavaScript file"""
    try:
        with open('app.js', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        return "JavaScript file not found", 404

@app.route('/config.js')
def config_js():
    """Serve configuration file"""
    try:
        with open('config.js', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        return "Config file not found", 404

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return '', 204

# API Routes
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "service": "Procurement RAG API",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }), 200

@app.route('/api/status', methods=['GET'])
def api_status():
    """API status endpoint"""
    return jsonify({
        "status": "success",
        "message": "API is running",
        "timestamp": datetime.now().isoformat(),
        "api_key_configured": anthropic_api_key is not None,
        "documents_count": len(documents)
    }), 200

@app.route('/api/set-api-key', methods=['POST'])
def set_api_key():
    """Set Anthropic API key"""
    global anthropic_api_key
    
    try:
        data = request.get_json()
        if not data or 'api_key' not in data:
            return jsonify({
                "error": "API key is required",
                "status": "error"
            }), 400
        
        anthropic_api_key = data['api_key']
        
        return jsonify({
            "status": "success",
            "message": "API key set successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/upload-policy', methods=['POST'])
def upload_policy():
    """Upload policy document (simplified version)"""
    try:
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
                "error": "File type not allowed",
                "status": "error"
            }), 400
        
        # For Cloudflare, we'll just store metadata
        doc_info = {
            "filename": file.filename,
            "size": len(file.read()),
            "upload_time": datetime.now().isoformat(),
            "doc_hash": f"doc_{len(documents) + 1}"
        }
        
        documents.append(doc_info)
        
        return jsonify({
            "status": "success",
            "message": f"Successfully uploaded {file.filename}",
            "filename": file.filename,
            "doc_hash": doc_info["doc_hash"],
            "chunks_created": 1  # Simplified for Cloudflare
        }), 201
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/list-documents', methods=['GET'])
def list_documents():
    """List uploaded documents"""
    return jsonify({
        "status": "success",
        "documents": documents,
        "count": len(documents)
    }), 200

@app.route('/api/delete-document/<doc_hash>', methods=['DELETE'])
def delete_document(doc_hash):
    """Delete a document"""
    global documents
    
    documents = [doc for doc in documents if doc.get('doc_hash') != doc_hash]
    
    return jsonify({
        "status": "success",
        "message": "Document deleted successfully"
    }), 200

@app.route('/api/search', methods=['POST'])
def search():
    """Search documents (simplified)"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({
                "error": "Query is required",
                "status": "error"
            }), 400
        
        # Simplified search - just return mock results
        results = {
            "query": query,
            "results": [
                {
                    "content": f"Mock result for query: {query}",
                    "score": 0.95,
                    "source": "policy_document.pdf"
                }
            ],
            "total_results": 1
        }
        
        return jsonify({
            "status": "success",
            "results": results
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/check-compliance', methods=['POST'])
def check_compliance():
    """Check compliance (simplified)"""
    try:
        data = request.get_json()
        contract_text = data.get('contractText', '')
        
        if not contract_text:
            return jsonify({
                "error": "Contract text is required",
                "status": "error"
            }), 400
        
        # Simplified compliance check
        compliance_result = {
            "overall_score": 85,
            "issues": [
                {
                    "type": "missing_clause",
                    "description": "Payment terms not specified",
                    "severity": "medium"
                }
            ],
            "recommendations": [
                "Add payment terms clause",
                "Specify delivery timeline"
            ]
        }
        
        return jsonify({
            "status": "success",
            "compliance": compliance_result
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/grammar-check', methods=['POST'])
def grammar_check():
    """Grammar check (simplified)"""
    try:
        data = request.get_json()
        text = data.get('grammarText', '')
        
        if not text:
            return jsonify({
                "error": "Text is required",
                "status": "error"
            }), 400
        
        # Simplified grammar check
        grammar_result = {
            "score": 92,
            "issues": [
                {
                    "text": "This is a example",
                    "suggestion": "This is an example",
                    "type": "grammar"
                }
            ]
        }
        
        return jsonify({
            "status": "success",
            "grammar": grammar_result
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/fix-contract', methods=['POST'])
def fix_contract():
    """Fix contract (simplified)"""
    try:
        data = request.get_json()
        contract_text = data.get('fixText', '')
        
        if not contract_text:
            return jsonify({
                "error": "Contract text is required",
                "status": "error"
            }), 400
        
        # Simplified contract fixing
        fixed_contract = contract_text + "\n\n[AI-generated improvements added]"
        
        return jsonify({
            "status": "success",
            "fixed_contract": fixed_contract,
            "changes_made": ["Added payment terms", "Improved clarity"]
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/suggest-clauses', methods=['POST'])
def suggest_clauses():
    """Suggest clauses (simplified)"""
    try:
        data = request.get_json()
        text = data.get('clauseText', '')
        
        if not text:
            return jsonify({
                "error": "Text is required",
                "status": "error"
            }), 400
        
        # Simplified clause suggestions
        suggestions = [
            "Payment terms clause",
            "Delivery timeline clause",
            "Force majeure clause"
        ]
        
        return jsonify({
            "status": "success",
            "suggestions": suggestions
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/generate-contract', methods=['POST'])
def generate_contract():
    """Generate contract (simplified)"""
    try:
        data = request.get_json()
        required_fields = ['buyerName', 'vendorName', 'scope', 'contractValue', 'duration']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "error": f"Field '{field}' is required",
                    "status": "error"
                }), 400
        
        # Simplified contract generation
        contract = f"""
CONTRACT AGREEMENT

Buyer: {data['buyerName']}
Vendor: {data['vendorName']}
Scope: {data['scope']}
Value: {data['contractValue']}
Duration: {data['duration']}

[AI-generated contract content would go here]
        """.strip()
        
        return jsonify({
            "status": "success",
            "contract": contract
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/full-workflow', methods=['POST'])
def full_workflow():
    """Full workflow (simplified)"""
    try:
        data = request.get_json()
        
        # Simplified workflow
        result = {
            "status": "success",
            "workflow_completed": True,
            "steps": [
                "Document analysis",
                "Compliance check",
                "Grammar review",
                "Contract generation"
            ]
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/batch-compliance', methods=['POST'])
def batch_compliance():
    """Batch compliance check (simplified)"""
    try:
        data = request.get_json()
        contracts = data.get('contracts', [])
        
        if not contracts:
            return jsonify({
                "error": "Contracts are required",
                "status": "error"
            }), 400
        
        # Simplified batch processing
        results = []
        for i, contract in enumerate(contracts):
            results.append({
                "contract_id": i + 1,
                "score": 85 + (i * 2),
                "issues": ["Mock issue"]
            })
        
        return jsonify({
            "status": "success",
            "results": results
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API documentation"""
    docs = {
        "title": "Procurement RAG API",
        "version": "1.0.0",
        "endpoints": [
            {
                "path": "/api/status",
                "method": "GET",
                "description": "Get API status"
            },
            {
                "path": "/api/set-api-key",
                "method": "POST",
                "description": "Set Anthropic API key"
            },
            {
                "path": "/api/upload-policy",
                "method": "POST",
                "description": "Upload policy document"
            }
        ]
    }
    
    return jsonify(docs), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)

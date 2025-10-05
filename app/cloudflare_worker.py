"""
Cloudflare Workers-compatible version of the Procurement RAG System
This is a separate, lightweight version for Cloudflare deployment
that doesn't interfere with the local development system.
"""
import os
import json
from flask import Flask, request, jsonify
from datetime import datetime

# Initialize Flask app for Cloudflare Workers
app = Flask(__name__)

# CORS configuration
from flask_cors import CORS
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'.pdf', '.txt', '.docx'}

# Global variables for Cloudflare Workers
anthropic_api_key = None
documents = []
rag_system = None

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
    """Serve configuration file - use production config for Cloudflare"""
    try:
        with open('config.production.js', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        # Fallback to regular config
        with open('config.js', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript'}

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return '', 204

# API Routes
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "service": "Procurement RAG API (Cloudflare)",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "deployment": "cloudflare"
    }), 200

@app.route('/api/status', methods=['GET'])
def api_status():
    """API status endpoint"""
    return jsonify({
        "status": "success",
        "message": "API is running on Cloudflare Workers",
        "timestamp": datetime.now().isoformat(),
        "api_key_configured": anthropic_api_key is not None,
        "documents_count": len(documents),
        "deployment": "cloudflare"
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
            "message": "API key set successfully for Cloudflare deployment"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/upload-policy', methods=['POST'])
def upload_policy():
    """Upload policy document (Cloudflare-compatible version)"""
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
        
        # For Cloudflare Workers, we'll simulate document processing
        doc_info = {
            "filename": file.filename,
            "size": len(file.read()),
            "upload_time": datetime.now().isoformat(),
            "doc_hash": f"cloudflare_doc_{len(documents) + 1}",
            "chunks": 1,  # Simplified for Cloudflare
            "processing": "simulated"  # Cloudflare Workers limitation
        }
        
        documents.append(doc_info)
        
        return jsonify({
            "status": "success",
            "message": f"Successfully uploaded {file.filename} (Cloudflare Workers)",
            "filename": file.filename,
            "doc_hash": doc_info["doc_hash"],
            "chunks_created": 1,
            "deployment": "cloudflare"
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
        "count": len(documents),
        "deployment": "cloudflare"
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
    """Search documents (Cloudflare-compatible simulation)"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({
                "error": "Query is required",
                "status": "error"
            }), 400
        
        # Simulated search results for Cloudflare Workers
        results = {
            "query": query,
            "results": [
                {
                    "content": f"Cloudflare Workers search result for: {query}",
                    "score": 0.95,
                    "source": "cloudflare_processed_document.pdf",
                    "deployment": "cloudflare"
                }
            ],
            "total_results": 1,
            "processing_note": "Simulated search for Cloudflare Workers deployment"
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
    """Check compliance (Cloudflare-compatible simulation)"""
    try:
        data = request.get_json()
        contract_text = data.get('contractText', '')
        
        if not contract_text:
            return jsonify({
                "error": "Contract text is required",
                "status": "error"
            }), 400
        
        # Simulated compliance check for Cloudflare Workers
        compliance_result = {
            "overall_score": 88,
            "issues": [
                {
                    "type": "missing_clause",
                    "description": "Payment terms not specified (Cloudflare simulation)",
                    "severity": "medium"
                }
            ],
            "recommendations": [
                "Add payment terms clause",
                "Specify delivery timeline",
                "Include force majeure clause"
            ],
            "deployment": "cloudflare",
            "processing_note": "Simulated compliance check for Cloudflare Workers"
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
    """Grammar check (Cloudflare-compatible simulation)"""
    try:
        data = request.get_json()
        text = data.get('grammarText', '')
        
        if not text:
            return jsonify({
                "error": "Text is required",
                "status": "error"
            }), 400
        
        # Simulated grammar check for Cloudflare Workers
        grammar_result = {
            "score": 94,
            "issues": [
                {
                    "text": "This is a example",
                    "suggestion": "This is an example",
                    "type": "grammar"
                }
            ],
            "deployment": "cloudflare",
            "processing_note": "Simulated grammar check for Cloudflare Workers"
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
    """Fix contract (Cloudflare-compatible simulation)"""
    try:
        data = request.get_json()
        contract_text = data.get('fixText', '')
        
        if not contract_text:
            return jsonify({
                "error": "Contract text is required",
                "status": "error"
            }), 400
        
        # Simulated contract fixing for Cloudflare Workers
        fixed_contract = contract_text + "\n\n[AI-generated improvements added via Cloudflare Workers]"
        
        return jsonify({
            "status": "success",
            "fixed_contract": fixed_contract,
            "changes_made": ["Added payment terms", "Improved clarity", "Cloudflare Workers processing"],
            "deployment": "cloudflare"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/suggest-clauses', methods=['POST'])
def suggest_clauses():
    """Suggest clauses (Cloudflare-compatible simulation)"""
    try:
        data = request.get_json()
        text = data.get('clauseText', '')
        
        if not text:
            return jsonify({
                "error": "Text is required",
                "status": "error"
            }), 400
        
        # Simulated clause suggestions for Cloudflare Workers
        suggestions = [
            "Payment terms clause (Cloudflare optimized)",
            "Delivery timeline clause",
            "Force majeure clause",
            "Data protection clause",
            "Termination clause"
        ]
        
        return jsonify({
            "status": "success",
            "suggestions": suggestions,
            "deployment": "cloudflare"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/generate-contract', methods=['POST'])
def generate_contract():
    """Generate contract (Cloudflare-compatible simulation)"""
    try:
        data = request.get_json()
        required_fields = ['buyerName', 'vendorName', 'scope', 'contractValue', 'duration']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "error": f"Field '{field}' is required",
                    "status": "error"
                }), 400
        
        # Simulated contract generation for Cloudflare Workers
        contract = f"""
CONTRACT AGREEMENT (Cloudflare Workers Generated)

Buyer: {data['buyerName']}
Vendor: {data['vendorName']}
Scope: {data['scope']}
Value: {data['contractValue']}
Duration: {data['duration']}

[AI-generated contract content via Cloudflare Workers]
[This is a simulated contract generation for Cloudflare Workers deployment]
        """.strip()
        
        return jsonify({
            "status": "success",
            "contract": contract,
            "deployment": "cloudflare"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/full-workflow', methods=['POST'])
def full_workflow():
    """Full workflow (Cloudflare-compatible simulation)"""
    try:
        data = request.get_json()
        
        # Simulated workflow for Cloudflare Workers
        result = {
            "status": "success",
            "workflow_completed": True,
            "steps": [
                "Document analysis (Cloudflare Workers)",
                "Compliance check (simulated)",
                "Grammar review (simulated)",
                "Contract generation (simulated)"
            ],
            "deployment": "cloudflare",
            "processing_note": "Simulated full workflow for Cloudflare Workers"
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/batch-compliance', methods=['POST'])
def batch_compliance():
    """Batch compliance check (Cloudflare-compatible simulation)"""
    try:
        data = request.get_json()
        contracts = data.get('contracts', [])
        
        if not contracts:
            return jsonify({
                "error": "Contracts are required",
                "status": "error"
            }), 400
        
        # Simulated batch processing for Cloudflare Workers
        results = []
        for i, contract in enumerate(contracts):
            results.append({
                "contract_id": i + 1,
                "score": 85 + (i * 2),
                "issues": ["Mock issue (Cloudflare Workers)"],
                "deployment": "cloudflare"
            })
        
        return jsonify({
            "status": "success",
            "results": results,
            "deployment": "cloudflare"
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
        "title": "Procurement RAG API (Cloudflare Workers)",
        "version": "1.0.0",
        "deployment": "cloudflare",
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
                "description": "Upload policy document (simulated for Cloudflare Workers)"
            }
        ],
        "note": "This is a Cloudflare Workers-compatible version with simulated AI processing"
    }
    
    return jsonify(docs), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Cloudflare Workers entry point
def handler(request):
    """Main handler for Cloudflare Workers"""
    return app(request.environ, lambda *args: None)

if __name__ == "__main__":
    # For local testing of Cloudflare worker
    print("🚀 Starting Cloudflare Workers-compatible server...")
    print("📝 Note: This is a simulated version for Cloudflare deployment")
    print("🌐 Local development server runs separately on port 5000")
    app.run(host='0.0.0.0', port=8080, debug=True)

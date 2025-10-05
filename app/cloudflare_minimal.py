"""
Ultra-minimal Cloudflare Worker for Procurement RAG System
This version uses only built-in Python libraries to avoid size limits
"""
import json
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Global variables
anthropic_api_key = None
documents = []

def allowed_file(filename):
    """Check if file extension is allowed"""
    allowed_extensions = {'.pdf', '.txt', '.docx'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in [ext[1:] for ext in allowed_extensions]

def create_response(body, status_code=200, headers=None):
    """Create HTTP response"""
    if headers is None:
        headers = {}
    
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    default_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body) if isinstance(body, dict) else body
    }

def handle_cors(request):
    """Handle CORS preflight requests"""
    if request.get('method') == 'OPTIONS':
        return create_response({}, 200)

def serve_static_file(filename, content_type):
    """Serve static files"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return create_response(content, 200, {'Content-Type': content_type})
    except FileNotFoundError:
        return create_response({'error': f'{filename} not found'}, 404)

def handle_health():
    """Health check endpoint"""
    return create_response({
        "service": "Procurement RAG API (Cloudflare Minimal)",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "deployment": "cloudflare-minimal"
    })

def handle_status():
    """API status endpoint"""
    return create_response({
        "status": "success",
        "message": "API is running on Cloudflare Workers (Minimal)",
        "timestamp": datetime.now().isoformat(),
        "api_key_configured": anthropic_api_key is not None,
        "documents_count": len(documents),
        "deployment": "cloudflare-minimal"
    })

def handle_set_api_key(data):
    """Set Anthropic API key"""
    global anthropic_api_key
    
    if not data or 'api_key' not in data:
        return create_response({
            "error": "API key is required",
            "status": "error"
        }, 400)
    
    anthropic_api_key = data['api_key']
    
    return create_response({
        "status": "success",
        "message": "API key set successfully for Cloudflare deployment (Minimal)"
    })

def handle_upload_policy(data):
    """Upload policy document (simulated)"""
    if 'file' not in data:
        return create_response({
            "error": "No file provided",
            "status": "error"
        }, 400)
    
    file_info = data['file']
    if not file_info.get('filename'):
        return create_response({
            "error": "No file selected",
            "status": "error"
        }, 400)
    
    filename = file_info['filename']
    if not allowed_file(filename):
        return create_response({
            "error": "File type not allowed",
            "status": "error"
        }, 400)
    
    # Simulate document processing
    doc_info = {
        "filename": filename,
        "size": file_info.get('size', 0),
        "upload_time": datetime.now().isoformat(),
        "doc_hash": f"minimal_doc_{len(documents) + 1}",
        "chunks": 1,
        "processing": "simulated-minimal"
    }
    
    documents.append(doc_info)
    
    return create_response({
        "status": "success",
        "message": f"Successfully uploaded {filename} (Cloudflare Minimal)",
        "filename": filename,
        "doc_hash": doc_info["doc_hash"],
        "chunks_created": 1,
        "deployment": "cloudflare-minimal"
    }, 201)

def handle_list_documents():
    """List uploaded documents"""
    return create_response({
        "status": "success",
        "documents": documents,
        "count": len(documents),
        "deployment": "cloudflare-minimal"
    })

def handle_search(data):
    """Search documents (simulated)"""
    query = data.get('query', '')
    
    if not query:
        return create_response({
            "error": "Query is required",
            "status": "error"
        }, 400)
    
    # Simulated search results
    results = {
        "query": query,
        "results": [
            {
                "content": f"Minimal search result for: {query}",
                "score": 0.95,
                "source": "minimal_processed_document.pdf",
                "deployment": "cloudflare-minimal"
            }
        ],
        "total_results": 1,
        "processing_note": "Simulated search for Cloudflare Workers minimal deployment"
    }
    
    return create_response({
        "status": "success",
        "results": results
    })

def handle_compliance_check(data):
    """Check compliance (simulated)"""
    contract_text = data.get('contractText', '')
    
    if not contract_text:
        return create_response({
            "error": "Contract text is required",
            "status": "error"
        }, 400)
    
    # Simulated compliance check
    compliance_result = {
        "overall_score": 90,
        "issues": [
            {
                "type": "missing_clause",
                "description": "Payment terms not specified (Minimal simulation)",
                "severity": "medium"
            }
        ],
        "recommendations": [
            "Add payment terms clause",
            "Specify delivery timeline",
            "Include force majeure clause"
        ],
        "deployment": "cloudflare-minimal",
        "processing_note": "Simulated compliance check for Cloudflare Workers minimal deployment"
    }
    
    return create_response({
        "status": "success",
        "compliance": compliance_result
    })

def handle_grammar_check(data):
    """Grammar check (simulated)"""
    text = data.get('grammarText', '')
    
    if not text:
        return create_response({
            "error": "Text is required",
            "status": "error"
        }, 400)
    
    # Simulated grammar check
    grammar_result = {
        "score": 96,
        "issues": [
            {
                "text": "This is a example",
                "suggestion": "This is an example",
                "type": "grammar"
            }
        ],
        "deployment": "cloudflare-minimal",
        "processing_note": "Simulated grammar check for Cloudflare Workers minimal deployment"
    }
    
    return create_response({
        "status": "success",
        "grammar": grammar_result
    })

def handle_fix_contract(data):
    """Fix contract (simulated)"""
    contract_text = data.get('fixText', '')
    
    if not contract_text:
        return create_response({
            "error": "Contract text is required",
            "status": "error"
        }, 400)
    
    # Simulated contract fixing
    fixed_contract = contract_text + "\n\n[AI-generated improvements added via Cloudflare Workers Minimal]"
    
    return create_response({
        "status": "success",
        "fixed_contract": fixed_contract,
        "changes_made": ["Added payment terms", "Improved clarity", "Cloudflare Workers minimal processing"],
        "deployment": "cloudflare-minimal"
    })

def handle_suggest_clauses(data):
    """Suggest clauses (simulated)"""
    text = data.get('clauseText', '')
    
    if not text:
        return create_response({
            "error": "Text is required",
            "status": "error"
        }, 400)
    
    # Simulated clause suggestions
    suggestions = [
        "Payment terms clause (Minimal optimized)",
        "Delivery timeline clause",
        "Force majeure clause",
        "Data protection clause",
        "Termination clause"
    ]
    
    return create_response({
        "status": "success",
        "suggestions": suggestions,
        "deployment": "cloudflare-minimal"
    })

def handle_generate_contract(data):
    """Generate contract (simulated)"""
    required_fields = ['buyerName', 'vendorName', 'scope', 'contractValue', 'duration']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return create_response({
                "error": f"Field '{field}' is required",
                "status": "error"
            }, 400)
    
    # Simulated contract generation
    contract = f"""
CONTRACT AGREEMENT (Cloudflare Workers Minimal Generated)

Buyer: {data['buyerName']}
Vendor: {data['vendorName']}
Scope: {data['scope']}
Value: {data['contractValue']}
Duration: {data['duration']}

[AI-generated contract content via Cloudflare Workers Minimal]
[This is a simulated contract generation for minimal deployment]
    """.strip()
    
    return create_response({
        "status": "success",
        "contract": contract,
        "deployment": "cloudflare-minimal"
    })

def handle_full_workflow(data):
    """Full workflow (simulated)"""
    result = {
        "status": "success",
        "workflow_completed": True,
        "steps": [
            "Document analysis (Minimal)",
            "Compliance check (simulated)",
            "Grammar review (simulated)",
            "Contract generation (simulated)"
        ],
        "deployment": "cloudflare-minimal",
        "processing_note": "Simulated full workflow for Cloudflare Workers minimal deployment"
    }
    
    return create_response(result)

def handle_batch_compliance(data):
    """Batch compliance check (simulated)"""
    contracts = data.get('contracts', [])
    
    if not contracts:
        return create_response({
            "error": "Contracts are required",
            "status": "error"
        }, 400)
    
    # Simulated batch processing
    results = []
    for i, contract in enumerate(contracts):
        results.append({
            "contract_id": i + 1,
            "score": 88 + (i * 2),
            "issues": ["Mock issue (Minimal)"],
            "deployment": "cloudflare-minimal"
        })
    
    return create_response({
        "status": "success",
        "results": results,
        "deployment": "cloudflare-minimal"
    })

def handle_api_docs():
    """API documentation"""
    docs = {
        "title": "Procurement RAG API (Cloudflare Workers Minimal)",
        "version": "1.0.0",
        "deployment": "cloudflare-minimal",
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
                "description": "Upload policy document (simulated)"
            }
        ],
        "note": "This is a minimal Cloudflare Workers-compatible version with simulated AI processing"
    }
    
    return create_response(docs)

def handler(request):
    """Main handler for Cloudflare Workers"""
    # Handle CORS
    cors_response = handle_cors(request)
    if cors_response:
        return cors_response
    
    method = request.get('method', 'GET')
    url = request.get('url', '')
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    # Parse request body for POST requests
    data = {}
    if method in ['POST', 'PUT']:
        try:
            body = request.get('body', '')
            if body:
                data = json.loads(body)
        except:
            pass
    
    # Route handling
    if path == '/':
        return serve_static_file('index.html', 'text/html')
    elif path == '/styles.css':
        return serve_static_file('styles.css', 'text/css')
    elif path == '/app.js':
        return serve_static_file('app.js', 'application/javascript')
    elif path == '/config.js':
        return serve_static_file('config.production.js', 'application/javascript')
    elif path == '/favicon.ico':
        return create_response('', 204)
    elif path == '/health':
        return handle_health()
    elif path == '/api/status':
        return handle_status()
    elif path == '/api/set-api-key' and method == 'POST':
        return handle_set_api_key(data)
    elif path == '/api/upload-policy' and method == 'POST':
        return handle_upload_policy(data)
    elif path == '/api/list-documents':
        return handle_list_documents()
    elif path == '/api/search' and method == 'POST':
        return handle_search(data)
    elif path == '/api/check-compliance' and method == 'POST':
        return handle_compliance_check(data)
    elif path == '/api/grammar-check' and method == 'POST':
        return handle_grammar_check(data)
    elif path == '/api/fix-contract' and method == 'POST':
        return handle_fix_contract(data)
    elif path == '/api/suggest-clauses' and method == 'POST':
        return handle_suggest_clauses(data)
    elif path == '/api/generate-contract' and method == 'POST':
        return handle_generate_contract(data)
    elif path == '/api/full-workflow' and method == 'POST':
        return handle_full_workflow(data)
    elif path == '/api/batch-compliance' and method == 'POST':
        return handle_batch_compliance(data)
    elif path == '/api/docs':
        return handle_api_docs()
    else:
        return create_response({'error': 'Not found'}, 404)

# For local testing
if __name__ == "__main__":
    print("🚀 Starting Cloudflare Workers Minimal server...")
    print("📝 Note: This is an ultra-minimal version for Cloudflare deployment")
    print("🌐 Local development server runs separately on port 5000")
    print("💡 This version uses only built-in Python libraries")
    
    # Simple local server for testing
    import http.server
    import socketserver
    from urllib.parse import urlparse, parse_qs
    
    class MinimalHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            if path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = handle_health()
                self.wfile.write(response['body'].encode())
            else:
                self.send_response(404)
                self.end_headers()
        
        def do_POST(self):
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
            except:
                data = {}
            
            if path == '/api/status':
                response = handle_status()
            elif path == '/api/set-api-key':
                response = handle_set_api_key(data)
            else:
                response = create_response({'error': 'Not found'}, 404)
            
            self.send_response(response['statusCode'])
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response['body'].encode())
    
    PORT = 8080
    with socketserver.TCPServer(("", PORT), MinimalHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        httpd.serve_forever()

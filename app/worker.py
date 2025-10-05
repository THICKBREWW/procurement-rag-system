"""
Cloudflare Worker for Procurement RAG System
"""
import os
import json
from flask import Flask, request, jsonify, render_template_string
from app.api import app as flask_app
from app.rag_engine import ProcurementRAG

# Initialize the Flask app
app = Flask(__name__)

# Copy routes from the main API
@app.route('/')
def index():
    return flask_app.index()

@app.route('/styles.css')
def styles():
    return flask_app.styles()

@app.route('/app.js')
def app_js():
    return flask_app.app_js()

@app.route('/config.js')
def config_js():
    return flask_app.config_js()

@app.route('/favicon.ico')
def favicon():
    return flask_app.favicon()

@app.route('/api/status', methods=['GET'])
def api_status():
    return flask_app.api_status()

@app.route('/api/set-api-key', methods=['POST'])
def set_api_key():
    return flask_app.set_api_key()

@app.route('/api/upload-policy', methods=['POST'])
def upload_policy():
    return flask_app.upload_policy()

@app.route('/api/list-documents', methods=['GET'])
def list_documents():
    return flask_app.list_documents()

@app.route('/api/delete-document/<doc_hash>', methods=['DELETE'])
def delete_document(doc_hash):
    return flask_app.delete_document(doc_hash)

@app.route('/api/search', methods=['POST'])
def search():
    return flask_app.search()

@app.route('/api/check-compliance', methods=['POST'])
def check_compliance():
    return flask_app.check_compliance()

@app.route('/api/grammar-check', methods=['POST'])
def grammar_check():
    return flask_app.grammar_check()

@app.route('/api/fix-contract', methods=['POST'])
def fix_contract():
    return flask_app.fix_contract()

@app.route('/api/suggest-clauses', methods=['POST'])
def suggest_clauses():
    return flask_app.suggest_clauses()

@app.route('/api/generate-contract', methods=['POST'])
def generate_contract():
    return flask_app.generate_contract()

@app.route('/api/full-workflow', methods=['POST'])
def full_workflow():
    return flask_app.full_workflow()

@app.route('/api/batch-compliance', methods=['POST'])
def batch_compliance():
    return flask_app.batch_compliance()

@app.route('/api/docs', methods=['GET'])
def api_docs():
    return flask_app.api_docs()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "Procurement RAG API is running"})

# Cloudflare Worker entry point
def handler(request):
    """Main handler for Cloudflare Worker"""
    return app(request.environ, lambda *args: None)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

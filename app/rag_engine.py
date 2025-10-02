# pip install docling chromadb sentence-transformers pypdf langchain-text-splitters anthropic python-dotenv

import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from docling.document_converter import DocumentConverter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json
import hashlib
import logging
import os
from anthropic import Anthropic

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcurementRAG:
    """
    Session-based RAG system for procurement policies with Claude AI integration.
    Uses in-memory ChromaDB - all data is cleared when session ends.
    Perfect for uploading policies on-the-fly and getting instant answers.
    """
    
    def __init__(self, api_key=None):
        """Initialize with in-memory database (non-persistent)"""
        self.embedding_model_name = "all-MiniLM-L6-v2"
        self.embedder = SentenceTransformer(self.embedding_model_name)
        
        # Initialize Claude API
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("⚠️  No Claude API key provided. Set ANTHROPIC_API_KEY environment variable.")
        self.claude = Anthropic(api_key=self.api_key) if self.api_key else None
        
        # Initialize ChromaDB with IN-MEMORY client (ephemeral)
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.embedding_model_name
        )
        
        # Use ephemeral client - data only exists in current session
        self.client = chromadb.EphemeralClient()
        
        # Create collections for different document types (in-memory)
        self.policy_collection = self.client.get_or_create_collection(
            name="procurement_policies",
            embedding_function=embedding_fn,
            metadata={"description": "Procurement policies and procedures"}
        )
        
        self.vendor_collection = self.client.get_or_create_collection(
            name="vendor_information",
            embedding_function=embedding_fn,
            metadata={"description": "Vendor guidelines and contracts"}
        )
        
        self.compliance_collection = self.client.get_or_create_collection(
            name="compliance_docs",
            embedding_function=embedding_fn,
            metadata={"description": "Compliance and regulatory documents"}
        )
        
        # Track uploaded documents in this session
        self.session_documents = []
        
        logger.info(f"✅ Initialized ProcurementRAG with ephemeral storage (session-based)")
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, any]:
        """Enhanced PDF extraction with structure preservation."""
        try:
            converter = DocumentConverter()
            result = converter.convert(pdf_path)
            
            metadata = {
                "filename": Path(pdf_path).name,
                "filepath": pdf_path,
                "page_count": len(result.document.pages) if hasattr(result.document, 'pages') else 0,
                "extraction_date": datetime.now().isoformat(),
            }
            
            text = result.document.export_to_markdown()
            doc_hash = hashlib.md5(text.encode()).hexdigest()
            metadata["doc_hash"] = doc_hash
            
            logger.info(f"✅ Extracted text from {metadata['filename']}")
            return {"text": text, "metadata": metadata}
            
        except Exception as e:
            logger.error(f"❌ Error extracting PDF {pdf_path}: {e}")
            raise
    
    def smart_chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """Advanced chunking with semantic awareness."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ";", ",", " ", ""],
            is_separator_regex=False
        )
        
        chunks = splitter.split_text(text)
        
        chunk_dicts = []
        for i, chunk in enumerate(chunks):
            chunk_meta = metadata.copy()
            chunk_meta.update({
                "chunk_id": i,
                "chunk_total": len(chunks),
                "chunk_size": len(chunk)
            })
            chunk_dicts.append({"text": chunk, "metadata": chunk_meta})
        
        logger.info(f"✅ Created {len(chunk_dicts)} semantic chunks")
        return chunk_dicts
    
    def categorize_document(self, filename: str, text: str) -> str:
        """Auto-categorize document based on content and filename."""
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        if any(k in text_lower or k in filename_lower for k in 
               ["policy", "procedure", "guideline", "standard operating"]):
            return "policy"
        elif any(k in text_lower or k in filename_lower for k in 
                 ["vendor", "supplier", "contract", "rfp", "rfq"]):
            return "vendor"
        elif any(k in text_lower or k in filename_lower for k in 
                 ["compliance", "regulation", "audit", "sox", "gdpr"]):
            return "compliance"
        else:
            return "policy"
    
    def store_document(
        self, 
        pdf_path: str, 
        doc_type: Optional[str] = None,
        custom_metadata: Optional[Dict] = None
    ):
        """Store a procurement document in the appropriate in-memory collection."""
        extracted = self.extract_text_from_pdf(pdf_path)
        text = extracted["text"]
        metadata = extracted["metadata"]
        
        if custom_metadata:
            metadata.update(custom_metadata)
        
        if not doc_type:
            doc_type = self.categorize_document(metadata["filename"], text)
        
        metadata["doc_type"] = doc_type
        metadata["session_upload"] = True
        
        collection = self._get_collection(doc_type)
        chunks = self.smart_chunk_text(text, metadata)
        
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        ids = [f"{metadata['doc_hash']}_chunk_{i}" for i in range(len(chunks))]
        
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        # Track in session
        self.session_documents.append({
            "filename": metadata["filename"],
            "doc_type": doc_type,
            "doc_hash": metadata["doc_hash"],
            "chunks": len(chunks),
            "upload_time": datetime.now().isoformat()
        })
        
        logger.info(f"✅ Stored {len(chunks)} chunks from '{metadata['filename']}' in '{doc_type}' collection")
        return {"doc_type": doc_type, "chunks": len(chunks), "doc_hash": metadata["doc_hash"]}
    
    def _get_collection(self, doc_type: str):
        """Get the appropriate collection based on document type."""
        collections = {
            "policy": self.policy_collection,
            "vendor": self.vendor_collection,
            "compliance": self.compliance_collection
        }
        return collections.get(doc_type, self.policy_collection)
    
    def search(
        self,
        query: str,
        doc_type: Optional[str] = None,
        top_k: int = 5,
        filters: Optional[Dict] = None
    ) -> Dict:
        """Enhanced search with filtering - only searches uploaded documents."""
        results = {"query": query, "results": []}
        
        collections_to_search = []
        if doc_type:
            collections_to_search = [(doc_type, self._get_collection(doc_type))]
        else:
            collections_to_search = [
                ("policy", self.policy_collection),
                ("vendor", self.vendor_collection),
                ("compliance", self.compliance_collection)
            ]
        
        for coll_name, collection in collections_to_search:
            try:
                search_results = collection.query(
                    query_texts=[query],
                    n_results=top_k,
                    where=filters
                )
                
                if search_results['documents'][0]:
                    for i, doc in enumerate(search_results['documents'][0]):
                        result_item = {
                            "collection": coll_name,
                            "text": doc,
                            "metadata": search_results['metadatas'][0][i],
                            "distance": search_results['distances'][0][i] if 'distances' in search_results else None
                        }
                        results["results"].append(result_item)
            except Exception as e:
                logger.warning(f"Search error in {coll_name}: {e}")
        
        results["results"].sort(key=lambda x: x["distance"] if x["distance"] else float('inf'))
        results["results"] = results["results"][:top_k]
        
        logger.info(f"🔎 Found {len(results['results'])} results for query: '{query}'")
        return results
    
    def get_relevant_policies(self, context: str, top_k: int = 10) -> str:
        """Retrieve relevant policies for a given context - only from uploaded docs."""
        results = self.search(context, top_k=top_k)
        
        policy_text = "\n\n---\n\n".join([
            f"Source: {r['metadata'].get('filename', 'Unknown')}\n{r['text']}"
            for r in results["results"]
        ])
        
        return policy_text
    
    def check_compliance(self, input_text: str, contract_type: str = "general") -> Dict:
        """
        Check if input text complies with uploaded procurement policies.
        Only checks against documents uploaded in this session.
        """
        if not self.claude:
            raise ValueError("Claude API key not configured")
        
        if not self.session_documents:
            return {
                "status": "error",
                "error": "No policies uploaded. Please upload policy documents first."
            }
        
        logger.info(f"🔍 Checking compliance against {len(self.session_documents)} uploaded documents...")
        
        # Retrieve relevant policies
        policy_context = self.get_relevant_policies(
            f"{contract_type} contract requirements policies compliance",
            top_k=10
        )
        
        if not policy_context.strip():
            return {
                "status": "error",
                "error": "No relevant policies found in uploaded documents. Please upload appropriate policy documents."
            }
        
        # Create compliance check prompt
        prompt = f"""You are a procurement compliance expert. Analyze the following contract text against the provided procurement policies.

UPLOADED PROCUREMENT POLICIES (from current session):
{policy_context}

CONTRACT TEXT TO ANALYZE:
{input_text}

Please provide a detailed compliance analysis with:

1. COMPLIANCE STATUS: Overall assessment (Compliant/Non-Compliant/Partially Compliant)

2. VIOLATIONS: List any specific policy violations or non-compliant sections with:
   - The violated policy requirement
   - The problematic section in the contract
   - Severity (Critical/High/Medium/Low)

3. MISSING CLAUSES: Identify required clauses that are missing based on policies:
   - Clause name
   - Why it's required
   - Policy reference

4. RECOMMENDATIONS: Specific suggestions to achieve compliance

Format your response as a structured analysis that's easy to parse."""

        try:
            message = self.claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis = message.content[0].text
            
            logger.info("✅ Compliance check completed")
            
            return {
                "status": "success",
                "analysis": analysis,
                "policies_checked": len(self.session_documents),
                "contract_length": len(input_text),
                "uploaded_docs": [doc["filename"] for doc in self.session_documents]
            }
            
        except Exception as e:
            logger.error(f"❌ Compliance check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def suggest_missing_clauses(self, input_text: str, contract_type: str = "general") -> Dict:
        """
        Identify and suggest missing clauses based on uploaded policies only.
        """
        if not self.claude:
            raise ValueError("Claude API key not configured")
        
        if not self.session_documents:
            return {
                "status": "error",
                "error": "No policies uploaded. Please upload policy documents first."
            }
        
        logger.info(f"💡 Analyzing missing clauses against {len(self.session_documents)} uploaded documents...")
        
        # Retrieve relevant policies
        policy_context = self.get_relevant_policies(
            f"{contract_type} contract required clauses terms conditions",
            top_k=12
        )
        
        if not policy_context.strip():
            return {
                "status": "error",
                "error": "No relevant policies found. Please upload appropriate policy documents."
            }
        
        prompt = f"""You are a procurement legal expert. Review the contract text and identify missing clauses based on the uploaded procurement policies.

UPLOADED PROCUREMENT POLICIES (from current session):
{policy_context}

CURRENT CONTRACT TEXT:
{input_text}

Analyze what's missing and provide:

1. MISSING CRITICAL CLAUSES: Essential clauses that MUST be included
   - Clause title
   - Purpose and importance
   - Template/example text
   - Policy reference

2. MISSING RECOMMENDED CLAUSES: Important but not critical clauses
   - Clause title
   - Benefits of inclusion
   - Template/example text

3. ENHANCEMENT SUGGESTIONS: Ways to strengthen existing clauses
   - Current clause reference
   - Suggested improvements
   - Rationale

Provide detailed, actionable suggestions with example text for each missing clause."""

        try:
            message = self.claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=5000,
                temperature=0.4,
                messages=[{"role": "user", "content": prompt}]
            )
            
            suggestions = message.content[0].text
            
            logger.info("✅ Missing clause analysis completed")
            
            return {
                "status": "success",
                "suggestions": suggestions,
                "policies_referenced": len(self.session_documents),
                "uploaded_docs": [doc["filename"] for doc in self.session_documents]
            }
            
        except Exception as e:
            logger.error(f"❌ Missing clause analysis failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def generate_contract(
        self,
        contract_params: Dict,
        contract_type: str = "general",
        include_optional_clauses: bool = True
    ) -> Dict:
        """
        Generate a complete contract based on input parameters and uploaded policies.
        Only uses policies uploaded in the current session.
        """
        if not self.claude:
            raise ValueError("Claude API key not configured")
        
        if not self.session_documents:
            return {
                "status": "error",
                "error": "No policies uploaded. Please upload policy documents first to generate compliant contracts."
            }
        
        logger.info(f"📝 Generating {contract_type} contract using {len(self.session_documents)} uploaded policies...")
        
        # Retrieve relevant policies and templates
        policy_context = self.get_relevant_policies(
            f"{contract_type} contract template structure required clauses",
            top_k=15
        )
        
        if not policy_context.strip():
            return {
                "status": "error",
                "error": "No relevant policies found. Please upload appropriate policy documents."
            }
        
        # Format contract parameters
        params_text = json.dumps(contract_params, indent=2)
        
        prompt = f"""You are an expert procurement contract drafter. Generate a complete, legally sound contract based on the provided parameters and the uploaded procurement policies.

UPLOADED PROCUREMENT POLICIES AND REQUIREMENTS (from current session):
{policy_context}

CONTRACT PARAMETERS:
{params_text}

CONTRACT TYPE: {contract_type}
INCLUDE OPTIONAL CLAUSES: {include_optional_clauses}

Generate a comprehensive contract that:

1. Follows all procurement policies and compliance requirements from the uploaded documents
2. Includes all mandatory clauses (payment terms, termination, liability, warranties, etc.)
3. Is professionally formatted with proper sections and numbering
4. Uses clear, unambiguous legal language
5. Incorporates the specific parameters provided
6. Includes {"optional recommended clauses" if include_optional_clauses else "only mandatory clauses"}

Structure the contract with:
- Title and Contract Number
- Parties section
- Recitals/Background
- Definitions
- Scope of Work/Services
- Payment Terms
- Term and Termination
- Warranties and Representations
- Liability and Indemnification
- Compliance clauses
- General Provisions
- Signature blocks

Generate the complete contract ready for review and execution."""

        try:
            message = self.claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            contract = message.content[0].text
            
            # Run a quick compliance check on generated contract
            logger.info("🔍 Running self-check on generated contract...")
            compliance_check = self.check_compliance(contract, contract_type)
            
            logger.info("✅ Contract generation completed")
            
            return {
                "status": "success",
                "contract": contract,
                "contract_type": contract_type,
                "parameters_used": contract_params,
                "compliance_check": compliance_check,
                "word_count": len(contract.split()),
                "policies_referenced": len(self.session_documents),
                "uploaded_docs": [doc["filename"] for doc in self.session_documents]
            }
            
        except Exception as e:
            logger.error(f"❌ Contract generation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def full_contract_workflow(
        self,
        initial_draft: Optional[str] = None,
        contract_params: Optional[Dict] = None,
        contract_type: str = "general"
    ) -> Dict:
        """
        Complete workflow using only uploaded policies in current session.
        """
        if not self.claude:
            raise ValueError("Claude API key not configured")
        
        if not self.session_documents:
            return {
                "status": "error",
                "error": "No policies uploaded. Please upload policy documents first."
            }
        
        logger.info("🚀 Starting full contract workflow...")
        
        workflow_result = {
            "workflow": "complete",
            "steps": [],
            "uploaded_docs_used": [doc["filename"] for doc in self.session_documents]
        }
        
        # Step 1: Generate or use provided contract
        if initial_draft:
            logger.info("📄 Using provided draft...")
            contract_text = initial_draft
            workflow_result["steps"].append({
                "step": "initial_draft_provided",
                "status": "success"
            })
        elif contract_params:
            logger.info("📝 Generating new contract...")
            gen_result = self.generate_contract(contract_params, contract_type)
            if gen_result["status"] == "success":
                contract_text = gen_result["contract"]
                workflow_result["steps"].append({
                    "step": "contract_generation",
                    "status": "success",
                    "details": gen_result
                })
            else:
                return {"status": "error", "error": "Contract generation failed", "details": gen_result}
        else:
            return {"status": "error", "error": "Must provide either initial_draft or contract_params"}
        
        # Step 2: Compliance check
        logger.info("🔍 Checking compliance...")
        compliance_result = self.check_compliance(contract_text, contract_type)
        workflow_result["steps"].append({
            "step": "compliance_check",
            "status": compliance_result["status"],
            "details": compliance_result
        })
        
        # Step 3: Missing clause analysis
        logger.info("💡 Analyzing missing clauses...")
        missing_result = self.suggest_missing_clauses(contract_text, contract_type)
        workflow_result["steps"].append({
            "step": "missing_clause_analysis",
            "status": missing_result["status"],
            "details": missing_result
        })
        
        # Step 4: Generate improved version if issues found
        if "non-compliant" in compliance_result.get("analysis", "").lower() or \
           "missing critical" in missing_result.get("suggestions", "").lower():
            
            logger.info("🔧 Generating improved contract version...")
            
            improvement_prompt = f"""Based on the compliance check and missing clause analysis, generate an improved version of this contract using the uploaded policies.

ORIGINAL CONTRACT:
{contract_text}

COMPLIANCE ISSUES:
{compliance_result.get('analysis', '')}

MISSING CLAUSES:
{missing_result.get('suggestions', '')}

Generate a complete, corrected contract that addresses all issues and includes all missing clauses."""

            try:
                message = self.claude.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=8000,
                    temperature=0.3,
                    messages=[{"role": "user", "content": improvement_prompt}]
                )
                
                improved_contract = message.content[0].text
                workflow_result["improved_contract"] = improved_contract
                workflow_result["steps"].append({
                    "step": "contract_improvement",
                    "status": "success"
                })
                
            except Exception as e:
                logger.warning(f"⚠️  Could not generate improved version: {e}")
        
        workflow_result["status"] = "success"
        workflow_result["final_contract"] = workflow_result.get("improved_contract", contract_text)
        
        logger.info("✅ Full workflow completed")
        return workflow_result
    
    def get_document_list(self) -> List[Dict]:
        """List all documents uploaded in this session."""
        return self.session_documents.copy()
    
    def get_session_info(self) -> Dict:
        """Get information about current session."""
        return {
            "total_documents": len(self.session_documents),
            "documents_by_type": {
                "policy": len([d for d in self.session_documents if d["doc_type"] == "policy"]),
                "vendor": len([d for d in self.session_documents if d["doc_type"] == "vendor"]),
                "compliance": len([d for d in self.session_documents if d["doc_type"] == "compliance"])
            },
            "uploaded_files": [doc["filename"] for doc in self.session_documents],
            "storage_type": "ephemeral (in-memory)",
            "persistence": "session-only"
        }
    
    def clear_session(self):
        """Clear all uploaded documents from current session."""
        # Reset collections
        self.client.delete_collection("procurement_policies")
        self.client.delete_collection("vendor_information")
        self.client.delete_collection("compliance_docs")
        
        # Recreate collections
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.embedding_model_name
        )
        
        self.policy_collection = self.client.get_or_create_collection(
            name="procurement_policies",
            embedding_function=embedding_fn
        )
        self.vendor_collection = self.client.get_or_create_collection(
            name="vendor_information",
            embedding_function=embedding_fn
        )
        self.compliance_collection = self.client.get_or_create_collection(
            name="compliance_docs",
            embedding_function=embedding_fn
        )
        
        # Clear session documents
        self.session_documents = []
        
        logger.info("🗑️  Session cleared - all documents removed")


# ----------------------------
# Example Usage
# ----------------------------
if __name__ == "__main__":
    # Initialize with ephemeral storage
    rag = ProcurementRAG()
    
    print("\n" + "="*70)
    print("SESSION-BASED PROCUREMENT RAG SYSTEM")
    print("="*70)
    print("\n⚡ Using ephemeral (in-memory) storage")
    print("💡 All data cleared when session ends\n")
    
    # Example: Upload policies for this session
    print("📤 UPLOAD POLICIES FOR THIS SESSION")
    print("-"*70)
    
    # Note: Replace with your actual PDF files
    sample_policies = [
        "data/policies/procurement_policy.pdf",
        "data/policies/vendor_guidelines.pdf"
    ]
    
    for policy_file in sample_policies:
        if Path(policy_file).exists():
            try:
                result = rag.store_document(policy_file, doc_type="policy")
                print(f"✅ Uploaded: {policy_file} ({result['chunks']} chunks)")
            except Exception as e:
                print(f"⚠️  Could not upload {policy_file}: {e}")
        else:
            print(f"⚠️  File not found: {policy_file}")
    
    # Show session info
    print("\n📊 SESSION INFORMATION")
    print("-"*70)
    session_info = rag.get_session_info()
    print(json.dumps(session_info, indent=2))
    
    # Example: Check compliance against uploaded policies only
    if rag.session_documents:
        print("\n🔍 COMPLIANCE CHECK (using uploaded policies only)")
        print("-"*70)
        
        sample_contract = """
        SERVICE AGREEMENT
        Between ABC Corp and XYZ Services
        Services: IT consulting
        Payment: $100,000 annually
        Term: 1 year
        """
        
        result = rag.check_compliance(sample_contract, "service")
        if result["status"] == "success":
            print(f"✅ Compliance check completed")
            print(f"📚 Checked against: {', '.join(result['uploaded_docs'])}")
            print(f"\n{result['analysis'][:500]}...")
        else:
            print(f"❌ {result['error']}")
    
    print("\n" + "="*70)
    print("💡 TIP: When you restart the application, all data is cleared.")
    print("    You must re-upload policies for each session.")
    print("="*70)
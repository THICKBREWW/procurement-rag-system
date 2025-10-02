"""
Complete Usage Examples for Procurement RAG System
Run this file to see all features in action
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from app.rag_engine import ProcurementRAG


def print_section(title):
    """Print section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def example_1_initialize_system():
    """Example 1: Initialize and check system"""
    print_section("EXAMPLE 1: Initialize System")
    
    # Initialize RAG system
    rag = ProcurementRAG()
    print("System initialized successfully")
    
    # Check stored documents
    docs = rag.get_document_list()
    print(f"Total documents stored: {len(docs)}")
    
    for doc in docs:
        print(f"  - {doc['filename']} ({doc['collection']})")
    
    return rag


def example_2_upload_policy(rag):
    """Example 2: Upload a policy document"""
    print_section("EXAMPLE 2: Upload Policy Document")
    
    # Note: You need to have a PDF file in data/policies/
    policy_path = "data/policies/sample_policy.pdf"
    
    if not Path(policy_path).exists():
        print(f"Sample policy not found at {policy_path}")
        print("   Please add a PDF file to data/policies/ directory")
        return
    
    try:
        result = rag.store_document(
            policy_path,
            doc_type="policy",
            custom_metadata={
                "version": "2.1",
                "department": "Procurement",
                "effective_date": "2024-01-01"
            }
        )
        
        print(f"✅ Policy uploaded successfully!")
        print(f"   - File: {policy_path}")
        print(f"   - Type: {result['doc_type']}")
        print(f"   - Chunks: {result['chunks']}")
        print(f"   - Hash: {result['doc_hash'][:16]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_3_search_policies(rag):
    """Example 3: Search for relevant policies"""
    print_section("EXAMPLE 3: Search Policies")
    
    queries = [
        "procurement approval process",
        "vendor selection criteria",
        "contract payment terms"
    ]
    
    for query in queries:
        print(f"🔍 Query: '{query}'")
        results = rag.search(query, top_k=3)
        
        print(f"   Found {len(results['results'])} results:\n")
        
        for i, result in enumerate(results['results'], 1):
            print(f"   {i}. Source: {result['metadata'].get('filename', 'Unknown')}")
            print(f"      Collection: {result['collection']}")
            print(f"      Relevance: {1 - result['distance']:.3f}" if result['distance'] else "N/A")
            print(f"      Text: {result['text'][:150]}...\n")


def example_4_check_compliance(rag):
    """Example 4: Check contract compliance"""
    print_section("EXAMPLE 4: Check Compliance")
    
    sample_contract = """
    SERVICE AGREEMENT
    
    This Agreement is entered into on March 1, 2024 between:
    
    BUYER: ABC Corporation, 123 Business Street, City, State 12345
    VENDOR: XYZ Services Ltd., 456 Vendor Avenue, City, State 67890
    
    1. SCOPE OF WORK
    The Vendor shall provide IT consulting services including software development,
    system maintenance, and technical support as requested by the Buyer.
    
    2. PAYMENT TERMS
    Payment will be made within 30 days of invoice receipt. The total contract
    value is $150,000 for the duration of this agreement.
    
    3. TERM
    This agreement is valid for one year from the date of signing and may be
    renewed upon mutual agreement.
    
    4. CONFIDENTIALITY
    Both parties agree to maintain confidentiality of proprietary information
    shared during the course of this agreement.
    """
    
    print("📄 Sample Contract:")
    print(sample_contract[:200] + "...\n")
    
    print("🔍 Running compliance check...")
    
    try:
        result = rag.check_compliance(
            input_text=sample_contract,
            contract_type="service"
        )
        
        if result["status"] == "success":
            print("✅ Compliance check completed!\n")
            print("📊 ANALYSIS:")
            print("-" * 70)
            print(result["analysis"])
            print("-" * 70)
            print(f"\n📈 Policies checked: {result['policies_checked']}")
            print(f"📏 Contract length: {result['contract_length']} characters")
        else:
            print(f"❌ Error: {result.get('error')}")
    
    except Exception as e:
        print(f"❌ Error during compliance check: {e}")


def example_5_missing_clauses(rag):
    """Example 5: Identify missing clauses"""
    print_section("EXAMPLE 5: Missing Clause Analysis")
    
    incomplete_contract = """
    PURCHASE AGREEMENT
    
    Between ABC Corp and XYZ Supplier.
    
    The supplier will deliver 1000 units of Product X.
    Total value: $50,000
    Delivery within 60 days.
    """
    
    print("📄 Incomplete Contract:")
    print(incomplete_contract)
    
    print("\n💡 Analyzing missing clauses...")
    
    try:
        result = rag.suggest_missing_clauses(
            input_text=incomplete_contract,
            contract_type="procurement"
        )
        
        if result["status"] == "success":
            print("✅ Analysis completed!\n")
            print("📋 SUGGESTIONS:")
            print("-" * 70)
            print(result["suggestions"])
            print("-" * 70)
            print(f"\n📚 Policies referenced: {result['policies_referenced']}")
        else:
            print(f"❌ Error: {result.get('error')}")
    
    except Exception as e:
        print(f"❌ Error during analysis: {e}")


def example_6_generate_contract(rag):
    """Example 6: Generate complete contract"""
    print_section("EXAMPLE 6: Generate Complete Contract")
    
    contract_params = {
        "parties": {
            "buyer": {
                "name": "TechCorp Industries Inc.",
                "address": "789 Innovation Drive, Tech City, TC 12345",
                "contact": "John Smith, Procurement Director",
                "email": "john.smith@techcorp.com",
                "phone": "+1-555-0123"
            },
            "vendor": {
                "name": "CloudServices Global Ltd.",
                "address": "321 Service Boulevard, Cloud Town, CT 67890",
                "contact": "Jane Doe, Sales Manager",
                "email": "jane.doe@cloudservices.com",
                "phone": "+1-555-0456"
            }
        },
        "scope": """Provision of comprehensive cloud infrastructure services including:
        - 24/7 server monitoring and maintenance
        - Database management and optimization
        - Security updates and patch management
        - Technical support and incident response
        - Monthly performance reporting and analytics""",
        "value": "$250,000 USD annually",
        "duration": "2 years with option to extend for one additional year",
        "start_date": "2024-04-01",
        "delivery_date": "2024-04-15",
        "payment_terms": "Monthly invoicing, payment due within 30 days of invoice date",
        "special_terms": [
            "Service Level Agreement: 99.9% uptime guarantee",
            "Response time: 2 hours for critical issues, 8 hours for standard issues",
            "Quarterly business reviews required",
            "Data backup and disaster recovery included",
            "Dedicated account manager assigned"
        ],
        "deliverables": [
            "Monthly performance and uptime reports",
            "Quarterly security audit reports",
            "Incident response documentation",
            "Annual infrastructure optimization recommendations"
        ]
    }
    
    print("📝 Contract Parameters:")
    print(json.dumps(contract_params, indent=2)[:500] + "...\n")
    
    print("🚀 Generating contract... (this may take 30-60 seconds)")
    
    try:
        result = rag.generate_contract(
            contract_params=contract_params,
            contract_type="service",
            include_optional_clauses=True
        )
        
        if result["status"] == "success":
            print("✅ Contract generated successfully!\n")
            
            print("📊 STATISTICS:")
            print(f"   - Word count: {result['word_count']}")
            print(f"   - Contract type: {result['contract_type']}")
            print(f"   - Policies referenced: {result['policies_referenced']}")
            
            print("\n📄 GENERATED CONTRACT:")
            print("=" * 70)
            print(result["contract"][:1000] + "\n...\n[Contract continues...]")
            print("=" * 70)
            
            # Save to file
            output_file = f"generated_contract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(output_file, 'w') as f:
                f.write(result["contract"])
            print(f"\n💾 Full contract saved to: {output_file}")
            
            # Show compliance check
            if result.get("compliance_check"):
                print("\n🔍 BUILT-IN COMPLIANCE CHECK:")
                print(result["compliance_check"]["analysis"][:500] + "...")
        else:
            print(f"❌ Error: {result.get('error')}")
    
    except Exception as e:
        print(f"❌ Error during generation: {e}")


def example_7_full_workflow(rag):
    """Example 7: Complete workflow"""
    print_section("EXAMPLE 7: Full Contract Workflow")
    
    draft_contract = """
    CONSULTING SERVICES AGREEMENT
    
    Between: DataTech Solutions (Client)
    And: Analytics Pro Consulting (Consultant)
    
    Services: Data analytics and business intelligence consulting
    
    Fee: $80,000 for 6 months
    
    Start Date: May 1, 2024
    """
    
    print("📄 Initial Draft:")
    print(draft_contract)
    
    print("\n🚀 Starting full workflow...")
    print("   This will: Check compliance → Identify issues → Generate improved version\n")
    
    try:
        result = rag.full_contract_workflow(
            initial_draft=draft_contract,
            contract_type="consulting"
        )
        
        if result["status"] == "success":
            print("✅ Workflow completed successfully!\n")
            
            print("📊 WORKFLOW STEPS:")
            for i, step in enumerate(result["steps"], 1):
                print(f"   {i}. {step['step'].replace('_', ' ').title()}: {step['status']}")
            
            if "improved_contract" in result:
                print("\n✨ IMPROVED CONTRACT GENERATED!")
                print("=" * 70)
                print(result["final_contract"][:800] + "\n...\n[Contract continues...]")
                print("=" * 70)
                
                # Save improved version
                output_file = f"improved_contract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(output_file, 'w') as f:
                    f.write(result["final_contract"])
                print(f"\n💾 Improved contract saved to: {output_file}")
            else:
                print("\n✅ Original contract was compliant - no improvements needed!")
        else:
            print(f"❌ Error: {result.get('error')}")
    
    except Exception as e:
        print(f"❌ Error during workflow: {e}")


def example_8_batch_operations(rag):
    """Example 8: Batch processing"""
    print_section("EXAMPLE 8: Batch Operations")
    
    contracts = [
        {
            "name": "Contract A - Software License",
            "type": "software",
            "text": "Software license for 100 users. Annual fee $10,000."
        },
        {
            "name": "Contract B - Maintenance Service", 
            "type": "service",
            "text": "Annual maintenance service for equipment. Fee: $5,000."
        },
        {
            "name": "Contract C - Office Supplies",
            "type": "procurement",
            "text": "Purchase of office supplies worth $2,000."
        }
    ]
    
    print(f"📋 Processing {len(contracts)} contracts...\n")
    
    results = []
    for i, contract in enumerate(contracts, 1):
        print(f"{i}. {contract['name']}")
        try:
            result = rag.check_compliance(
                input_text=contract["text"],
                contract_type=contract["type"]
            )
            results.append({
                "name": contract["name"],
                "status": result["status"],
                "summary": result["analysis"][:200] + "..." if result["status"] == "success" else result.get("error")
            })
            print(f"   ✅ Processed")
        except Exception as e:
            results.append({
                "name": contract["name"],
                "status": "error",
                "summary": str(e)
            })
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 BATCH RESULTS:")
    print("=" * 70)
    for result in results:
        print(f"\n{result['name']}: {result['status'].upper()}")
        print(f"   {result['summary'][:150]}...")


def example_9_document_management(rag):
    """Example 9: Document management operations"""
    print_section("EXAMPLE 9: Document Management")
    
    print("Current Document Inventory:")
    docs = rag.get_document_list()
    
    if not docs:
        print("   No documents stored yet")
        return
    
    # Group by collection
    by_collection = {}
    for doc in docs:
        coll = doc['collection']
        if coll not in by_collection:
            by_collection[coll] = []
        by_collection[coll].append(doc)
    
    for collection, collection_docs in by_collection.items():
        print(f"\n{collection.upper()} ({len(collection_docs)} documents):")
        for doc in collection_docs:
            print(f"   - {doc['filename']}")
            print(f"     Pages: {doc['page_count']}, Hash: {doc['doc_hash'][:12]}...")
    
    print(f"\nTotal: {len(docs)} documents across {len(by_collection)} collections")


def example_10_api_integration():
    """Example 10: API integration examples"""
    print_section("EXAMPLE 10: API Integration Examples")
    
    print("REST API Endpoints:\n")
    
    examples = {
        "Health Check": "curl http://localhost:5000/health",
        "Upload Policy": """curl -X POST http://localhost:5000/api/upload-policy \\
  -F "file=@policy.pdf" \\
  -F "doc_type=policy" \\
  -F "version=2.0" """,
        "Check Compliance": """curl -X POST http://localhost:5000/api/check-compliance \\
  -H "Content-Type: application/json" \\
  -d '{
    "contract_text": "Your contract here...",
    "contract_type": "service"
  }'""",
        "Generate Contract": """curl -X POST http://localhost:5000/api/generate-contract \\
  -H "Content-Type: application/json" \\
  -d '{
    "parameters": {
      "parties": {...},
      "scope": "Service description",
      "value": "$100,000"
    },
    "contract_type": "service"
  }'""",
        "List Documents": "curl http://localhost:5000/api/list-documents"
    }
    
    for title, command in examples.items():
        print(f"{title}:")
        print(f"   {command}\n")
    
    print("Full API documentation: http://localhost:5000/api/docs")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("  PROCUREMENT RAG SYSTEM - COMPLETE USAGE EXAMPLES")
    print("="*70)
    
    try:
        # Example 1: Initialize
        rag = example_1_initialize_system()
        
        # Example 2: Upload (commented out - requires actual PDF)
        # example_2_upload_policy(rag)
        
        # Example 3: Search
        if len(rag.get_document_list()) > 0:
            example_3_search_policies(rag)
        else:
            print("\nSkipping search example - no documents stored")
        
        # Example 4: Compliance check
        if len(rag.get_document_list()) > 0:
            example_4_check_compliance(rag)
        else:
            print("\nSkipping compliance check - no policies to check against")
        
        # Example 5: Missing clauses
        if len(rag.get_document_list()) > 0:
            example_5_missing_clauses(rag)
        else:
            print("\nSkipping missing clause analysis - no policies loaded")
        
        # Example 6: Generate contract
        if len(rag.get_document_list()) > 0:
            example_6_generate_contract(rag)
        else:
            print("\nSkipping contract generation - no policies loaded")
        
        # Example 7: Full workflow
        if len(rag.get_document_list()) > 0:
            example_7_full_workflow(rag)
        else:
            print("\nSkipping workflow - no policies loaded")
        
        # Example 8: Batch operations
        if len(rag.get_document_list()) > 0:
            example_8_batch_operations(rag)
        else:
            print("\nSkipping batch operations - no policies loaded")
        
        # Example 9: Document management
        example_9_document_management(rag)
        
        # Example 10: API examples
        example_10_api_integration()
        
        # Summary
        print_section("EXAMPLES COMPLETED")
        print("Next steps:")
        print("   1. Upload your policy PDFs to data/policies/")
        print("   2. Run: python scripts/import_policies.py")
        print("   3. Start Streamlit UI: streamlit run app/streamlit_app.py")
        print("   4. Start Flask API: python app/api.py")
        print("\nFor more info, see README.md")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
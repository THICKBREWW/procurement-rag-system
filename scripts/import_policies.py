#!/usr/bin/env python3
"""
Bulk import script for policy documents
Uploads all PDF files from data/policies/ directory to the RAG system
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag_engine import ProcurementRAG
from app.utils.logger import get_system_logger

logger = get_system_logger()

def import_policies():
    """Import all policy documents from data/policies/ directory"""
    logger.info("Starting bulk policy import...")
    
    # Initialize RAG system
    rag = ProcurementRAG()
    
    # Get policies directory
    policies_dir = Path("data/policies")
    
    if not policies_dir.exists():
        logger.error(f"Policies directory not found: {policies_dir}")
        print(f"Error: Policies directory not found: {policies_dir}")
        print("   Please create the directory and add PDF files to import")
        return
    
    # Find all PDF files
    pdf_files = list(policies_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("No PDF files found in policies directory")
        print("No PDF files found in data/policies/")
        print("   Please add PDF files to the directory and try again")
        return
    
    print(f"Found {len(pdf_files)} PDF files to import")
    logger.info(f"Found {len(pdf_files)} PDF files to import")
    
    # Import each file
    successful_imports = 0
    failed_imports = 0
    results = []
    
    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")
        
        try:
            # Determine document type based on filename
            filename_lower = pdf_file.name.lower()
            if "vendor" in filename_lower or "supplier" in filename_lower:
                doc_type = "vendor"
            elif "compliance" in filename_lower or "regulation" in filename_lower:
                doc_type = "compliance"
            else:
                doc_type = "policy"
            
            # Prepare metadata
            custom_metadata = {
                "imported_via": "bulk_import",
                "import_timestamp": datetime.now().isoformat(),
                "original_filename": pdf_file.name
            }
            
            # Store document
            result = rag.store_document(
                str(pdf_file),
                doc_type=doc_type,
                custom_metadata=custom_metadata
            )
            
            print(f"   Successfully imported ({result['chunks']} chunks)")
            logger.info(f"Successfully imported {pdf_file.name}: {result['chunks']} chunks")
            
            successful_imports += 1
            results.append({
                "filename": pdf_file.name,
                "status": "success",
                "doc_type": result['doc_type'],
                "chunks": result['chunks'],
                "doc_hash": result['doc_hash']
            })
            
        except Exception as e:
            print(f"   Failed to import: {e}")
            logger.error(f"Failed to import {pdf_file.name}: {e}")
            
            failed_imports += 1
            results.append({
                "filename": pdf_file.name,
                "status": "error",
                "error": str(e)
            })
    
    # Summary
    print(f"\nImport Summary:")
    print(f"   Successful: {successful_imports}")
    print(f"   Failed: {failed_imports}")
    print(f"   Total: {len(pdf_files)}")
    
    # Save results to file
    results_file = f"import_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"   Results saved to: {results_file}")
    
    # Show current document count
    docs = rag.get_document_list()
    print(f"\nTotal documents in system: {len(docs)}")
    
    logger.info(f"Bulk import completed: {successful_imports} successful, {failed_imports} failed")

def main():
    """Main function"""
    print("Procurement RAG System - Bulk Policy Import")
    print("=" * 50)
    
    try:
        import_policies()
    except Exception as e:
        print(f"\nFatal error: {e}")
        logger.error(f"Fatal error in bulk import: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

"""
Basic tests for the Procurement RAG System
"""

import sys
from pathlib import Path
import unittest

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.rag_engine import ProcurementRAG
from app.utils.validators import validate_contract_input

class TestBasicFunctionality(unittest.TestCase):
    """Basic functionality tests"""
    
    def test_rag_initialization(self):
        """Test RAG system initialization"""
        rag = ProcurementRAG()
        self.assertIsNotNone(rag)
        self.assertIsNotNone(rag.client)
    
    def test_document_list(self):
        """Test document list retrieval"""
        rag = ProcurementRAG()
        docs = rag.get_document_list()
        self.assertIsInstance(docs, list)
    
    def test_search_functionality(self):
        """Test search functionality"""
        rag = ProcurementRAG()
        results = rag.search("test query", top_k=5)
        self.assertIsInstance(results, dict)
        self.assertIn("results", results)
        self.assertIsInstance(results["results"], list)
    
    def test_validation(self):
        """Test input validation"""
        test_contract = "This is a test contract with sufficient content."
        result = validate_contract_input(test_contract, "service")
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)

if __name__ == "__main__":
    unittest.main()


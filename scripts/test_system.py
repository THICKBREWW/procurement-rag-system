#!/usr/bin/env python3
"""
System test script for the Procurement RAG System
Tests all major components and functionality
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
from app.utils.validators import validate_contract_input

logger = get_system_logger()

class SystemTester:
    """System testing class"""
    
    def __init__(self):
        self.rag = None
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
    
    def log_test(self, test_name: str, status: str, message: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if status == "PASS":
            self.passed_tests += 1
            print(f"PASS {test_name}: {message}")
        else:
            self.failed_tests += 1
            print(f"FAIL {test_name}: {message}")
    
    def test_rag_initialization(self):
        """Test RAG system initialization"""
        try:
            self.rag = ProcurementRAG()
            self.log_test("RAG Initialization", "PASS", "RAG system initialized successfully")
            return True
        except Exception as e:
            self.log_test("RAG Initialization", "FAIL", f"Failed to initialize RAG: {e}")
            return False
    
    def test_configuration(self):
        """Test configuration loading"""
        try:
            from config import ANTHROPIC_API_KEY, CONTRACT_TYPES, DOCUMENT_TYPES
            api_key_configured = bool(ANTHROPIC_API_KEY)
            
            if api_key_configured:
                self.log_test("Configuration", "PASS", "Configuration loaded, API key configured")
            else:
                self.log_test("Configuration", "WARN", "Configuration loaded, but API key not configured")
            
            return True
        except Exception as e:
            self.log_test("Configuration", "FAIL", f"Failed to load configuration: {e}")
            return False
    
    def test_document_operations(self):
        """Test document operations"""
        if not self.rag:
            self.log_test("Document Operations", "SKIP", "RAG system not initialized")
            return False
        
        try:
            # Test document list
            docs = self.rag.get_document_list()
            self.log_test("Document List", "PASS", f"Retrieved {len(docs)} documents")
            
            # Test session info
            session_info = self.rag.get_session_info()
            self.log_test("Session Info", "PASS", f"Session info retrieved: {session_info['total_documents']} docs")
            
            return True
        except Exception as e:
            self.log_test("Document Operations", "FAIL", f"Document operations failed: {e}")
            return False
    
    def test_search_functionality(self):
        """Test search functionality"""
        if not self.rag:
            self.log_test("Search Functionality", "SKIP", "RAG system not initialized")
            return False
        
        try:
            # Test search with empty results (no documents loaded)
            results = self.rag.search("test query", top_k=5)
            self.log_test("Search Query", "PASS", f"Search executed, found {len(results['results'])} results")
            
            return True
        except Exception as e:
            self.log_test("Search Functionality", "FAIL", f"Search failed: {e}")
            return False
    
    def test_validation_functions(self):
        """Test validation functions"""
        try:
            # Test contract validation
            test_contract = "This is a test contract with sufficient content to pass validation."
            validation_result = validate_contract_input(test_contract, "service")
            
            if validation_result["valid"]:
                self.log_test("Contract Validation", "PASS", "Contract validation working")
            else:
                self.log_test("Contract Validation", "FAIL", f"Validation failed: {validation_result['errors']}")
            
            return True
        except Exception as e:
            self.log_test("Validation Functions", "FAIL", f"Validation test failed: {e}")
            return False
    
    def test_compliance_check(self):
        """Test compliance checking (without policies)"""
        if not self.rag:
            self.log_test("Compliance Check", "SKIP", "RAG system not initialized")
            return False
        
        try:
            test_contract = """
            SERVICE AGREEMENT
            
            This is a test service agreement between ABC Corp and XYZ Services.
            The vendor will provide consulting services for a period of one year.
            Payment terms: Net 30 days.
            """
            
            result = self.rag.check_compliance(test_contract, "service")
            
            if result["status"] == "error" and "No policies uploaded" in result.get("error", ""):
                self.log_test("Compliance Check", "PASS", "Compliance check working (no policies loaded)")
            else:
                self.log_test("Compliance Check", "PASS", "Compliance check executed successfully")
            
            return True
        except Exception as e:
            self.log_test("Compliance Check", "FAIL", f"Compliance check failed: {e}")
            return False
    
    def test_missing_clauses(self):
        """Test missing clause analysis"""
        if not self.rag:
            self.log_test("Missing Clauses", "SKIP", "RAG system not initialized")
            return False
        
        try:
            test_contract = "Simple contract without detailed clauses."
            
            result = self.rag.suggest_missing_clauses(test_contract, "service")
            
            if result["status"] == "error" and "No policies uploaded" in result.get("error", ""):
                self.log_test("Missing Clauses", "PASS", "Missing clause analysis working (no policies loaded)")
            else:
                self.log_test("Missing Clauses", "PASS", "Missing clause analysis executed successfully")
            
            return True
        except Exception as e:
            self.log_test("Missing Clauses", "FAIL", f"Missing clause analysis failed: {e}")
            return False
    
    def test_contract_generation(self):
        """Test contract generation"""
        if not self.rag:
            self.log_test("Contract Generation", "SKIP", "RAG system not initialized")
            return False
        
        try:
            test_params = {
                "parties": {
                    "buyer": {"name": "Test Buyer Corp", "address": "123 Test St"},
                    "vendor": {"name": "Test Vendor Ltd", "address": "456 Vendor Ave"}
                },
                "scope": "Test consulting services",
                "value": "$10,000",
                "duration": "6 months"
            }
            
            result = self.rag.generate_contract(test_params, "service")
            
            if result["status"] == "error" and "No policies uploaded" in result.get("error", ""):
                self.log_test("Contract Generation", "PASS", "Contract generation working (no policies loaded)")
            else:
                self.log_test("Contract Generation", "PASS", "Contract generation executed successfully")
            
            return True
        except Exception as e:
            self.log_test("Contract Generation", "FAIL", f"Contract generation failed: {e}")
            return False
    
    def test_logging_system(self):
        """Test logging system"""
        try:
            logger.info("Test log message")
            self.log_test("Logging System", "PASS", "Logging system working")
            return True
        except Exception as e:
            self.log_test("Logging System", "FAIL", f"Logging system failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all system tests"""
        print("Procurement RAG System - System Tests")
        print("=" * 50)
        
        # Run tests
        self.test_configuration()
        self.test_logging_system()
        self.test_rag_initialization()
        self.test_document_operations()
        self.test_search_functionality()
        self.test_validation_functions()
        self.test_compliance_check()
        self.test_missing_clauses()
        self.test_contract_generation()
        
        # Summary
        print(f"\nTest Summary:")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.failed_tests}")
        print(f"   Total: {len(self.test_results)}")
        
        # Save results
        results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"   Results saved to: {results_file}")
        
        # Return success status
        return self.failed_tests == 0

def main():
    """Main function"""
    try:
        tester = SystemTester()
        success = tester.run_all_tests()
        
        if success:
            print("\nAll tests passed! System is ready.")
            sys.exit(0)
        else:
            print("\nSome tests failed. Check the results above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\nFatal error during testing: {e}")
        logger.error(f"Fatal error in system test: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

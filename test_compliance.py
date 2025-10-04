#!/usr/bin/env python3
"""
Test script to check compliance endpoint
"""
import requests
import json

def test_compliance():
    """Test the compliance check endpoint"""
    url = "http://localhost:5000/api/check-compliance"
    
    # Test data
    test_contract = """
    SERVICE AGREEMENT
    
    This is a test service agreement between ABC Corp and XYZ Services.
    The vendor will provide consulting services for a period of one year.
    Payment terms: Net 30 days.
    """
    
    payload = {
        "contract_text": test_contract,
        "contract_type": "service"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Testing compliance check endpoint...")
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('status')}")
            if result.get('status') == 'error':
                print(f"Error: {result.get('error')}")
        else:
            print(f"HTTP Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to API server. Make sure it's running on localhost:5000")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_compliance()

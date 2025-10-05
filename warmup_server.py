#!/usr/bin/env python3
"""
Warmup script for the Procurement RAG System
This script initializes the RAG system to avoid initialization delays during first requests.
"""

import requests
import time
import sys

def warmup_server(base_url="http://localhost:5000", max_retries=5, retry_delay=10):
    """Warm up the server by calling the warmup endpoint"""
    print("🔥 Starting server warmup...")
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}: Checking server status...")
            
            # First check if server is responding
            health_response = requests.get(f"{base_url}/health", timeout=10)
            if health_response.status_code == 200:
                print("✅ Server is responding")
                
                # Now warm up the RAG system
                print("🧠 Warming up RAG system...")
                warmup_response = requests.post(f"{base_url}/api/warmup", timeout=60)
                
                if warmup_response.status_code == 200:
                    print("✅ RAG system warmed up successfully!")
                    print("🚀 Server is ready for requests")
                    return True
                else:
                    print(f"❌ Warmup failed: {warmup_response.text}")
                    
        except requests.exceptions.ConnectionError:
            print(f"❌ Server not responding (attempt {attempt + 1}/{max_retries})")
        except requests.exceptions.Timeout:
            print(f"⏰ Request timed out (attempt {attempt + 1}/{max_retries})")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        if attempt < max_retries - 1:
            print(f"⏳ Waiting {retry_delay} seconds before retry...")
            time.sleep(retry_delay)
    
    print("❌ Failed to warm up server after all attempts")
    return False

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    success = warmup_server(base_url)
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Procurement RAG System Startup Script
Automatically starts Flask server and Cloudflare tunnel
"""

import subprocess
import time
import re
import threading
import sys
import os
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("=" * 50)
    print("   Procurement RAG System Startup")
    print("=" * 50)
    print()

def start_flask_server():
    """Start Flask API server"""
    print("[1/3] Starting Flask API Server...")
    try:
        # Start Flask server in a separate process
        flask_process = subprocess.Popen(
            [sys.executable, "app/api.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("   ✓ Flask server starting on port 5000")
        return flask_process
    except Exception as e:
        print(f"   ✗ Error starting Flask server: {e}")
        return None

def start_cloudflare_tunnel():
    """Start Cloudflare tunnel and capture URL"""
    print("\n[2/3] Starting Cloudflare Tunnel...")
    print("   🌐 Creating global tunnel...")
    print("   📡 This will provide a global URL for your system")
    print()
    
    try:
        # Start cloudflared tunnel
        tunnel_process = subprocess.Popen(
            ["./cloudflared.exe", "tunnel", "--url", "http://127.0.0.1:5000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        tunnel_url = None
        
        # Monitor output for tunnel URL
        print("   🔍 Waiting for tunnel URL...")
        for line in iter(tunnel_process.stdout.readline, ''):
            if line:
                print(f"   {line.strip()}")
                
                # Look for tunnel URL
                url_match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                if url_match:
                    tunnel_url = url_match.group(0)
                    break
        
        return tunnel_process, tunnel_url
        
    except Exception as e:
        print(f"   ✗ Error starting tunnel: {e}")
        return None, None

def main():
    """Main startup function"""
    print_banner()
    
    # Start Flask server
    flask_process = start_flask_server()
    if not flask_process:
        print("Failed to start Flask server. Exiting.")
        return
    
    # Wait for server to initialize
    print("\n[3/3] Waiting for server to initialize...")
    time.sleep(8)
    print("   ✓ Server initialization complete")
    
    # Start Cloudflare tunnel
    tunnel_process, tunnel_url = start_cloudflare_tunnel()
    
    print("\n" + "=" * 50)
    print("   System Status")
    print("=" * 50)
    print()
    
    print("✅ Flask API Server: Running on localhost:5000")
    if tunnel_process:
        print("✅ Cloudflare Tunnel: Active")
    else:
        print("❌ Cloudflare Tunnel: Failed to start")
    
    print()
    
    if tunnel_url:
        print(f"🌐 Global URL: {tunnel_url}")
        print()
        print("📋 Your system is now accessible globally!")
        print("   Copy the URL above to access from anywhere")
    else:
        print("🌐 Global URL: Check tunnel output for URL")
        print("   Look for a URL ending with .trycloudflare.com")
    
    print()
    print("🔗 Local Access: http://localhost:5000")
    print()
    print("📋 Features Available:")
    print("   • Set API Key")
    print("   • Upload Documents") 
    print("   • Compliance Check")
    print("   • Contract Generation")
    print("   • Grammar Check")
    print()
    
    print("Press Ctrl+C to stop all services...")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping services...")
        if flask_process:
            flask_process.terminate()
        if tunnel_process:
            tunnel_process.terminate()
        print("All services stopped.")

if __name__ == "__main__":
    main()

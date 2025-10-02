#!/usr/bin/env python3
"""
Startup script for the Procurement RAG System
Provides easy access to all system components
"""

import sys
import os
import subprocess
from pathlib import Path
import argparse

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def print_banner():
    """Print system banner"""
    print("=" * 50)
    print("  PROCUREMENT RAG SYSTEM")
    print("  AI-Powered Contract Compliance & Generation")
    print("=" * 50)
    print()

def check_environment():
    """Check if environment is properly configured"""
    print("Checking environment...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("ERROR: Python 3.9+ required")
        return False
    
    # Check for .env file
    if not Path(".env").exists():
        print("WARNING: .env file not found. Copy env.example to .env and configure your API key")
        return False
    
    # Check for API key
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or api_key == "your-api-key-here":
            print("WARNING: ANTHROPIC_API_KEY not configured in .env file")
            return False
    except ImportError:
        print("WARNING: python-dotenv not installed")
        return False
    
    print("SUCCESS: Environment looks good!")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("SUCCESS: Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        return False

def run_streamlit():
    """Run Streamlit UI"""
    print("Starting Streamlit UI...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app/streamlit_app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to start Streamlit: {e}")
    except KeyboardInterrupt:
        print("\nStreamlit stopped")

def run_flask():
    """Run Flask API"""
    print("Starting Flask API...")
    try:
        subprocess.run([sys.executable, "app/api.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to start Flask: {e}")
    except KeyboardInterrupt:
        print("\nFlask API stopped")

def run_tests():
    """Run system tests"""
    print("Running system tests...")
    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path(__file__).parent)
        subprocess.run([sys.executable, "scripts/test_system.py"], check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Tests failed: {e}")

def import_policies():
    """Import policy documents"""
    print("Importing policy documents...")
    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path(__file__).parent)
        subprocess.run([sys.executable, "scripts/import_policies.py"], check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Import failed: {e}")

def run_examples():
    """Run usage examples"""
    print("Running usage examples...")
    try:
        # Set PYTHONPATH to include current directory
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path(__file__).parent)
        subprocess.run([sys.executable, "scripts/example_usage.py"], check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Examples failed: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Procurement RAG System Launcher")
    parser.add_argument("command", nargs="?", default="help", 
                       choices=["help", "install", "check", "ui", "api", "test", "import", "examples"],
                       help="Command to run")
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.command == "help":
        print("Available commands:")
        print("  install   - Install dependencies")
        print("  check     - Check environment configuration")
        print("  ui        - Start Streamlit UI")
        print("  api       - Start Flask API")
        print("  test      - Run system tests")
        print("  import    - Import policy documents")
        print("  examples  - Run usage examples")
        print()
        print("Usage: python run.py <command>")
        return
    
    if args.command == "install":
        install_dependencies()
        return
    
    if args.command == "check":
        check_environment()
        return
    
    if not check_environment():
        print("\nERROR: Environment check failed. Please fix the issues above.")
        return
    
    if args.command == "ui":
        run_streamlit()
    elif args.command == "api":
        run_flask()
    elif args.command == "test":
        run_tests()
    elif args.command == "import":
        import_policies()
    elif args.command == "examples":
        run_examples()

if __name__ == "__main__":
    main()


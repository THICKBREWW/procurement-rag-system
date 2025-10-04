#!/bin/bash

# Procurement RAG System Deployment Script
# This script helps deploy the application in various environments

set -e

echo "🚀 Procurement RAG System Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is required but not installed"
        exit 1
    fi
    
    print_success "System requirements met"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found, skipping dependency installation"
    fi
}

# Setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            cp env.example .env
            print_warning "Created .env file from env.example"
            print_warning "Please edit .env file with your API keys"
        else
            print_warning "No .env file found. You'll need to set ANTHROPIC_API_KEY manually"
        fi
    fi
    
    # Create necessary directories
    mkdir -p logs uploads chroma_db pdf_artifacts
    print_success "Environment setup complete"
}

# Local development deployment
deploy_local() {
    print_status "Deploying for local development..."
    
    check_requirements
    install_dependencies
    setup_environment
    
    print_success "Local deployment ready!"
    echo ""
    echo "To start the application:"
    echo "1. Start the Python backend:"
    echo "   python run.py api"
    echo ""
    echo "2. In another terminal, start the frontend server:"
    echo "   python -m http.server 8000"
    echo ""
    echo "3. Open your browser to: http://localhost:8000"
}

# Production deployment with systemd
deploy_production() {
    print_status "Deploying for production..."
    
    check_requirements
    install_dependencies
    setup_environment
    
    # Create systemd service file
    SERVICE_FILE="/tmp/procurement-api.service"
    cat > $SERVICE_FILE << EOF
[Unit]
Description=Procurement RAG API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(which python3)
ExecStart=$(which python3) run.py api
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    print_status "Created systemd service file: $SERVICE_FILE"
    print_warning "To install the service:"
    echo "sudo cp $SERVICE_FILE /etc/systemd/system/"
    echo "sudo systemctl daemon-reload"
    echo "sudo systemctl enable procurement-api"
    echo "sudo systemctl start procurement-api"
    echo ""
    print_warning "To serve the frontend, configure nginx or apache to serve static files from:"
    echo "$(pwd)"
}

# Docker deployment
deploy_docker() {
    print_status "Deploying with Docker..."
    
    # Create Dockerfile if it doesn't exist
    if [ ! -f "Dockerfile" ]; then
        cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs uploads chroma_db pdf_artifacts

# Expose ports
EXPOSE 5000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start both services
CMD ["sh", "-c", "python -m http.server 8000 & python run.py api"]
EOF
        print_success "Created Dockerfile"
    fi
    
    # Build Docker image
    print_status "Building Docker image..."
    docker build -t procurement-rag-app .
    
    print_success "Docker image built successfully!"
    echo ""
    echo "To run the container:"
    echo "docker run -p 8000:8000 -p 5000:5000 procurement-rag-app"
    echo ""
    echo "To run with environment variables:"
    echo "docker run -p 8000:8000 -p 5000:5000 -e ANTHROPIC_API_KEY=your-key procurement-rag-app"
}

# Docker Compose deployment
deploy_docker_compose() {
    print_status "Deploying with Docker Compose..."
    
    # Create docker-compose.yml if it doesn't exist
    if [ ! -f "docker-compose.yml" ]; then
        cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  procurement-app:
    build: .
    ports:
      - "8000:8000"  # Frontend
      - "5000:5000"  # Backend API
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - procurement-app
    restart: unless-stopped
EOF

        # Create nginx configuration
        cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server procurement-app:5000;
    }

    server {
        listen 80;
        server_name localhost;

        # Serve static frontend files
        location / {
            proxy_pass http://procurement-app:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Proxy API requests to Python backend
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location /health {
            proxy_pass http://backend;
        }
    }
}
EOF
        print_success "Created docker-compose.yml and nginx.conf"
    fi
    
    print_status "Starting services with Docker Compose..."
    docker-compose up -d
    
    print_success "Services started!"
    echo ""
    echo "Application is available at: http://localhost"
    echo "API is available at: http://localhost/api"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
}

# Show usage information
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  local       Deploy for local development"
    echo "  production  Deploy for production (creates systemd service)"
    echo "  docker      Deploy with Docker"
    echo "  compose     Deploy with Docker Compose (recommended for production)"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 local      # Quick local setup"
    echo "  $0 docker     # Docker deployment"
    echo "  $0 compose    # Production-ready Docker Compose setup"
}

# Main script logic
main() {
    case "${1:-help}" in
        "local")
            deploy_local
            ;;
        "production")
            deploy_production
            ;;
        "docker")
            deploy_docker
            ;;
        "compose")
            deploy_docker_compose
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

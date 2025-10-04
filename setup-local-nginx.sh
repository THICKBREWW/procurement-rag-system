#!/bin/bash

# Local Nginx Setup for iframe embedding
# Removes all security restrictions

set -e

echo "🚀 Setting up local nginx for iframe embedding"
echo "=============================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

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

# Check if nginx is installed
check_nginx() {
    if ! command -v nginx &> /dev/null; then
        print_error "Nginx is not installed. Please install it first:"
        echo ""
        echo "macOS:"
        echo "  brew install nginx"
        echo ""
        echo "Ubuntu/Debian:"
        echo "  sudo apt-get install nginx"
        echo ""
        echo "CentOS/RHEL:"
        echo "  sudo yum install nginx"
        exit 1
    fi
    print_success "Nginx is installed"
}

# Install nginx on macOS
install_nginx_macos() {
    if ! command -v brew &> /dev/null; then
        print_error "Homebrew is not installed. Please install it first:"
        echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    print_status "Installing nginx via Homebrew..."
    brew install nginx
    print_success "Nginx installed"
}

# Install nginx on Ubuntu/Debian
install_nginx_ubuntu() {
    print_status "Installing nginx..."
    sudo apt-get update
    sudo apt-get install -y nginx
    print_success "Nginx installed"
}

# Install nginx on CentOS/RHEL
install_nginx_centos() {
    print_status "Installing nginx..."
    sudo yum install -y nginx
    print_success "Nginx installed"
}

# Detect OS and install nginx if needed
install_nginx() {
    if command -v nginx &> /dev/null; then
        print_success "Nginx is already installed"
        return
    fi
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        install_nginx_macos
    elif [[ -f /etc/debian_version ]]; then
        install_nginx_ubuntu
    elif [[ -f /etc/redhat-release ]]; then
        install_nginx_centos
    else
        print_error "Unsupported operating system. Please install nginx manually."
        exit 1
    fi
}

# Setup nginx configuration
setup_nginx() {
    print_status "Setting up nginx configuration..."
    
    # Backup existing default config
    if [[ -f /etc/nginx/sites-available/default ]]; then
        sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup
        print_status "Backed up existing nginx config"
    fi
    
    # Copy our iframe-friendly config
    sudo cp nginx-iframe.conf /etc/nginx/sites-available/procurement-iframe
    
    # Enable the site
    if [[ -d /etc/nginx/sites-enabled ]]; then
        sudo ln -sf /etc/nginx/sites-available/procurement-iframe /etc/nginx/sites-enabled/
        sudo rm -f /etc/nginx/sites-enabled/default
    else
        # For macOS nginx
        sudo cp nginx-iframe.conf /usr/local/etc/nginx/nginx.conf
    fi
    
    print_success "Nginx configuration set up"
}

# Test nginx configuration
test_nginx() {
    print_status "Testing nginx configuration..."
    if sudo nginx -t; then
        print_success "Nginx configuration is valid"
    else
        print_error "Nginx configuration test failed"
        exit 1
    fi
}

# Start services
start_services() {
    print_status "Starting services..."
    
    # Start Python backend
    print_status "Starting Python backend..."
    python3 run.py api &
    BACKEND_PID=$!
    echo $BACKEND_PID > backend.pid
    print_success "Python backend started (PID: $BACKEND_PID)"
    
    # Wait a moment for backend to start
    sleep 3
    
    # Start nginx
    print_status "Starting nginx..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sudo nginx
    else
        sudo systemctl start nginx
        sudo systemctl enable nginx
    fi
    print_success "Nginx started"
}

# Show status
show_status() {
    echo ""
    print_success "🎉 Setup complete!"
    echo ""
    echo "Services running:"
    echo "  Frontend: http://localhost"
    echo "  Backend API: http://localhost/api"
    echo "  Health Check: http://localhost/health"
    echo ""
    echo "iframe embedding:"
    echo "  <iframe src=\"http://localhost\" width=\"100%\" height=\"600px\"></iframe>"
    echo ""
    echo "To stop services:"
    echo "  ./stop-local.sh"
    echo ""
    echo "To restart:"
    echo "  ./start-local.sh"
}

# Create stop script
create_stop_script() {
    cat > stop-local.sh << 'EOF'
#!/bin/bash
echo "Stopping services..."

# Stop Python backend
if [[ -f backend.pid ]]; then
    PID=$(cat backend.pid)
    kill $PID 2>/dev/null || true
    rm backend.pid
    echo "Python backend stopped"
fi

# Stop nginx
if [[ "$OSTYPE" == "darwin"* ]]; then
    sudo nginx -s stop
else
    sudo systemctl stop nginx
fi
echo "Nginx stopped"
echo "All services stopped"
EOF
    chmod +x stop-local.sh
    print_success "Created stop-local.sh script"
}

# Create start script
create_start_script() {
    cat > start-local.sh << 'EOF'
#!/bin/bash
echo "Starting services..."

# Start Python backend
python3 run.py api &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid
echo "Python backend started (PID: $BACKEND_PID)"

# Start nginx
if [[ "$OSTYPE" == "darwin"* ]]; then
    sudo nginx
else
    sudo systemctl start nginx
fi
echo "Nginx started"
echo "Services running at http://localhost"
EOF
    chmod +x start-local.sh
    print_success "Created start-local.sh script"
}

# Main execution
main() {
    print_status "Setting up local nginx for iframe embedding..."
    
    # Install nginx if needed
    install_nginx
    
    # Setup nginx configuration
    setup_nginx
    
    # Test configuration
    test_nginx
    
    # Create helper scripts
    create_stop_script
    create_start_script
    
    # Start services
    start_services
    
    # Show status
    show_status
}

# Run main function
main "$@"

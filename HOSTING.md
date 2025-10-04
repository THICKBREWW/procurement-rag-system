# 🚀 Procurement RAG System - Hosting Guide

This guide shows you how to host your Procurement Contract Assistant with the new HTML/CSS/JS frontend and Python backend.

## 📋 Quick Start

### Option 1: Local Development (Easiest)
```bash
# Make the deployment script executable
chmod +x deploy.sh

# Deploy for local development
./deploy.sh local

# Then start the services:
# Terminal 1: Start Python backend
python run.py api

# Terminal 2: Start frontend server
python -m http.server 8000

# Open browser to: http://localhost:8000
```

### Option 2: Docker (Recommended for Production)
```bash
# Deploy with Docker Compose (includes nginx)
./deploy.sh compose

# Application will be available at: http://localhost
```

## 🌐 Hosting Options

### 1. **Local Development**
- **Best for**: Testing and development
- **Requirements**: Python 3.9+
- **Access**: `http://localhost:8000`

### 2. **Traditional VPS/Server**
- **Best for**: Small to medium deployments
- **Requirements**: Ubuntu/CentOS server, nginx, gunicorn
- **Steps**:
  ```bash
  ./deploy.sh production
  # Follow the systemd service instructions
  ```

### 3. **Docker Deployment**
- **Best for**: Containerized environments
- **Requirements**: Docker installed
- **Steps**:
  ```bash
  ./deploy.sh docker
  docker run -p 8000:8000 -p 5000:5000 procurement-rag-app
  ```

### 4. **Docker Compose (Recommended)**
- **Best for**: Production deployments
- **Requirements**: Docker and Docker Compose
- **Features**: Includes nginx reverse proxy, health checks, auto-restart
- **Steps**:
  ```bash
  ./deploy.sh compose
  ```

### 5. **Cloud Platforms**

#### **Heroku**
```bash
# Install Heroku CLI
heroku create your-procurement-app
git add .
git commit -m "Deploy procurement app"
git push heroku main
```

#### **DigitalOcean App Platform**
1. Push code to GitHub
2. Connect to DigitalOcean App Platform
3. Configure build settings and environment variables

#### **AWS/GCP/Azure**
- Use container services (ECS, Cloud Run, Container Instances)
- Or serverless options (Lambda, Cloud Functions)

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```env
ANTHROPIC_API_KEY=your-api-key-here
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
```

### API Configuration
The frontend communicates with your Python backend at:
- **Local**: `http://localhost:5000`
- **Production**: Update `CONFIG.API.BASE_URL` in `config.js`

## 📁 File Structure
```
procurement-rag-system/
├── index.html          # Frontend application
├── styles.css          # Styling
├── app.js             # JavaScript application
├── config.js          # Configuration
├── deploy.sh          # Deployment script
├── app/
│   ├── api.py         # Python Flask backend
│   └── rag_engine.py  # RAG system
└── requirements.txt   # Python dependencies
```

## 🔒 Security Considerations

### Production Deployment
1. **Use HTTPS**: Configure SSL certificates
2. **API Key Security**: Store API keys in environment variables
3. **CORS**: Configure CORS properly for your domain
4. **Rate Limiting**: Implement rate limiting on API endpoints
5. **Firewall**: Restrict access to necessary ports only

### Nginx Configuration Example
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Serve frontend
    location / {
        root /path/to/procurement-rag-system;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # Proxy API
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Frontend can't connect to backend**
   - Check if Python backend is running on port 5000
   - Verify CORS settings in Flask app
   - Check firewall settings

2. **API key not working**
   - Ensure `ANTHROPIC_API_KEY` is set in environment
   - Check API key format (should start with `sk-ant-`)
   - Verify API key has sufficient credits

3. **File upload issues**
   - Check file size limits (10MB max)
   - Verify file types (PDF, TXT, DOCX only)
   - Ensure upload directory has write permissions

4. **Performance issues**
   - Use gunicorn with multiple workers for production
   - Enable nginx caching for static files
   - Consider using a CDN for static assets

### Logs
- **Python backend**: Check `logs/api.log`
- **Nginx**: Check `/var/log/nginx/error.log`
- **Docker**: Use `docker-compose logs -f`

## 📞 Support

If you encounter issues:
1. Check the logs first
2. Verify all environment variables are set
3. Ensure all dependencies are installed
4. Check network connectivity between frontend and backend

## 🎯 Next Steps

After successful deployment:
1. **Configure SSL**: Set up HTTPS certificates
2. **Domain Setup**: Point your domain to the server
3. **Monitoring**: Set up application monitoring
4. **Backup**: Implement regular backups of data
5. **Updates**: Plan for regular updates and maintenance

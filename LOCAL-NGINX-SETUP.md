# 🚀 Local Nginx Setup for iframe Embedding

This setup removes ALL security restrictions to allow iframe embedding.

## 📋 Quick Setup Steps

### Step 1: Run the Setup Script
```bash
cd /Users/alferix/Documents/Projects/procurement-rag-system
./setup-local-nginx.sh
```

### Step 2: Access Your Application
- **Frontend**: http://localhost
- **API**: http://localhost/api
- **Health Check**: http://localhost/health

### Step 3: Embed in iframe
```html
<iframe src="http://localhost" width="100%" height="600px" frameborder="0"></iframe>
```

## 🔧 Manual Setup (if script fails)

### 1. Install Nginx

**macOS:**
```bash
brew install nginx
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install nginx
```

**CentOS/RHEL:**
```bash
sudo yum install nginx
```

### 2. Configure Nginx

**macOS:**
```bash
sudo cp nginx-iframe.conf /usr/local/etc/nginx/nginx.conf
```

**Linux:**
```bash
sudo cp nginx-iframe.conf /etc/nginx/sites-available/procurement-iframe
sudo ln -sf /etc/nginx/sites-available/procurement-iframe /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
```

### 3. Test Configuration
```bash
sudo nginx -t
```

### 4. Start Services

**Start Python Backend:**
```bash
python3 run.py api &
```

**Start Nginx:**
```bash
# macOS
sudo nginx

# Linux
sudo systemctl start nginx
sudo systemctl enable nginx
```

## 🛠️ Management Commands

### Start Services
```bash
./start-local.sh
```

### Stop Services
```bash
./stop-local.sh
```

### Restart Services
```bash
./stop-local.sh
./start-local.sh
```

### Check Status
```bash
# Check if services are running
curl http://localhost/health
curl http://localhost/api/status
```

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Kill processes on ports 80 and 5000
sudo lsof -ti:80 | xargs kill -9
sudo lsof -ti:5000 | xargs kill -9
```

### Nginx Permission Issues
```bash
# macOS
sudo chown -R $(whoami) /usr/local/var/log/nginx
sudo chown -R $(whoami) /usr/local/etc/nginx

# Linux
sudo chown -R www-data:www-data /var/log/nginx
sudo chown -R www-data:www-data /etc/nginx
```

### Python Backend Issues
```bash
# Check if backend is running
ps aux | grep python

# Kill backend process
pkill -f "run.py api"

# Restart backend
python3 run.py api &
```

## 📁 File Structure After Setup

```
procurement-rag-system/
├── index.html              # Frontend
├── styles.css              # Styles
├── app.js                  # JavaScript
├── config.js               # Configuration (updated for nginx)
├── nginx-iframe.conf       # Nginx config (no security restrictions)
├── setup-local-nginx.sh    # Setup script
├── start-local.sh          # Start services
├── stop-local.sh           # Stop services
├── backend.pid             # Backend process ID
└── app/
    ├── api.py              # Flask API (CORS disabled)
    └── rag_engine.py       # RAG system
```

## 🌐 iframe Usage Examples

### Basic iframe
```html
<iframe src="http://localhost" width="100%" height="600px"></iframe>
```

### Responsive iframe
```html
<div style="position: relative; width: 100%; height: 0; padding-bottom: 56.25%;">
    <iframe src="http://localhost" 
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
            frameborder="0">
    </iframe>
</div>
```

### Full-screen iframe
```html
<iframe src="http://localhost" 
        width="100%" 
        height="100vh" 
        frameborder="0"
        style="border: none;">
</iframe>
```

## ⚠️ Security Notes

This setup removes ALL security restrictions:
- ✅ CORS disabled
- ✅ X-Frame-Options removed
- ✅ XSS protection disabled
- ✅ Content-Type sniffing allowed
- ✅ All origins allowed

**Use only for local development and testing!**

## 🎯 Next Steps

1. **Test the setup**: Visit http://localhost
2. **Embed in iframe**: Use the examples above
3. **Configure API key**: Set your Anthropic API key in the interface
4. **Upload policies**: Add your policy documents
5. **Test functionality**: Try all features (compliance, generation, etc.)

## 📞 Support

If you encounter issues:
1. Check if nginx is running: `sudo nginx -t`
2. Check if Python backend is running: `curl http://localhost/api/status`
3. Check logs: `tail -f logs/api.log`
4. Restart services: `./stop-local.sh && ./start-local.sh`

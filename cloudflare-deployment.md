# 🌐 Cloudflare Deployment Guide

## 🚀 Quick Deploy

### Option 1: Windows
```bash
.\deploy-cloudflare.bat
```

### Option 2: Linux/Mac
```bash
chmod +x deploy-cloudflare.sh
./deploy-cloudflare.sh
```

## 📋 Prerequisites

1. **Node.js** - Install from [nodejs.org](https://nodejs.org/)
2. **Python 3.8+** - Already installed
3. **Cloudflare Account** - Sign up at [cloudflare.com](https://cloudflare.com)

## 🔧 Manual Setup

### 1. Install Wrangler CLI
```bash
npm install -g wrangler
```

### 2. Login to Cloudflare
```bash
wrangler login
```

### 3. Install Dependencies
```bash
pip install -r requirements-cloudflare.txt
```

### 4. Deploy
```bash
wrangler deploy
```

## 🌍 Environment Variables

Set these in your Cloudflare dashboard:

- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `ENVIRONMENT` - Set to "production"
- `CHROMA_PERSIST_DIR` - Set to "/tmp/chroma"

## 📁 File Structure

```
├── wrangler.toml          # Cloudflare configuration
├── app/worker.py          # Cloudflare Worker entry point
├── requirements-cloudflare.txt  # Production dependencies
├── deploy-cloudflare.bat  # Windows deployment script
├── deploy-cloudflare.sh   # Linux/Mac deployment script
└── cloudflare-deployment.md  # This guide
```

## 🎯 Features

- ✅ **Serverless** - No server management needed
- ✅ **Global CDN** - Fast worldwide access
- ✅ **Auto-scaling** - Handles traffic spikes
- ✅ **HTTPS** - Secure by default
- ✅ **DDoS Protection** - Built-in security

## 🔧 Configuration

The `wrangler.toml` file contains:
- **App Name**: procurement-rag-system
- **Main File**: app/worker.py
- **Compatibility Date**: 2024-10-05
- **Environment**: production

## 📊 Monitoring

After deployment, monitor your app:
1. **Cloudflare Dashboard** - View analytics
2. **Workers Analytics** - Monitor performance
3. **Logs** - Check for errors

## 🚨 Troubleshooting

### Common Issues:

1. **Wrangler not found**
   ```bash
   npm install -g wrangler
   ```

2. **Authentication failed**
   ```bash
   wrangler login
   ```

3. **Deployment failed**
   - Check your Cloudflare account
   - Verify API key permissions
   - Check wrangler.toml configuration

## 🎉 Success!

Once deployed, your Procurement RAG System will be available at:
`https://your-app-name.your-subdomain.workers.dev`

## 📞 Support

- **Cloudflare Docs**: [developers.cloudflare.com](https://developers.cloudflare.com)
- **Wrangler CLI**: [developers.cloudflare.com/workers/wrangler](https://developers.cloudflare.com/workers/wrangler)

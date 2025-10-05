# 🌐 Cloudflare Tunnel Setup Guide

## 🚀 Quick Start

### Option 1: Automatic Setup
```bash
.\start-tunnel.bat
```

### Option 2: Manual Setup
```bash
# 1. Install cloudflared
.\install-cloudflared.bat

# 2. Login to Cloudflare
cloudflared tunnel login

# 3. Start tunnel
cloudflared tunnel --url http://127.0.0.1:5000
```

## 📋 Prerequisites

1. **Cloudflare Account** - Sign up at [cloudflare.com](https://cloudflare.com)
2. **Local API Running** - Make sure `python app/api.py` is running on port 5000

## 🔧 Step-by-Step Setup

### 1. Install Cloudflared
```bash
.\install-cloudflared.bat
```

### 2. Login to Cloudflare
```bash
cloudflared tunnel login
```
- This will open your browser
- Login to your Cloudflare account
- Authorize the tunnel

### 3. Start the Tunnel
```bash
cloudflared tunnel --url http://127.0.0.1:5000
```

## 🌍 What You'll Get

- ✅ **Public URL** - Your local app will be accessible worldwide
- ✅ **HTTPS** - Secure connection automatically
- ✅ **No Port Forwarding** - No router configuration needed
- ✅ **Free** - No cost for basic usage

## 📊 Example Output

```
2024-10-05T14:30:00Z INF |  Your tunnel is running at: https://abc123.trycloudflare.com
2024-10-05T14:30:00Z INF |  Traffic is being tunneled to: http://127.0.0.1:5000
```

## 🎯 Usage

1. **Start your API server:**
   ```bash
   python app/api.py
   ```

2. **Start the tunnel:**
   ```bash
   .\start-tunnel.bat
   ```

3. **Share the public URL** with others!

## 🔧 Troubleshooting

### Common Issues:

1. **"cloudflared not found"**
   - Run `.\install-cloudflared.bat` first

2. **"Login required"**
   - Run `cloudflared tunnel login`

3. **"Connection refused"**
   - Make sure your API server is running on port 5000

4. **"Port already in use"**
   - Check if another service is using port 5000
   - Use a different port: `cloudflared tunnel --url http://127.0.0.1:8080`

## 🎉 Benefits

- 🌐 **Global Access** - Share your local app with anyone
- 🔒 **Secure** - HTTPS encryption
- 🚀 **Fast** - Cloudflare's global network
- 💰 **Free** - No cost for basic usage
- 🛠️ **Easy** - No complex setup required

## 📞 Support

- **Cloudflare Docs**: [developers.cloudflare.com/cloudflare-one/connections/connect-apps](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps)
- **Cloudflared GitHub**: [github.com/cloudflare/cloudflared](https://github.com/cloudflare/cloudflared)

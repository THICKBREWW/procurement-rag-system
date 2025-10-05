#!/bin/bash

echo "🚀 Deploying Procurement RAG System to Cloudflare"
echo "================================================"

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "❌ Wrangler CLI not found. Installing..."
    npm install -g wrangler
fi

# Login to Cloudflare (if not already logged in)
echo "🔐 Logging into Cloudflare..."
wrangler login

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements-cloudflare.txt

# Deploy to Cloudflare Workers
echo "🌐 Deploying to Cloudflare Workers..."
wrangler deploy

echo "✅ Deployment complete!"
echo "🌍 Your application is now live on Cloudflare!"
echo "📋 Check your Cloudflare dashboard for the URL"

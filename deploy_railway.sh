#!/bin/bash

# Railway Deployment Script
# Automates the deployment process

echo "╔══════════════════════════════════════════════════════════╗"
echo "║       🚂 Railway Deployment Script                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found"
    echo ""
    echo "Install it with:"
    echo "  npm install -g @railway/cli"
    echo ""
    echo "Or visit: https://railway.app"
    exit 1
fi

echo "✅ Railway CLI found"
echo ""

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway..."
    railway login
    echo ""
fi

echo "✅ Logged in to Railway"
echo ""

# Check if project exists
if [ ! -f ".railway" ]; then
    echo "🆕 Initializing new Railway project..."
    railway init
    echo ""
fi

# Set environment variables
echo "🔑 Setting environment variables..."
echo ""

# Read from .env file
if [ -f ".env" ]; then
    echo "Reading from .env file..."
    
    # Extract values (simplified - you may need to adjust)
    NVIDIA_KEY=$(grep NVIDIA_API_KEY .env | cut -d '=' -f2)
    OPENROUTER_KEY=$(grep OPENROUTER_API_KEY .env | cut -d '=' -f2)
    GOOGLE_KEY=$(grep GOOGLE_API_KEY .env | cut -d '=' -f2)
    GOOGLE_CSE=$(grep GOOGLE_CSE_ID .env | cut -d '=' -f2)
    
    if [ ! -z "$OPENROUTER_KEY" ]; then
        railway variables set OPENROUTER_API_KEY="$OPENROUTER_KEY"
        echo "  ✅ OPENROUTER_API_KEY set"
    fi
    
    if [ ! -z "$GOOGLE_KEY" ]; then
        railway variables set GOOGLE_API_KEY="$GOOGLE_KEY"
        echo "  ✅ GOOGLE_API_KEY set"
    fi
    
    if [ ! -z "$GOOGLE_CSE" ]; then
        railway variables set GOOGLE_CSE_ID="$GOOGLE_CSE"
        echo "  ✅ GOOGLE_CSE_ID set"
    fi
    
    railway variables set OPENROUTER_SITE_URL="https://myrealtrip.com"
    railway variables set OPENROUTER_APP_NAME="MRT Tech Test Generator"
    echo "  ✅ OpenRouter attribution set"
    echo ""
else
    echo "⚠️  .env file not found. Set variables manually:"
    echo "  railway variables set OPENROUTER_API_KEY=..."
    echo "  railway variables set GOOGLE_API_KEY=..."
    echo "  railway variables set GOOGLE_CSE_ID=..."
    echo ""
fi

# Deploy
echo "🚀 Deploying to Railway..."
echo ""
railway up

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Deployment Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🌐 Get your app URL:"
echo "   railway domain"
echo ""
echo "📊 View in browser:"
echo "   railway open"
echo ""
echo "📋 Check logs:"
echo "   railway logs"
echo ""
echo "🎊 Your tech test generator is now LIVE online! 🎊"
echo ""


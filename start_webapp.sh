#!/bin/bash

# Tech Test Generator Web App Startup Script

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     🚀 Tech Test Generator Web Application              ║"
echo "╔══════════════════════════════════════════════════════════╗"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📥 Installing Flask..."
    pip install flask
fi

# Check .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Please create .env with your API keys."
    echo "   See .env.example for reference."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create output directory
mkdir -p output

echo ""
echo "══════════════════════════════════════════════════════════"
echo "✅ Starting Flask server..."
echo "══════════════════════════════════════════════════════════"
echo ""
echo "📍 Web UI: http://localhost:8080"
echo "🎨 Design: Myrealtrip branding with warm neutrals"
echo "🤖 AI: NVIDIA minimax-m2 with fallback"
echo "🔍 Research: Google Custom Search Engine"
echo ""
echo "⚠️  Note: Using port 8080 (port 5000 is used by macOS AirPlay)"
echo ""
echo "Press Ctrl+C to stop the server"
echo "══════════════════════════════════════════════════════════"
echo ""

# Start the Flask app
python app.py


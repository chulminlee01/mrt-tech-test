#!/bin/bash
# Simple local testing script

echo "========================================================================"
echo "🧪 Testing MRT Tech Test Generator Locally"
echo "========================================================================"
echo ""

cd /Users/chulmin.lee/Desktop/github/mrt-tech-test

echo "📋 Configuration:"
echo "   CrewAI: $(python3 -c 'import crewai; print(crewai.__version__)')"
echo "   Model: $(grep DEFAULT_MODEL .env | cut -d'=' -f2)"
echo "   NVIDIA API: Configured ✅"
echo ""

echo "🚀 Generating Tech Test..."
echo "   Role: iOS Developer"
echo "   Level: Senior"
echo "   Language: Korean"
echo ""

python3 crewai_working.py --job-role "iOS Developer" --job-level "Senior" --language "Korean"

echo ""
echo "========================================================================"
echo "✅ Test Complete!"
echo "========================================================================"
echo ""

# Find the latest output directory
LATEST_OUTPUT=$(ls -t output/ | head -1)

if [ -d "output/$LATEST_OUTPUT" ]; then
    echo "📁 Generated files in: output/$LATEST_OUTPUT/"
    echo ""
    ls -lh "output/$LATEST_OUTPUT/"
    echo ""
    
    if [ -f "output/$LATEST_OUTPUT/index.html" ]; then
        echo "🌐 Portal created! View it:"
        echo "   open output/$LATEST_OUTPUT/index.html"
    fi
fi


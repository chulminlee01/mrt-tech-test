#!/bin/bash
# Startup script for deployment platforms
# Ensures PORT variable is properly set and expanded

# Set default PORT if not provided
export PORT=${PORT:-8080}

echo "========================================================================"
echo "🚀 Starting MRT Tech Test Generator"
echo "========================================================================"
echo "📦 Version: $(cat VERSION 2>/dev/null || echo '2.0.0')"
echo "🔌 Port: $PORT"
echo "========================================================================"

# Start gunicorn with properly expanded PORT
exec gunicorn -w 2 -b "0.0.0.0:${PORT}" app:app --timeout 600 --access-logfile - --error-logfile -


# Dockerfile for Railway Deployment
# Pre-builds all dependencies to avoid build timeouts

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run with gunicorn (using shell form to expand $PORT)
CMD ["sh", "-c", "gunicorn -w 2 -b 0.0.0.0:${PORT:-8080} app:app --timeout 600 --access-logfile - --error-logfile -"]


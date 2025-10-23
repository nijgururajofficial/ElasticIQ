# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY . services/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/services/service-account.json
ENV PYTHONPATH=/app

# Create necessary directories
RUN mkdir -p /tmp/uploads && chmod 777 /tmp/uploads

# Make port 8080 available
EXPOSE 8080

# Start server
CMD exec uvicorn services.api.search_rag:app --host 0.0.0.0 --port ${PORT} --log-level debug --timeout-keep-alive 75 --workers 1 --limit-max-requests 1000
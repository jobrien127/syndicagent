# Use Python 3.12 Alpine image for better security
FROM python:3.12-alpine

# Update packages
RUN apk update && apk upgrade

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    g++ \
    libffi-dev \
    openssl-dev \
    curl \
    musl-dev

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/output

# Expose port for potential web interface
EXPOSE 8080

# Default command (can be overridden)
CMD ["python", "demo.py"]

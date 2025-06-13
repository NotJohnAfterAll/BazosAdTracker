# Multi-stage build for production deployment
# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files first for better caching
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# Stage 2: Production Python image
FROM python:3.11-slim

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_DEBUG=0 \
    PORT=${PORT:-5000} \
    HOST=${HOST:-0.0.0.0}

# Create non-root user for security
RUN groupadd -g 1001 appuser && \
    useradd -r -u 1001 -g appuser appuser

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy built frontend from previous stage to serve as static files
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create necessary directories and set permissions
RUN mkdir -p data logs && \
    chown -R appuser:appuser /app

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create log directory for supervisor  
RUN mkdir -p /var/log/supervisor && \
    chown -R appuser:appuser /var/log/supervisor

# Switch to non-root user
USER appuser

# Health check for Coolify
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/api/health || exit 1

# Expose the port (Coolify will map this automatically)
EXPOSE ${PORT:-5000}

# Use supervisor to manage both Flask app and scheduler
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
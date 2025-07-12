# Multi-stage build for production deployment
# Stage 1: Build frontend
FROM node:18-bullseye AS frontend-builder

WORKDIR /app/frontend

# Copy package files first for better caching
COPY frontend/package*.json ./

# Clean install with proper platform support
RUN npm ci --platform=linux --arch=x64

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

# Install system dependencies (removed supervisor for simplicity)
RUN apt-get update && apt-get install -y \
    curl \
    wget \
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
RUN mkdir -p data logs notifications && \
    chown -R appuser:appuser /app && \
    chmod +x start.sh

# Switch to non-root user
USER appuser

# Health check for Coolify
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/api/health || exit 1

# Expose the port (Coolify will map this automatically)
EXPOSE ${PORT:-5000}

# Use simple shell script to manage both processes
CMD ["./start.sh"]

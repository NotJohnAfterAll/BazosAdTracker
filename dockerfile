# Multi-stage build for production deployment
# Stage 1: Build frontend
FROM node:20-bullseye AS frontend-builder

# Set npm configuration for better dependency resolution
ENV NPM_CONFIG_OPTIONAL=false \
    NPM_CONFIG_FETCH_TIMEOUT=300000 \
    NPM_CONFIG_FETCH_RETRIES=3

WORKDIR /app/frontend

# Copy package files and npm config
COPY frontend/package*.json frontend/.npmrc ./

# Install dependencies with multiple fallback strategies
RUN set -e && \
    echo "Attempting npm install with platform flags..." && \
    (npm ci --platform=linux --arch=x64 --optional=false || \
     echo "First attempt failed, trying without platform flags..." && \
     npm ci --optional=false || \
     echo "CI failed, trying regular install..." && \
     rm -f package-lock.json && \
     npm install --platform=linux --arch=x64 --optional=false || \
     echo "Platform install failed, trying without optional deps..." && \
     npm install --no-optional || \
     echo "Final attempt with force..." && \
     npm install --force)

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
    HOST=${HOST:-0.0.0.0} \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN groupadd -g 1001 appuser && \
    useradd -r -u 1001 -g appuser appuser

# Set work directory
WORKDIR /app

# Install system dependencies (including PostgreSQL client libraries)
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    libpq-dev \
    gcc \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python -c "import psycopg2; print('✅ PostgreSQL support installed')" || \
    (echo "❌ PostgreSQL support installation failed" && exit 1)

# Copy application code and test PostgreSQL setup
COPY . .
RUN python test_postgres.py || \
    (echo "❌ PostgreSQL connectivity test failed" && exit 1)

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

# Multi-stage build for production deployment
# Stage 1: Build frontend
FROM node:18-alp    --keepalive ${GUNICORN_KEEPALIVE:-60} \\\n\ne AS frontend-builder

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
    && apt-get install wget \
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

# Create a startup script for production with proper error handling
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Starting Bazos Ad Tracker in production mode..."\n\
\n\
# Ensure data directory exists and has proper permissions\n\
mkdir -p /app/data /app/logs\n\
\n\
# Start scheduler in background\n\
echo "Starting scheduler process..."\n\
python scheduler.py &\n\
SCHEDULER_PID=$!\n\
\n\
# Function to handle shutdown\n\
cleanup() {\n\
    echo "Received shutdown signal, cleaning up..."\n\
    if kill -0 $SCHEDULER_PID 2>/dev/null; then\n\
        echo "Stopping scheduler process..."\n\
        kill -TERM $SCHEDULER_PID\n\
        wait $SCHEDULER_PID\n\
    fi\n\
    exit 0\n\
}\n\
\n\
# Set up signal handlers\n\
trap cleanup SIGTERM SIGINT\n\
\n\
# Give scheduler time to start\n\
sleep 2\n\
\n\
# Start web application\n\
echo "Starting web application with Gunicorn..."\n\
exec python -m gunicorn \\\n\
    --bind ${HOST:-0.0.0.0}:${PORT:-5000} \\\n\
    --workers ${GUNICORN_WORKERS:-2} \\\n\    --timeout ${GUNICORN_TIMEOUT:-120} \\\n\
    --keep-alive ${GUNICORN_KEEPALIVE:-60} \\\n\
    --max-requests ${GUNICORN_MAX_REQUESTS:-1000} \\\n\
    --max-requests-jitter 100 \\\n\
    --preload \\\n\
    --access-logfile - \\\n\
    --error-logfile - \\\n\
    --log-level info \\\n\
    --pythonpath . \\\n\
    app:app\n\
' > /app/start.sh && chmod +x /app/start.sh

# Switch to non-root user
USER appuser

# Health check for Coolify
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/api/health || exit 1

# Expose the port (Coolify will map this automatically)
EXPOSE ${PORT:-5000}

# Production startup command with both scheduler and web app
CMD ["/app/start.sh"]
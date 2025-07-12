#!/bin/bash
set -e

echo "Starting BazosChecker with PostgreSQL support..."

# Setup PostgreSQL support first
echo "Setting up PostgreSQL support..."
python setup_postgres.py || echo "PostgreSQL setup encountered issues, will attempt fallback"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Test PostgreSQL connectivity
echo "Testing PostgreSQL connectivity..."
python test_postgres.py || echo "PostgreSQL test failed - check logs above"

# Initialize database
echo "Initializing database..."
python init_db.py

# Set up data directory with proper permissions
echo "📁 Setting up data directory..."
mkdir -p data logs notifications
chmod 755 data

# Build frontend if in development or if dist doesn't exist
if [ ! -d "frontend/dist" ] || [ "$NODE_ENV" = "development" ]; then
    echo "🏗️ Building frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
fi

# Set default environment variables
export FLASK_ENV=${FLASK_ENV:-production}
export FLASK_DEBUG=${FLASK_DEBUG:-false}
export PORT=${PORT:-5000}
export HOST=${HOST:-0.0.0.0}

# Generate secret keys if not provided
if [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    echo "✅ Generated SECRET_KEY"
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    export JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    echo "✅ Generated JWT_SECRET_KEY"
fi

echo "🔧 Environment configured:"
echo "   - FLASK_ENV: $FLASK_ENV"
echo "   - PORT: $PORT"
echo "   - HOST: $HOST"
echo "   - DATABASE_URL: ${DATABASE_URL:-'SQLite (development)'}"

# Function to handle cleanup on exit
cleanup() {
    echo "🛑 Shutting down processes..."
    kill $SCHEDULER_PID $FLASK_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start scheduler in background (only in production)
if [ "$FLASK_ENV" = "production" ]; then
    echo "Starting scheduler with PostgreSQL support..."
    python run_scheduler.py 2>&1 | tee logs/scheduler.log &
    SCHEDULER_PID=$!
    echo "Scheduler started with PID: $SCHEDULER_PID"
fi

# Wait a moment for scheduler to initialize
sleep 2

# Start Flask app in background
echo "Starting Flask app with PostgreSQL support..."
python run_app.py 2>&1 | tee logs/flask.log &
FLASK_PID=$!
echo "Flask app started with PID: $FLASK_PID"

# Wait for both processes and restart if they crash
while true; do
    # Check if scheduler is still running
    if ! kill -0 $SCHEDULER_PID 2>/dev/null; then
        echo "Scheduler crashed, restarting..."
        python run_scheduler.py 2>&1 | tee logs/scheduler.log &
        SCHEDULER_PID=$!
        echo "Scheduler restarted with PID: $SCHEDULER_PID"
    fi
    
    # Check if Flask app is still running
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo "Flask app crashed, restarting..."
        python run_app.py 2>&1 | tee logs/flask.log &
        FLASK_PID=$!
        echo "Flask app restarted with PID: $FLASK_PID"
    fi
    
    # Wait before next check
    sleep 10
done

#!/bin/bash

# Simple process manager for Flask app and scheduler
# Alternative to supervisor that's even more Docker-friendly

echo "🚀 Starting BazosChecker production processes..."

# Create necessary directories
mkdir -p data logs notifications

# Function to handle cleanup on exit
cleanup() {
    echo "🛑 Shutting down processes..."
    kill $SCHEDULER_PID $FLASK_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start scheduler in background
echo "📅 Starting scheduler..."
python scheduler.py > logs/scheduler.log 2>&1 &
SCHEDULER_PID=$!
echo "Scheduler started with PID: $SCHEDULER_PID"

# Wait a moment for scheduler to initialize
sleep 2

# Start Flask app in background
echo "🌐 Starting Flask app..."
python app.py > logs/flask.log 2>&1 &
FLASK_PID=$!
echo "Flask app started with PID: $FLASK_PID"

# Wait for both processes and restart if they crash
while true; do
    # Check if scheduler is still running
    if ! kill -0 $SCHEDULER_PID 2>/dev/null; then
        echo "⚠️ Scheduler crashed, restarting..."
        python scheduler.py > logs/scheduler.log 2>&1 &
        SCHEDULER_PID=$!
        echo "Scheduler restarted with PID: $SCHEDULER_PID"
    fi
    
    # Check if Flask app is still running
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo "⚠️ Flask app crashed, restarting..."
        python app.py > logs/flask.log 2>&1 &
        FLASK_PID=$!
        echo "Flask app restarted with PID: $FLASK_PID"
    fi
    
    # Wait before next check
    sleep 10
done

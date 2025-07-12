#!/bin/bash

# BazosChecker Deployment Script for Coolify
# This script sets up the application with user authentication

echo "🚀 Starting BazosChecker deployment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python init_db.py

# Build frontend
echo "🏗️ Building frontend..."
cd frontend

# Clean install to avoid platform issues
echo "📦 Installing frontend dependencies..."
rm -rf node_modules package-lock.json

# Multiple fallback strategies for npm install
echo "Attempting npm install with fallback strategies..."
if npm install --platform=linux --arch=x64 --optional=false; then
    echo "✅ npm install succeeded with platform flags"
elif npm install --no-optional; then
    echo "✅ npm install succeeded without optional dependencies"
elif npm install --force; then
    echo "⚠️ npm install succeeded with --force flag"
else
    echo "❌ All npm install attempts failed"
    exit 1
fi

echo "🔨 Building frontend assets..."
npm run build

cd ..

# Set up data directory
echo "📁 Setting up data directory..."
mkdir -p data
chmod 755 data

# Set environment variables for production
echo "🔧 Configuring environment..."
export FLASK_ENV=production
export FLASK_DEBUG=false

# Generate secret keys if not set
if [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
    echo "Generated SECRET_KEY"
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    export JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
    echo "Generated JWT_SECRET_KEY"
fi

# Start the application
echo "✅ Deployment complete!"
echo "🌐 Starting application..."

# Use Gunicorn for production
if command -v gunicorn &> /dev/null; then
    echo "🚀 Starting with Gunicorn..."
    exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app
else
    echo "⚠️ Gunicorn not found, using Flask dev server..."
    exec python app.py
fi

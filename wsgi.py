#!/usr/bin/env python3
"""
Production startup script for BazosChecker with Gunicorn
Use this instead of running app.py directly in production
"""

import os
import sys
from app import app, socketio

# Create the WSGI application
application = app

if __name__ == '__main__':
    # This file should be used with Gunicorn in production
    print("🚨 This file should be run with Gunicorn in production!")
    print("   Use: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 wsgi:application")
    print("   For Socket.IO support: gunicorn --worker-class eventlet -w 1 wsgi:application")
    sys.exit(1)

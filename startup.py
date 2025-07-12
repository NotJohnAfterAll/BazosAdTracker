#!/usr/bin/env python3
"""
Application startup script with PostgreSQL dialect pre-loading
This ensures PostgreSQL support is ready before Flask app initialization
"""

import os
import sys
import logging

def setup_logging():
    """Setup logging before anything else"""
    os.makedirs('data', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data/startup.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def preload_postgresql_support():
    """Pre-load PostgreSQL support before app initialization"""
    logger = setup_logging()
    
    logger.info("Starting BazosChecker with PostgreSQL pre-loading...")
    
    # Check if we need PostgreSQL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.info("No DATABASE_URL set, PostgreSQL pre-loading skipped")
        return True
    
    # Fix URL format if needed
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        os.environ['DATABASE_URL'] = database_url
        logger.info("Fixed DATABASE_URL: postgres:// -> postgresql://")
    
    if 'postgresql' not in database_url.lower():
        logger.info("Non-PostgreSQL database URL, pre-loading skipped")
        return True
    
    logger.info("PostgreSQL URL detected, pre-loading support...")
    
    try:
        # Step 1: Import psycopg2
        import psycopg2
        logger.info(f"psycopg2 loaded: {psycopg2.__version__}")
        
        # Step 2: Import SQLAlchemy
        import sqlalchemy
        logger.info(f"SQLAlchemy loaded: {sqlalchemy.__version__}")
        
        # Step 3: Pre-load PostgreSQL dialect modules
        import sqlalchemy.dialects.postgresql
        import sqlalchemy.dialects.postgresql.psycopg2
        logger.info("PostgreSQL dialect modules loaded")
        
        # Step 4: Register dialect explicitly
        from sqlalchemy.dialects import registry
        registry.register("postgresql", "sqlalchemy.dialects.postgresql", "dialect")
        registry.register("postgresql.psycopg2", "sqlalchemy.dialects.postgresql.psycopg2", "dialect")
        logger.info("PostgreSQL dialect registered")
        
        # Step 5: Test engine creation
        from sqlalchemy import create_engine
        try:
            from sqlalchemy.testing.engines import mock
            test_engine = mock.create_mock_engine(database_url, executor=lambda sql, *_: None)
        except ImportError:
            # Fallback for older SQLAlchemy versions
            test_engine = create_engine(database_url, strategy='mock', executor=lambda sql, *_: None)
        
        logger.info("PostgreSQL engine creation test successful")
        
        logger.info("PostgreSQL support pre-loaded successfully!")
        return True
        
    except ImportError as e:
        logger.error(f"PostgreSQL import failed: {e}")
        logger.info("Will attempt fallback to SQLite in main app")
        return False
    except Exception as e:
        logger.error(f"PostgreSQL setup failed: {e}")
        logger.info("Will attempt fallback to SQLite in main app")
        return False

def main():
    """Main startup function"""
    logger = setup_logging()
    
    # Pre-load PostgreSQL support
    postgres_success = preload_postgresql_support()
    
    # Import and start the main Flask app
    logger.info("Starting Flask application...")
    try:
        # Add current directory to Python path to prioritize app.py over app/ directory
        import sys
        if '.' not in sys.path:
            sys.path.insert(0, '.')
        
        # Now we can import from app.py file
        import app as main_app
        
        app = main_app.app
        socketio = main_app.socketio
        
        # Get configuration
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
        
        logger.info(f"Starting server on {host}:{port}")
        logger.info(f"Debug mode: {debug}")
        logger.info(f"PostgreSQL pre-loaded: {postgres_success}")
        
        # Start the server
        socketio.run(app, host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"Failed to start Flask application: {e}")
        logger.error(f"Error details: {type(e).__name__}: {str(e)}")
        # Print more debugging info
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()

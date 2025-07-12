#!/usr/bin/env python3
"""
Simple wrapper to run app.py with PostgreSQL pre-loading
This avoids the module import conflicts
"""

import os
import sys

def setup_postgresql():
    """Setup PostgreSQL support before app import"""
    # Fix DATABASE_URL if needed
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        os.environ['DATABASE_URL'] = database_url
        print("Fixed DATABASE_URL: postgres:// -> postgresql://")
    
    # Pre-load PostgreSQL modules if needed
    if database_url and 'postgresql' in database_url:
        try:
            import psycopg2
            import sqlalchemy.dialects.postgresql
            from sqlalchemy.dialects import registry
            registry.register("postgresql", "sqlalchemy.dialects.postgresql", "dialect")
            registry.register("postgresql.psycopg2", "sqlalchemy.dialects.postgresql.psycopg2", "dialect")
            print("PostgreSQL support pre-loaded successfully")
            return True
        except ImportError as e:
            print(f"Warning: PostgreSQL pre-loading failed: {e}")
            return False
    return True

def main():
    # Setup PostgreSQL first
    setup_postgresql()
    
    # Add current directory to Python path to ensure app.py is found
    if '.' not in sys.path:
        sys.path.insert(0, '.')
    
    # Now import and run the main app
    try:
        # Import the app module directly
        import importlib.util
        spec = importlib.util.spec_from_file_location("main_app", "app.py")
        main_app = importlib.util.module_from_spec(spec)
        sys.modules["main_app"] = main_app
        spec.loader.exec_module(main_app)
        
        print("App module loaded and executed successfully")
        
        # Now manually start the Flask app since __name__ != '__main__'
        # Get port and host from environment variables (Coolify compatibility)
        port = int(os.getenv('PORT', 5000))
        host = os.getenv('HOST', '0.0.0.0')
        
        # Check if we're running in production
        is_production = os.getenv('FLASK_ENV', 'development') == 'production'
        
        print(f"🚀 Starting Bazos Ad Tracker via wrapper...")
        print(f"   Environment: {'Production' if is_production else 'Development'}")
        print(f"   Host: {host}:{port}")
        
        # Get the app instance from the loaded module
        app = main_app.app
        socketio = main_app.socketio
        
        # Clean up old NEW tags on startup
        main_app.cleanup_old_new_tags_on_startup()
        
        print(f"🌐 Starting Flask app on http://{host}:{port}")
        
        # Start the Flask app
        if is_production:
            # Production mode
            socketio.run(
                app, 
                debug=False, 
                host=host, 
                port=port,
                use_reloader=False,
                log_output=False,
                allow_unsafe_werkzeug=True
            )
        else:
            # Development mode
            socketio.run(
                app, 
                debug=True, 
                host=host, 
                port=port,
                use_reloader=False,  # Disable reloader in wrapper
                log_output=True
            )
        
    except Exception as e:
        print(f"Error running app.py: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

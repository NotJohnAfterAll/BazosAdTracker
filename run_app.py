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
        
        # The app.py file should start the server when executed
        print("App module loaded and executed successfully")
        
    except Exception as e:
        print(f"Error running app.py: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

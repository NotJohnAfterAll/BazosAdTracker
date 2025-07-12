#!/usr/bin/env python3
"""
Scheduler wrapper to handle module import conflicts
Similar to run_app.py but for the scheduler
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
            print("PostgreSQL support pre-loaded for scheduler")
            return True
        except ImportError as e:
            print(f"Warning: PostgreSQL pre-loading failed in scheduler: {e}")
            return False
    return True

def main():
    # Setup PostgreSQL first
    setup_postgresql()
    
    # Add current directory to Python path to ensure scheduler.py is found
    if '.' not in sys.path:
        sys.path.insert(0, '.')
    
    # Now import and run the scheduler
    try:
        # Import the scheduler module directly
        import importlib.util
        spec = importlib.util.spec_from_file_location("main_scheduler", "scheduler.py")
        main_scheduler = importlib.util.module_from_spec(spec)
        sys.modules["main_scheduler"] = main_scheduler
        spec.loader.exec_module(main_scheduler)
        
        print("Scheduler module loaded and executed successfully")
        
        # Now manually start the scheduler since __name__ != '__main__'
        scheduler = main_scheduler.AdScheduler()
        try:
            scheduler.run()
        except Exception as e:
            print(f"Fatal error in scheduler: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            # Ensure cleanup happens
            if hasattr(scheduler, 'app_context'):
                scheduler.app_context.pop()
        
    except Exception as e:
        print(f"Error running scheduler.py: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

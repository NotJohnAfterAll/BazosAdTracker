#!/usr/bin/env python3
"""
Pre-install and validate PostgreSQL setup for SQLAlchemy
This script ensures all PostgreSQL dependencies are properly installed and registered
"""

import sys
import subprocess
import os

def ensure_postgresql_support():
    """Ensure PostgreSQL support is properly installed and configured"""
    
    print("🔧 Ensuring PostgreSQL Support")
    print("=" * 35)
    
    # Step 1: Install/upgrade psycopg2-binary
    print("Step 1: Installing PostgreSQL driver...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "psycopg2-binary"])
        print("✅ psycopg2-binary installed/upgraded")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install psycopg2-binary: {e}")
        return False
    
    # Step 2: Test psycopg2 import
    print("\nStep 2: Testing psycopg2 import...")
    try:
        import psycopg2
        print(f"✅ psycopg2 version: {psycopg2.__version__}")
    except ImportError as e:
        print(f"❌ psycopg2 import failed: {e}")
        return False
    
    # Step 3: Install/upgrade SQLAlchemy
    print("\nStep 3: Installing SQLAlchemy...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "sqlalchemy"])
        print("✅ SQLAlchemy installed/upgraded")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install SQLAlchemy: {e}")
        return False
    
    # Step 4: Test SQLAlchemy and PostgreSQL dialect
    print("\nStep 4: Testing SQLAlchemy PostgreSQL dialect...")
    try:
        import sqlalchemy
        from sqlalchemy.dialects import postgresql
        from sqlalchemy.dialects.postgresql import psycopg2 as pg_psycopg2
        print(f"✅ SQLAlchemy version: {sqlalchemy.__version__}")
        print("✅ PostgreSQL dialect imported successfully")
    except ImportError as e:
        print(f"❌ SQLAlchemy PostgreSQL dialect import failed: {e}")
        return False
    
    # Step 5: Test engine creation
    print("\nStep 5: Testing engine creation...")
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.dialects import registry
        
        # Register the dialect explicitly
        registry.register("postgresql", "sqlalchemy.dialects.postgresql", "dialect")
        registry.register("postgresql.psycopg2", "sqlalchemy.dialects.postgresql.psycopg2", "dialect")
        
        # Test engine creation with newer API
        test_url = "postgresql://user:pass@localhost/test"
        try:
            from sqlalchemy.testing.engines import mock
            engine = mock.create_mock_engine(test_url, executor=lambda sql, *_: None)
        except ImportError:
            # Fallback to older API if mock is not available
            engine = create_engine(test_url, strategy='mock', executor=lambda sql, *_: None)
        
        print("✅ PostgreSQL engine creation successful")
    except Exception as e:
        print(f"❌ Engine creation failed: {e}")
        return False
    
    # Step 6: Test with real URL format if provided
    print("\nStep 6: Testing with environment URL...")
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        try:
            # Fix postgres:// to postgresql:// if needed
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
                print("✅ Fixed postgres:// -> postgresql://")
            
            try:
                from sqlalchemy.testing.engines import mock
                engine = mock.create_mock_engine(database_url, executor=lambda sql, *_: None)
            except ImportError:
                # Fallback to older API
                engine = create_engine(database_url, strategy='mock', executor=lambda sql, *_: None)
            
            print("✅ Environment URL validation successful")
        except Exception as e:
            print(f"⚠️ Environment URL test failed: {e}")
            print("This might be normal if DATABASE_URL is not properly formatted")
    else:
        print("⚠️ DATABASE_URL not set - skipping URL validation")
    
    print("\n✅ PostgreSQL support validation complete!")
    return True

if __name__ == "__main__":
    success = ensure_postgresql_support()
    if success:
        print("\n🎉 All PostgreSQL dependencies are properly installed and configured!")
        sys.exit(0)
    else:
        print("\n❌ PostgreSQL setup failed. Check the errors above.")
        sys.exit(1)

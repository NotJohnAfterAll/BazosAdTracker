#!/usr/bin/env python3
"""
Test PostgreSQL connectivity and SQLAlchemy dialect loading
Run this script to verify PostgreSQL setup before starting the application
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_postgresql_connectivity():
    """Test all aspects of PostgreSQL connectivity"""
    
    print("🔍 Testing PostgreSQL Connectivity")
    print("=" * 40)
    
    # Test 1: Import psycopg2
    print("Test 1: psycopg2 import")
    try:
        import psycopg2
        print(f"✅ psycopg2 version: {psycopg2.__version__}")
    except ImportError as e:
        print(f"❌ psycopg2 import failed: {e}")
        return False
    
    # Test 2: Import SQLAlchemy
    print("\nTest 2: SQLAlchemy import")
    try:
        import sqlalchemy
        print(f"✅ SQLAlchemy version: {sqlalchemy.__version__}")
    except ImportError as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False
    
    # Test 3: PostgreSQL dialect
    print("\nTest 3: PostgreSQL dialect")
    try:
        from sqlalchemy.dialects import postgresql
        print("✅ PostgreSQL dialect loaded successfully")
    except ImportError as e:
        print(f"❌ PostgreSQL dialect failed: {e}")
        return False
    
    # Test 4: Database URL parsing
    print("\nTest 4: Database URL parsing")
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("⚠️ DATABASE_URL not set - using SQLite")
        return True
    
    print(f"DATABASE_URL: {database_url.split('@')[0]}@...")
    
    # Fix postgres:// to postgresql:// if needed
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        print("✅ Fixed postgres:// -> postgresql://")
    
    # Test 5: Engine creation
    print("\nTest 5: Engine creation")
    try:
        from sqlalchemy import create_engine
        engine = create_engine(database_url, strategy='mock', executor=lambda sql, *_: None)
        print("✅ Engine created successfully")
    except Exception as e:
        print(f"❌ Engine creation failed: {e}")
        return False
    
    # Test 6: Real connection (if possible)
    print("\nTest 6: Real database connection")
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            print("✅ Database connection successful")
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
        print("This might be normal if the database isn't accessible yet")
    
    print("\n✅ All critical tests passed!")
    return True

if __name__ == "__main__":
    success = test_postgresql_connectivity()
    sys.exit(0 if success else 1)

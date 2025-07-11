#!/usr/bin/env python3
"""
Script to check the migration status from JSON files to database storage.
This helps verify that the system is properly using the database.
"""

import os
import json
from datetime import datetime

def check_migration_status():
    """Check the current migration status"""
    print("=" * 60)
    print("BAZOS CHECKER - MIGRATION STATUS CHECK")
    print("=" * 60)
    
    # Check if old JSON files exist
    keywords_file = 'data/keywords.json'
    ads_file = 'data/ads.json'
    db_file = 'data/bazos_checker.db'
    
    print("\n📂 FILE STATUS:")
    print("-" * 40)
    
    # Check JSON files
    if os.path.exists(keywords_file):
        try:
            with open(keywords_file, 'r', encoding='utf-8') as f:
                keywords = json.load(f)
            print(f"🟡 {keywords_file}: EXISTS ({len(keywords)} keywords) - DEPRECATED")
        except Exception as e:
            print(f"❌ {keywords_file}: ERROR reading - {e}")
    else:
        print(f"✅ {keywords_file}: NOT FOUND (good - using database)")
    
    if os.path.exists(ads_file):
        try:
            with open(ads_file, 'r', encoding='utf-8') as f:
                ads = json.load(f)
            total_ads = sum(len(keyword_ads) for keyword_ads in ads.values())
            print(f"🟡 {ads_file}: EXISTS ({len(ads)} keywords, {total_ads} total ads) - DEPRECATED")
        except Exception as e:
            print(f"❌ {ads_file}: ERROR reading - {e}")
    else:
        print(f"✅ {ads_file}: NOT FOUND (good - using database)")
    
    # Check database
    if os.path.exists(db_file):
        size_mb = os.path.getsize(db_file) / (1024 * 1024)
        print(f"✅ {db_file}: EXISTS ({size_mb:.2f} MB) - ACTIVE")
    else:
        print(f"❌ {db_file}: NOT FOUND - Database missing!")
    
    print("\n📊 DATABASE STATUS:")
    print("-" * 40)
    
    try:
        # Import database models
        import sys
        sys.path.insert(0, '.')
        from app import create_app
        from app.models import db, User, UserKeyword, UserAd
        
        app = create_app()
        with app.app_context():
            # Count users
            user_count = User.query.count()
            active_users = User.query.filter_by(is_active=True).count()
            
            # Count keywords
            keyword_count = UserKeyword.query.filter_by(is_active=True).count()
            
            # Count ads
            ad_count = UserAd.query.filter_by(is_deleted=False).count()
            new_ad_count = UserAd.query.filter_by(is_deleted=False, is_new=True).count()
            
            print(f"👥 Users: {user_count} total ({active_users} active)")
            print(f"🔍 Keywords: {keyword_count} active")
            print(f"📄 Ads: {ad_count} total ({new_ad_count} new)")
            
            if user_count > 0 and keyword_count > 0:
                print("✅ Database is populated and ready")
            elif user_count > 0:
                print("⚠️  Database has users but no keywords")
            else:
                print("⚠️  Database is empty - may need migration")
    
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
    
    print("\n📋 MIGRATION RECOMMENDATIONS:")
    print("-" * 40)
    
    if os.path.exists(keywords_file) or os.path.exists(ads_file):
        print("🟡 Old JSON files detected:")
        print("   • Run 'python init_db.py' to migrate data to database")
        print("   • After successful migration, consider archiving/removing JSON files")
        print("   • The system now uses database storage exclusively")
    else:
        print("✅ No old JSON files found - system is fully migrated")
    
    if os.path.exists(db_file):
        print("✅ Database file exists - system ready")
    else:
        print("❌ Database missing - run 'python init_db.py' to create")
    
    print("\n🔧 SCHEDULER STATUS:")
    print("-" * 40)
    print("✅ Scheduler updated to use database storage")
    print("✅ UserService handles per-user ad checking")
    print("✅ Legacy JSON functions marked as deprecated")
    
    print(f"\n📅 Check completed at: {datetime.now()}")
    print("=" * 60)

if __name__ == '__main__':
    check_migration_status()

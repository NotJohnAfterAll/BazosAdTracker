#!/usr/bin/env python3
"""
Debug script to help diagnose API issues in production
This script can be used to test API endpoints and file access in production environment
"""

import json
import os
import sys
from datetime import datetime

def debug_file_access():
    """Debug file access and data loading"""
    print("=== FILE ACCESS DEBUG ===")
    
    # Check working directory
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[0]}")
    
    # Check if data directory exists
    data_dir = "data"
    print(f"Data directory exists: {os.path.exists(data_dir)}")
    
    if os.path.exists(data_dir):
        print(f"Data directory contents: {os.listdir(data_dir)}")
    
    # Check specific files
    files_to_check = ["data/keywords.json", "data/ads.json", "data/stats.json"]
    
    for file_path in files_to_check:
        exists = os.path.exists(file_path)
        print(f"{file_path} exists: {exists}")
        
        if exists:
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                    if file_path == "data/ads.json":
                        total_ads = sum(len(ad_list) for ad_list in data.values()) if isinstance(data, dict) else 0
                        print(f"  -> {len(data)} keyword groups, {total_ads} total ads")
                    elif file_path == "data/keywords.json":
                        print(f"  -> {len(data)} keywords: {data}")
                    else:
                        print(f"  -> File readable, contains: {type(data).__name__}")
            except Exception as e:
                print(f"  -> Error reading file: {e}")

def debug_flask_globals():
    """Debug Flask application globals"""
    print("\n=== FLASK GLOBALS DEBUG ===")
    
    try:
        # Import and check Flask app globals
        from app import all_ads, keywords, stats
        
        print(f"Keywords in memory: {keywords}")
        print(f"Number of keyword groups in all_ads: {len(all_ads)}")
        
        if all_ads:
            total_ads = sum(len(ad_list) for ad_list in all_ads.values())
            print(f"Total ads in memory: {total_ads}")
            print(f"Keywords with ads: {list(all_ads.keys())}")
        else:
            print("No ads in memory!")
            
        # Check stats
        print(f"Stats object: {type(stats)}")
        
    except ImportError as e:
        print(f"Cannot import Flask app: {e}")
    except Exception as e:
        print(f"Error checking Flask globals: {e}")

def debug_api_response():
    """Simulate API responses"""
    print("\n=== API RESPONSE DEBUG ===")
    
    try:
        # Load data directly like the API would
        if os.path.exists("data/ads.json"):
            with open("data/ads.json", 'r', encoding='utf-8-sig') as f:
                all_ads = json.load(f)
            
            # Simulate recent-ads API
            all_recent_ads = []
            seen_ad_ids = set()
            
            for keyword, ads in all_ads.items():
                for ad in ads[:5]:  # Get 5 most recent ads per keyword
                    if ad['id'] not in seen_ad_ids:
                        seen_ad_ids.add(ad['id'])
                        all_recent_ads.append({
                            'keyword': keyword,
                            'ad': ad
                        })
            
            print(f"Recent ads API would return: {len(all_recent_ads)} ads")
            
            # Simulate specific keyword API
            if 'cdj' in all_ads:
                cdj_ads = all_ads['cdj']
                print(f"CDJ keyword API would return: {len(cdj_ads)} ads")
            
        else:
            print("ads.json file not found!")
            
    except Exception as e:
        print(f"Error simulating API: {e}")

def debug_environment():
    """Debug environment variables"""
    print("\n=== ENVIRONMENT DEBUG ===")
    
    important_vars = [
        'FLASK_ENV', 'FLASK_DEBUG', 'PORT', 'HOST',
        'PYTHONPATH', 'PATH', 'HOME', 'USER'
    ]
    
    for var in important_vars:
        value = os.environ.get(var, 'NOT SET')
        print(f"{var}: {value}")

def create_test_data():
    """Create minimal test data if files are missing"""
    print("\n=== CREATING TEST DATA ===")
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Create test keywords if missing
    if not os.path.exists("data/keywords.json"):
        test_keywords = ["test", "debug"]
        with open("data/keywords.json", 'w', encoding='utf-8') as f:
            json.dump(test_keywords, f, ensure_ascii=False)
        print("Created test keywords.json")
    
    # Create test ads if missing
    if not os.path.exists("data/ads.json"):
        test_ads = {
            "test": [
                {
                    "id": "debug001",
                    "title": "Debug Test Ad",
                    "link": "https://example.com/debug",
                    "price": "100 Kč",
                    "date_added": "12.6. 2025",
                    "description": "This is a test ad for debugging",
                    "image_url": "https://via.placeholder.com/300x200",
                    "scraped_at": datetime.now().timestamp(),
                    "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "seller_name": "Debug User"
                }
            ]
        }
        with open("data/ads.json", 'w', encoding='utf-8') as f:
            json.dump(test_ads, f, ensure_ascii=False)
        print("Created test ads.json")
    
    # Create test stats if missing
    if not os.path.exists("data/stats.json"):
        test_stats = {
            "checks": {"total": 1, "last_check": datetime.now().isoformat(), "avg_duration_ms": 1000},
            "ads": {"total_found": 1, "total_deleted": 0},
            "system": {"start_time": datetime.now().isoformat()}
        }
        with open("data/stats.json", 'w', encoding='utf-8') as f:
            json.dump(test_stats, f, ensure_ascii=False)
        print("Created test stats.json")

if __name__ == "__main__":
    print("BazosChecker Production Debug Tool")
    print("=" * 50)
    
    debug_environment()
    debug_file_access()
    
    # Try to create test data if needed
    if not os.path.exists("data/ads.json"):
        create_test_data()
        debug_file_access()  # Check again
    
    debug_flask_globals()
    debug_api_response()
    
    print("\n=== DEBUG COMPLETE ===")

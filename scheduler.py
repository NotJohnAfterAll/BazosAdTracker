#!/usr/bin/env python3
"""
Separate scheduler process for production deployment.
This runs independently of the Gunicorn web workers to avoid conflicts.
"""

import os
import sys
import time
import json
import signal
import logging
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.utils.bazos_scraper_fixed import BazosScraper
from utils.stats_tracker import StatsTracker

# Import database models and services
import sys
import importlib.util
spec = importlib.util.spec_from_file_location("main_app", os.path.join(os.path.dirname(__file__), "app.py"))
main_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_app)

from app.models import db, User, UserKeyword, UserAd, UserFavorite
from app.user_service import UserService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SCHEDULER - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AdScheduler:
    def __init__(self):
        self.running = True
        self.scraper = BazosScraper()
        self.stats = StatsTracker()
        self.check_interval = int(os.getenv('CHECK_INTERVAL', 300))  # Default 5 minutes
        
        # Initialize Flask app and database context
        self.app = main_app.create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Initialize user service for database operations
        self.user_service = UserService(scraper=self.scraper)
        
        # Data files (stats file still used for system-wide stats)
        # DEPRECATED: keywords_file and ads_file - now using database
        self.keywords_file = 'data/keywords.json'  # Only for migration/legacy support
        self.ads_file = 'data/ads.json'  # Only for migration/legacy support
        self.stats_file = 'data/stats.json'
        
        # Ensure data directory exists with proper permissions
        os.makedirs('data', exist_ok=True)
        
        # Test stats file access immediately
        self.test_stats_file_access()
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        logger.info(f"Scheduler initialized with {self.check_interval}s interval")

    def test_stats_file_access(self):
        """Test if we can read and write to the stats file"""
        try:
            logger.info("🔍 Testing stats file access...")
            
            # Test read access
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8-sig') as f:
                    stats_data = json.load(f)
                logger.info(f"✅ Stats file read successful. Current total checks: {stats_data.get('checks', {}).get('total', 0)}")
            else:
                logger.info("Stats file doesn't exist yet - will be created")
            
            # Test write access by recording a test event
            test_start_time = time.time()
            self.stats.record_system_start()
            test_duration = int((time.time() - test_start_time) * 1000)
            logger.info(f"✅ Stats write test successful (took {test_duration}ms)")
            
            # Verify the write by reading back
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8-sig') as f:
                    updated_stats = json.load(f)
                logger.info(f"✅ Stats write verification successful. Restarts: {updated_stats.get('system', {}).get('restarts', 0)}")
            
        except Exception as e:
            logger.error(f"❌ Stats file access test failed: {e}")
            logger.error(f"Stats file path: {os.path.abspath(self.stats_file)}")
            logger.error(f"Data directory exists: {os.path.exists('data')}")
            logger.error(f"Data directory permissions: {oct(os.stat('data').st_mode)[-3:] if os.path.exists('data') else 'N/A'}")

    def safe_record_check(self, duration_ms):
        """Safely record check with enhanced error handling"""
        try:
            logger.info(f"🔧 Recording check with duration: {duration_ms}ms")
            
            # Force reload stats from file to get latest data from other processes
            self.stats.reload_stats_from_file()
            
            # Get current stats before update
            current_total = self.stats.stats.get("checks", {}).get("total", 0)
            
            # Record the check
            self.stats.record_check(duration_ms)
            
            # Verify the update
            new_total = self.stats.stats.get("checks", {}).get("total", 0)
            
            if new_total > current_total:
                logger.info(f"✅ Check recorded successfully. Total checks: {current_total} → {new_total}")
                
                # Double-check by reading from file
                try:
                    with open(self.stats_file, 'r', encoding='utf-8-sig') as f:
                        file_stats = json.load(f)
                    file_total = file_stats.get("checks", {}).get("total", 0)
                    if file_total == new_total:
                        logger.info(f"✅ Stats file verification successful. File shows {file_total} checks")
                    else:
                        logger.warning(f"⚠️  Stats file mismatch. Memory: {new_total}, File: {file_total}")
                except Exception as e:
                    logger.error(f"❌ Failed to verify stats file after check recording: {e}")
            else:
                logger.error(f"❌ Check recording failed. Total unchanged: {current_total}")
                
        except Exception as e:
            logger.error(f"❌ Failed to record check: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

    def safe_record_ads_found(self, keyword, count):
        """Safely record ads found with enhanced error handling"""
        try:
            logger.info(f"📊 Recording {count} ads found for keyword '{keyword}'")
            
            # Force reload stats from file to get latest data from other processes
            self.stats.reload_stats_from_file()
            
            # Get current stats before update
            current_total = self.stats.stats.get("ads", {}).get("total_found", 0)
            current_keyword_stats = self.stats.stats.get("ads", {}).get("by_keyword", {}).get(keyword, {})
            current_keyword_found = current_keyword_stats.get("found", 0)
            
            # Record the ads
            self.stats.record_ads_found(keyword, count)
            
            # Verify the update
            new_total = self.stats.stats.get("ads", {}).get("total_found", 0)
            new_keyword_stats = self.stats.stats.get("ads", {}).get("by_keyword", {}).get(keyword, {})
            new_keyword_found = new_keyword_stats.get("found", 0)
            
            if new_keyword_found > current_keyword_found:
                logger.info(f"✅ Ads recorded successfully for '{keyword}': {current_keyword_found} → {new_keyword_found}")
                logger.info(f"✅ Total ads updated: {current_total} → {new_total}")
                
                # Double-check by reading from file
                try:
                    with open(self.stats_file, 'r', encoding='utf-8-sig') as f:
                        file_stats = json.load(f)
                    file_keyword_found = file_stats.get("ads", {}).get("by_keyword", {}).get(keyword, {}).get("found", 0)
                    if file_keyword_found == new_keyword_found:
                        logger.info(f"✅ Stats file verification successful for '{keyword}': {file_keyword_found} ads")
                    else:
                        logger.warning(f"⚠️  Stats file mismatch for '{keyword}'. Memory: {new_keyword_found}, File: {file_keyword_found}")
                except Exception as e:
                    logger.error(f"❌ Failed to verify stats file for '{keyword}': {e}")
            else:
                logger.error(f"❌ Ads recording failed for '{keyword}'. Count unchanged: {current_keyword_found}")
                
        except Exception as e:
            logger.error(f"❌ Failed to record ads found for '{keyword}': {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        
        # Clean up Flask app context
        if hasattr(self, 'app_context'):
            self.app_context.pop()

    # DEPRECATED METHODS - These methods use JSON files and are no longer used
    # The scheduler now uses database storage via UserService
    
    def load_keywords(self):
        """DEPRECATED: Load keywords from JSON file - now using database"""
        logger.warning("load_keywords() is deprecated - using database instead")
        if os.path.exists(self.keywords_file):
            try:
                with open(self.keywords_file, 'r', encoding='utf-8-sig') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading keywords: {e}")
                return []
        return []

    def load_ads(self):
        """DEPRECATED: Load ads from JSON file - now using database"""
        logger.warning("load_ads() is deprecated - using database instead")
        if os.path.exists(self.ads_file):
            try:
                with open(self.ads_file, 'r', encoding='utf-8-sig') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading ads: {e}")
                return {}
        return {}

    def save_ads(self, ads):
        """DEPRECATED: Save ads to JSON file - now using database"""
        logger.warning("save_ads() is deprecated - using database instead")
        """DEPRECATED: Save ads to JSON file - now using database"""
        logger.warning("save_ads() is deprecated - using database instead")
        try:
            with open(self.ads_file, 'w', encoding='utf-8') as f:
                json.dump(ads, f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving ads: {e}")

    def notify_web_app(self, new_ads, deleted_ads, keywords_with_changes):
        """Send notification to web app via file-based communication"""
        try:
            notification = {
                'timestamp': datetime.now().isoformat(),
                'new_ads': new_ads,
                'deleted_ads': deleted_ads,
                'keywords_with_changes': list(keywords_with_changes)
            }
            
            # Write notification to file for web app to pick up
            with open('data/notifications.json', 'w', encoding='utf-8') as f:
                json.dump(notification, f, ensure_ascii=False)
                
            logger.info(f"Notification sent: {len(new_ads)} new, {len(deleted_ads)} deleted")
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

    def check_for_new_ads(self):
        """Main function to check for new ads using database storage"""
        logger.info("Starting database-based ad check...")
        
        try:
            # Get all active users
            users = User.query.filter_by(is_active=True).all()
            
            if not users:
                logger.info("No active users to check")
                return
            
            total_new_ads = 0
            total_deleted_ads = 0
            total_users_with_changes = 0
            
            # Track performance
            start_time = time.time()
            
            logger.info(f"Checking ads for {len(users)} active users")
            
            for user in users:
                try:
                    # Check ads for this user using UserService
                    success, new_ads, deleted_ads = self.user_service.check_user_ads(user.id)
                    
                    if success:
                        user_new_count = len(new_ads)
                        user_deleted_count = len(deleted_ads)
                        
                        total_new_ads += user_new_count
                        total_deleted_ads += user_deleted_count
                        
                        if user_new_count > 0 or user_deleted_count > 0:
                            total_users_with_changes += 1
                            logger.info(f"User {user.username}: {user_new_count} new, {user_deleted_count} deleted ads")
                        
                    else:
                        logger.error(f"Failed to check ads for user {user.username}")
                        
                except Exception as e:
                    logger.error(f"Error checking ads for user {user.username}: {e}")
                    continue
            
            # Record check duration with enhanced logging
            check_duration_ms = int((time.time() - start_time) * 1000)
            self.safe_record_check(check_duration_ms)
            
            logger.info(f"Check completed in {check_duration_ms}ms. Total: {total_new_ads} new ads, {total_deleted_ads} deleted ads across {total_users_with_changes} users")
            
            # Note: Individual user notifications are handled by the UserService
            # The web app reads directly from the database, so no file-based notifications needed
            
        except Exception as e:
            logger.error(f"Error in database ad check: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

    def check_for_new_ads_legacy(self):
        """DEPRECATED: Legacy JSON-based ad checking - kept for reference only"""
        logger.warning("check_for_new_ads_legacy() is deprecated - use database-based check_for_new_ads() instead")
        
        try:
            keywords = self.load_keywords()
            all_ads = self.load_ads()
            
            if not keywords:
                logger.info("No keywords to check")
                return
            
            has_changes = False
            new_ads = []
            deleted_ads = []
            keywords_with_changes = set()
            
            # Track performance
            start_time = time.time()
            
            # Clear all "NEW" tags from previous scan
            for keyword in all_ads:
                for ad in all_ads[keyword]:
                    if ad.get('isNew'):
                        ad['isNew'] = False
            
            logger.info(f"Checking {len(keywords)} keywords: {keywords}")
            
            for keyword in keywords:
                logger.info(f"Checking keyword: {keyword}")
                
                try:
                    # Get current ads for this keyword
                    current_ads = self.scraper.search(keyword)
                    logger.info(f"Found {len(current_ads)} ads for '{keyword}'")
                    
                    # Get previous ads
                    previous_ads = all_ads.get(keyword, [])
                    previous_ids = {ad['id'] for ad in previous_ads}
                    current_ids = {ad['id'] for ad in current_ads}
                    
                    # Find new ads
                    new_ids = current_ids - previous_ids
                    if new_ids:
                        has_changes = True
                        keywords_with_changes.add(keyword)
                        new_ads_count = 0
                        
                        logger.info(f"Found {len(new_ids)} new ads for '{keyword}'")
                        
                        for ad in current_ads:
                            if ad['id'] in new_ids:
                                ad['isNew'] = True
                                new_ads.append({'keyword': keyword, 'ad': ad})
                                new_ads_count += 1
                        
                        self.safe_record_ads_found(keyword, new_ads_count)
                    
                    # Find deleted ads
                    deleted_ids = previous_ids - current_ids
                    if deleted_ids:
                        keywords_with_changes.add(keyword)
                        deleted_ads_count = 0
                        
                        logger.info(f"Found {len(deleted_ids)} deleted ads for '{keyword}'")
                        
                        for ad in previous_ads:
                            if ad['id'] in deleted_ids:
                                deleted_ads.append({'keyword': keyword, 'ad': ad})
                                deleted_ads_count += 1
                        
                        self.stats.record_ads_deleted(keyword, deleted_ads_count)
                    
                    # Update ads for this keyword
                    if current_ads is not None:
                        if len(previous_ads) > 0 and len(current_ads) == 0:
                            logger.warning(f"Got 0 ads for '{keyword}' but had {len(previous_ads)} before. Keeping previous ads.")
                        else:
                            all_ads[keyword] = current_ads
                    
                except Exception as e:
                    logger.error(f"Error checking keyword '{keyword}': {e}")
                    continue
            
            # Save updated ads
            self.save_ads(all_ads)
            
            # Record check duration with enhanced logging
            check_duration_ms = int((time.time() - start_time) * 1000)
            self.safe_record_check(check_duration_ms)
            
            logger.info(f"Check completed in {check_duration_ms}ms. New: {len(new_ads)}, Deleted: {len(deleted_ads)}")
            
            # Send notification if there are changes
            if has_changes or deleted_ads:
                self.notify_web_app(new_ads, deleted_ads, keywords_with_changes)
            
        except Exception as e:
            logger.error(f"Error in ad check: {e}")

    def cleanup_old_new_tags(self):
        """Clean up old NEW tags from the database"""
        try:
            from datetime import datetime, timedelta, timezone
            
            # Clear "NEW" tags from ads older than 6 hours
            # Use timezone-naive comparison since database stores timezone-naive datetimes
            six_hours_ago = datetime.utcnow() - timedelta(hours=6)
            
            updated_count = UserAd.query.filter(
                UserAd.is_new == True,
                UserAd.marked_new_at < six_hours_ago
            ).update({'is_new': False})
            
            if updated_count > 0:
                db.session.commit()
                logger.info(f"Cleaned up NEW tags from {updated_count} ads older than 6 hours")
            
        except Exception as e:
            logger.error(f"Error cleaning up old NEW tags: {e}")
            db.session.rollback()

    def cleanup_old_deleted_ads(self):
        """Permanently remove ads that have been marked as deleted for more than 30 days"""
        try:
            from datetime import datetime, timedelta, timezone
            
            # Remove ads that have been deleted for more than 30 days
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            
            # Find ads marked as deleted for more than 30 days
            old_deleted_ads = UserAd.query.filter(
                UserAd.is_deleted == True,
                UserAd.scraped_at < thirty_days_ago  # Using scraped_at as we don't have deleted_at
            ).all()
            
            if old_deleted_ads:
                count = len(old_deleted_ads)
                
                # Remove associated favorites first (to maintain foreign key integrity)
                for ad in old_deleted_ads:
                    UserFavorite.query.filter_by(ad_id=ad.id).delete()
                
                # Remove the ads
                for ad in old_deleted_ads:
                    db.session.delete(ad)
                
                db.session.commit()
                logger.info(f"Permanently removed {count} ads that were deleted more than 30 days ago")
            else:
                logger.info("No old deleted ads to clean up")
                
        except Exception as e:
            logger.error(f"Error cleaning up old deleted ads: {e}")
            db.session.rollback()

    def run(self):
        """Main scheduler loop"""
        logger.info("Starting scheduler loop...")
        
        # Initial stats setup
        self.stats.record_system_start()
        self.stats.reset_uptime()
        # Note: No longer calling recalculate_stats_from_current_data() as it uses JSON files
        # Individual user stats are managed by UserService
        
        next_check = time.time()
        next_cleanup = time.time() + 3600  # First cleanup in 1 hour
        next_deleted_cleanup = time.time() + 86400  # First deleted ads cleanup in 24 hours
        
        while self.running:
            try:
                current_time = time.time()
                
                if current_time >= next_check:
                    self.check_for_new_ads()
                    next_check = current_time + self.check_interval
                    logger.info(f"Next check scheduled in {self.check_interval} seconds")
                
                # Run NEW tag cleanup every hour
                if current_time >= next_cleanup:
                    self.cleanup_old_new_tags()
                    next_cleanup = current_time + 3600  # Next cleanup in 1 hour
                
                # Run deleted ads cleanup once per day
                if current_time >= next_deleted_cleanup:
                    self.cleanup_old_deleted_ads()
                    next_deleted_cleanup = current_time + 86400  # Next cleanup in 24 hours
                
                # Sleep for 1 second to avoid busy waiting
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
                break
            except Exception as e:
                logger.error(f"Unexpected error in scheduler loop: {e}")
                time.sleep(10)  # Wait before retrying
        
        logger.info("Scheduler stopped")
        
        # Clean up Flask app context
        if hasattr(self, 'app_context'):
            self.app_context.pop()

if __name__ == '__main__':
    scheduler = AdScheduler()
    try:
        scheduler.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        # Ensure cleanup happens
        if hasattr(scheduler, 'app_context'):
            scheduler.app_context.pop()

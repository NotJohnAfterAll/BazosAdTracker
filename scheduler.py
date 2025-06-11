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
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from app.utils.bazos_scraper_fixed import BazosScraper
from utils.stats_tracker import StatsTracker

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
        
        # Data files
        self.keywords_file = 'data/keywords.json'
        self.ads_file = 'data/ads.json'
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        logger.info(f"Scheduler initialized with {self.check_interval}s interval")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    def load_keywords(self):
        """Load keywords from JSON file"""
        if os.path.exists(self.keywords_file):
            try:
                with open(self.keywords_file, 'r', encoding='utf-8-sig') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading keywords: {e}")
                return []
        return []

    def load_ads(self):
        """Load ads from JSON file"""
        if os.path.exists(self.ads_file):
            try:
                with open(self.ads_file, 'r', encoding='utf-8-sig') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading ads: {e}")
                return {}
        return {}

    def save_ads(self, ads):
        """Save ads to JSON file"""
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
        """Main function to check for new ads"""
        logger.info("Starting ad check...")
        
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
                        
                        self.stats.record_ads_found(keyword, new_ads_count)
                    
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
            
            # Record check duration
            check_duration_ms = int((time.time() - start_time) * 1000)
            self.stats.record_check(check_duration_ms)
            
            logger.info(f"Check completed in {check_duration_ms}ms. New: {len(new_ads)}, Deleted: {len(deleted_ads)}")
            
            # Send notification if there are changes
            if has_changes or deleted_ads:
                self.notify_web_app(new_ads, deleted_ads, keywords_with_changes)
            
        except Exception as e:
            logger.error(f"Error in ad check: {e}")

    def run(self):
        """Main scheduler loop"""
        logger.info("Starting scheduler loop...")
        
        # Initial stats setup
        self.stats.record_system_start()
        self.stats.reset_uptime()
        self.stats.recalculate_stats_from_current_data()
        
        next_check = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                if current_time >= next_check:
                    self.check_for_new_ads()
                    next_check = current_time + self.check_interval
                    logger.info(f"Next check scheduled in {self.check_interval} seconds")
                
                # Sleep for 1 second to avoid busy waiting
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
                break
            except Exception as e:
                logger.error(f"Unexpected error in scheduler loop: {e}")
                time.sleep(10)  # Wait before retrying
        
        logger.info("Scheduler stopped")

if __name__ == '__main__':
    scheduler = AdScheduler()
    try:
        scheduler.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

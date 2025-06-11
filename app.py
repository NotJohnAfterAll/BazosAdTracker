"""
BazosChecker - Monitor ads from Bazos.cz for specific keywords
This application helps users track classified ads on Bazos.cz by monitoring
for specific keywords and provides notifications when new ads are found.

Features:
- Monitor multiple keywords simultaneously
- Web interface for managing tracked keywords
- Real-time notifications of new ads
- Statistics tracking
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_socketio import SocketIO
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from app.utils.bazos_scraper_fixed import BazosScraper
from utils.stats_tracker import StatsTracker

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    filename='data/scraper.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

# Enable CORS for the Vue.js frontend
# In production, CORS is handled by reverse proxy, but allow for development
is_production = os.getenv('FLASK_ENV', 'development') == 'production'
cors_origins = ['*'] if is_production else [
    'http://localhost:3000', 'https://localhost:3000', 
    'http://localhost:3001', 'https://localhost:3001',
    'http://127.0.0.1:3000', 'https://127.0.0.1:3000'
]

CORS(app, origins=cors_origins)

# Configure Socket.IO for Cloudflare compatibility
socketio = SocketIO(
    app, 
    cors_allowed_origins=cors_origins,
    # Cloudflare WebSocket configuration
    transports=['polling', 'websocket'],  # Allow both transports, start with polling
    ping_timeout=60,
    ping_interval=25,
    # Additional settings for better Cloudflare compatibility
    logger=False,  # Disable logging for production
    engineio_logger=False,
    allow_upgrades=True,
    http_compression=True,
    # Handle connection timeouts better
    max_http_buffer_size=1000000
)

# Load test configuration if exists
def load_test_config():
    test_config_file = 'test_config.json'
    if os.path.exists(test_config_file):
        try:
            with open(test_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"Test configuration loaded: {config}")
                return config
        except Exception as e:
            print(f"Error loading test configuration: {e}")
    return None

# Initialize components
test_config = load_test_config()
print("Initializing BazosScraper...")

# Initialize scraper with test mode if configuration exists
if test_config and test_config.get('simulate_removal'):
    ad_id_to_exclude = test_config.get('ad_id_to_remove')
    ads_to_exclude = [ad_id_to_exclude] if ad_id_to_exclude else []
    print(f"Initializing scraper in test mode, excluding ads: {ads_to_exclude}")
    scraper = BazosScraper(test_mode=True, ads_to_exclude=ads_to_exclude)
else:
    print("Initializing scraper in normal mode")
    scraper = BazosScraper()

print("Initializing BackgroundScheduler...")
scheduler = BackgroundScheduler()
print("Initializing StatsTracker...")
stats = StatsTracker()

# Record system start
print("Recording system start...")
stats.record_system_start()
print("Resetting uptime...")
stats.reset_uptime()
print("Recalculating stats from current data...")
stats.recalculate_stats_from_current_data()
print("App initialization complete.")

# Data storage
KEYWORDS_FILE = 'data/keywords.json'
ADS_FILE = 'data/ads.json'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Load saved keywords
def load_keywords():
    if os.path.exists(KEYWORDS_FILE):
        try:
            with open(KEYWORDS_FILE, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except Exception:
            return []
    return []

# Save keywords
def save_keywords(keywords):
    with open(KEYWORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(keywords, f, ensure_ascii=False)

# Load saved advertisements
def load_ads():
    if os.path.exists(ADS_FILE):
        try:
            with open(ADS_FILE, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

# Save advertisements
def save_ads(ads):
    with open(ADS_FILE, 'w', encoding='utf-8') as f:
        json.dump(ads, f, ensure_ascii=False)

# Initialize data
keywords = load_keywords()
all_ads = load_ads()

# Check for new advertisements
def check_for_new_ads():
    """
    Main function to check for new ads for all tracked keywords.
    This function:
    1. Clears all "NEW" tags from previous scan
    2. Fetches current ads for each keyword
    3. Compares with previously stored ads to identify new/deleted ads
    4. Marks new ads with "NEW" tag
    5. Updates stored ads and statistics
    6. Notifies clients via WebSocket if changes detected
    """
    global all_ads
    has_new_ads = False
    new_ads = []
    deleted_ads = []
    keywords_with_changes = set()
    
    # Track performance for statistics
    start_time = time.time()
    
    # Clear all "NEW" tags from previous scan
    print("Clearing all NEW tags from previous scan...")
    for keyword in all_ads:
        for ad in all_ads[keyword]:
            if ad.get('isNew'):
                ad['isNew'] = False
                print(f"Cleared NEW tag from ad {ad.get('id', 'unknown')} in keyword '{keyword}'")
    
    # Reload keywords to include any new ones added via web interface
    current_keywords = load_keywords()
    
    print(f"Starting ad check for {len(current_keywords)} keywords: {current_keywords}")

    for keyword in current_keywords:
        print(f"Checking ads for keyword: {keyword}")
        
        # Get current ads for this keyword
        try:
            current_ads = scraper.search(keyword)
            print(f"Found {len(current_ads)} current ads for '{keyword}'")
        except Exception as e:
            print(f"Error scraping ads for '{keyword}': {e}")
            logger.error(f"Error scraping ads for '{keyword}': {e}")
            continue
        
        # Enhance ads with additional details if needed
        for ad in current_ads:
            # If title or seller name is default/missing, try to get more details
            if ('title' not in ad or not ad['title'] or ad['title'] == "Bazos.cz Advertisement" or
                'seller_name' not in ad or not ad['seller_name'] or ad['seller_name'] == "Bazos User"):
                if ad.get('link'):
                    try:
                        details = scraper.get_ad_details(ad['link'])
                        if details and 'title' in details and details['title'] and details['title'] != "No title":
                            ad['title'] = details['title']
                        if details and 'seller_name' in details and details['seller_name'] and details['seller_name'] != "Unknown seller":
                            ad['seller_name'] = details['seller_name']
                    except Exception as e:
                        print(f"Error fetching details for ad {ad.get('id', 'unknown')}: {e}")
        
        # Get previous ads for this keyword
        previous_ads = all_ads.get(keyword, [])
        previous_ids = {ad['id'] for ad in previous_ads}
        current_ids = {ad['id'] for ad in current_ads}
        
        print(f"Previous ads count for '{keyword}': {len(previous_ads)}")
        print(f"Current ads count for '{keyword}': {len(current_ads)}")
          # Find new ads
        new_ids = current_ids - previous_ids
        if new_ids:
            has_new_ads = True
            keywords_with_changes.add(keyword)
            new_ads_count = 0
            
            print(f"Found {len(new_ids)} new ads for '{keyword}': {new_ids}")
            
            # Mark new ads with NEW tag and add to notification list
            for ad in current_ads:
                if ad['id'] in new_ids:
                    ad['isNew'] = True  # Mark as new
                    print(f"Marked ad {ad['id']} as NEW for keyword '{keyword}'")
                    new_ads.append({
                        'keyword': keyword,
                        'ad': ad
                    })
                    new_ads_count += 1
            
            # Record stats
            if new_ads_count > 0:
                stats.record_ads_found(keyword, new_ads_count)
        
        # Find deleted ads (ads that were in previous but not in current)
        deleted_ids = previous_ids - current_ids
        if deleted_ids:
            keywords_with_changes.add(keyword)
            deleted_ads_count = 0
            
            print(f"Found {len(deleted_ids)} deleted ads for '{keyword}': {deleted_ids}")
            
            for ad in previous_ads:
                if ad['id'] in deleted_ids:
                    deleted_ads.append({
                        'keyword': keyword,
                        'ad': ad
                    })
                    deleted_ads_count += 1
            
            # Record stats
            if deleted_ads_count > 0:
                stats.record_ads_deleted(keyword, deleted_ads_count)
          # Update ads for this keyword - only if we got valid results
        # Don't update if we got an empty result when we previously had ads
        # This prevents false "all ads deleted" notifications due to scraping issues
        if current_ads is not None:
            # If we previously had ads but now got 0, be cautious
            if len(previous_ads) > 0 and len(current_ads) == 0:
                print(f"Warning: Got 0 ads for '{keyword}' but had {len(previous_ads)} before. Keeping previous ads to avoid false deletions.")
                # Don't update - keep previous ads
            else:
                all_ads[keyword] = current_ads
        else:
            print(f"Warning: No ads retrieved for '{keyword}', keeping previous ads")
    
    # Save updated ads
    save_ads(all_ads)
    
    # Record check duration
    check_duration_ms = int((time.time() - start_time) * 1000)
    stats.record_check(check_duration_ms)
    
    print(f"Check completed in {check_duration_ms}ms. New ads: {len(new_ads)}, Deleted ads: {len(deleted_ads)}")
    
    # Only emit notification if there are actual changes
    if has_new_ads or deleted_ads:
        print(f"Emitting ads_update event for {len(list(keywords_with_changes))} keywords with changes")
        # Emit event to all connected clients
        socketio.emit('ads_update', {
            'new_ads': new_ads,
            'deleted_ads': deleted_ads,
            'keywords_with_changes': list(keywords_with_changes),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        print("No changes detected, no notification sent")

# Routes
@app.route('/')
def index():
    """Serve the Vue.js frontend"""
    try:
        return send_file('frontend/dist/index.html')
    except:
        # Fallback to API info if frontend not available
        return jsonify({
            "message": "Bazos Ad Tracker API",
            "version": "2.0",
            "frontend": "Vue.js frontend not found - run 'npm run build' in frontend/",
            "endpoints": {
                "health": "/api/health",
                "keywords": "/api/keywords",
                "recent_ads": "/api/recent-ads",
                "stats": "/api/stats",
                "manual_check": "/api/manual-check",
                "notifications": "/api/notifications",
                "api_info": "/api/info"
            }
        })

@app.route('/api/info')
def api_info():
    """API endpoint documentation"""
    return jsonify({
        "message": "Bazos Ad Tracker API",
        "version": "2.0",
        "frontend": "Vue.js (served at /)",
        "endpoints": {
            "health": "/api/health",
            "keywords": "/api/keywords",
            "recent_ads": "/api/recent-ads",
            "stats": "/api/stats",
            "manual_check": "/api/manual-check",
            "notifications": "/api/notifications"
        },
        "websocket": "Socket.IO supported",
        "documentation": "See README.md for setup instructions"
    })

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve Vue.js static assets"""
    return send_from_directory('frontend/dist/assets', filename)

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    try:
        return send_from_directory('frontend/dist', 'favicon.ico')
    except:
        return send_from_directory('frontend/public', 'favicon.png')

@app.route('/api/keywords', methods=['GET', 'POST'])
def manage_keywords():
    global keywords
    
    if request.method == 'POST':
        data = request.json
        new_keyword = data.get('keyword')
        
        if new_keyword and new_keyword not in keywords:
            keywords.append(new_keyword)
            save_keywords(keywords)
            
            # Get initial ads for this keyword
            initial_ads = scraper.search(new_keyword)
            all_ads[new_keyword] = initial_ads
            save_ads(all_ads)
            
            return jsonify({'success': True, 'keywords': keywords})
        
        return jsonify({'success': False, 'error': 'Invalid or duplicate keyword'})
    
    return jsonify({'keywords': keywords})

@app.route('/api/keywords/<keyword>', methods=['DELETE'])
def delete_keyword(keyword):
    global keywords, all_ads
    
    if keyword in keywords:
        print(f"Deleting keyword '{keyword}' and all associated data...")
        
        # Remove from keywords list
        keywords.remove(keyword)
        save_keywords(keywords)
        
        # Remove ads for this keyword
        if keyword in all_ads:
            del all_ads[keyword]
            save_ads(all_ads)
        
        # Remove stats for this keyword
        stats.remove_keyword_stats(keyword)
        
        print(f"Successfully deleted keyword '{keyword}' and cleaned up all data")
        return jsonify({'success': True, 'keywords': keywords})
    
    return jsonify({'success': False, 'error': 'Keyword not found'})

@app.route('/api/ads')
def get_ads():
    keyword = request.args.get('keyword')
    
    if keyword and keyword in all_ads:
        # Get ads for a specific keyword
        ads_to_return = all_ads[keyword]
        
        # Check for ads with default/placeholder titles and try to get more details
        for ad in ads_to_return:
            if ('title' not in ad or not ad['title'] or ad['title'] == "Bazos.cz Advertisement" or
                'seller_name' not in ad or not ad['seller_name'] or ad['seller_name'] == "Bazos User"):
                if ad.get('link'):
                    try:
                        details = scraper.get_ad_details(ad['link'])
                        if details and 'title' in details and details['title'] and details['title'] != "No title":
                            ad['title'] = details['title']
                        if details and 'seller_name' in details and details['seller_name'] and details['seller_name'] != "Unknown seller":
                            ad['seller_name'] = details['seller_name']
                    except Exception as e:
                        print(f"Error fetching details for ad {ad.get('id', 'unknown')}: {e}")
                        
        return jsonify({'ads': ads_to_return})
    
    # Return all ads
    return jsonify({'ads': all_ads})

@app.route('/api/recent-ads')
def get_recent_ads():
    all_recent_ads = []
    seen_ad_ids = set()  # Track ad IDs to prevent duplicates
    
    for keyword, ads in all_ads.items():
        for ad in ads[:5]:  # Get 5 most recent ads per keyword
            # Clean up the ad data if needed
            if 'title' in ad and (not ad['title'] or ad['title'] == "Bazos.cz Advertisement"):
                # Try to get more details about the ad
                if ad.get('link'):
                    try:
                        details = scraper.get_ad_details(ad['link'])
                        if details and 'title' in details and details['title'] and details['title'] != "No title":
                            ad['title'] = details['title']
                        if details and 'seller_name' in details and details['seller_name'] and details['seller_name'] != "Unknown seller":
                            ad['seller_name'] = details['seller_name']
                    except Exception as e:
                        print(f"Error fetching details for ad {ad.get('id', 'unknown')}: {e}")
            
            # Only add if we haven't seen this ad ID before
            if ad['id'] not in seen_ad_ids:
                seen_ad_ids.add(ad['id'])
                all_recent_ads.append({
                    'keyword': keyword,
                    'ad': ad
                })    # Sort by date_added (actual ad posting date) if available, otherwise fall back to scraped_at
    def get_sort_key(item):
        ad = item['ad']
        
        # First priority: use date_added (actual posting date from Bazos)
        if ad.get('date_added') and ad['date_added'] != 'N/A':
            try:
                # Parse Czech date format like "8.6. 2025" or "7.6. 2025"
                date_str = ad['date_added'].strip()
                # Handle formats like "8.6. 2025" or "8.6.2025"
                if '.' in date_str:
                    parts = date_str.replace(' ', '').split('.')
                    if len(parts) >= 3:
                        day = int(parts[0])
                        month = int(parts[1])
                        year = int(parts[2]) if parts[2] else 2025  # Default to current year
                        # Return timestamp for sorting (more recent = higher number for reverse=True)
                        return datetime(year, month, day).timestamp()
            except (ValueError, IndexError):
                pass
        
        # Second priority: use scraped_at timestamp
        if ad.get('scraped_at'):
            return ad['scraped_at']
        
        # Fallback: use parsed date field
        if ad.get('date'):
            try:
                return datetime.strptime(ad['date'], '%Y-%m-%d %H:%M:%S').timestamp()
            except:
                pass
        
        # Last resort: return 0 (oldest)
        return 0
    
    all_recent_ads.sort(key=get_sort_key, reverse=True)
    
    return jsonify({'ads': all_recent_ads[:20]})  # Return top 20 recent ads

@app.route('/api/stats')
def get_system_stats():
    """Get system statistics"""
    return jsonify(stats.get_stats())

@app.route('/api/manual-check')
def manual_check():
    """Manually trigger ad checking for testing"""
    print("=" * 50)
    print("MANUAL CHECK TRIGGERED FROM WEB INTERFACE")
    print("=" * 50)
    try:
        check_for_new_ads()
        print("=" * 50)
        print("MANUAL CHECK COMPLETED SUCCESSFULLY")
        print("=" * 50)
        return jsonify({"status": "success", "message": "Manual ad check completed"})
    except Exception as e:
        print(f"MANUAL CHECK FAILED: {e}")
        print("=" * 50)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/recalculate-stats')
def recalculate_stats():
    """Manually recalculate stats from current data"""
    try:
        success = stats.recalculate_stats_from_current_data()
        if success:
            return jsonify({"status": "success", "message": "Stats recalculated successfully"})
        else:
            return jsonify({"status": "error", "message": "Failed to recalculate stats"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/notifications')
def get_notifications():
    """Get pending notifications from scheduler"""
    notifications_file = 'data/notifications.json'
    
    if os.path.exists(notifications_file):
        try:
            with open(notifications_file, 'r', encoding='utf-8') as f:
                notification = json.load(f)
            
            # Delete the notification file after reading
            os.remove(notifications_file)
            
            return jsonify(notification)
        except Exception as e:
            logger.error(f"Error reading notifications: {e}")
            return jsonify({'error': 'Failed to read notifications'}), 500
    
    return jsonify({'new_ads': [], 'deleted_ads': [], 'keywords_with_changes': []})

@app.route('/api/health')
def health_check():
    """Health check endpoint for container orchestration (Coolify, Docker, etc.)"""
    try:
        # Basic health checks
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "services": {
                "database": "ok",
                "scraper": "ok",
                "scheduler": "ok" if scheduler.running else "stopped"
            },
            "stats": {
                "keywords_count": len(keywords),
                "total_ads": sum(len(ads) for ads in all_ads.values()),
                "uptime": stats.get_stats().get('system', {}).get('uptime_seconds', 0)
            }
        }
        
        # Check if critical services are working
        if not os.path.exists(KEYWORDS_FILE):
            health_status["services"]["database"] = "warning"
        
        if not scheduler.running:
            health_status["status"] = "degraded"
            
        return jsonify(health_status), 200
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

if __name__ == '__main__':
    # Get port and host from environment variables (Coolify compatibility)
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    # Check if we're running in production (with Gunicorn) or development
    is_production = os.getenv('FLASK_ENV', 'development') == 'production'
    is_gunicorn = 'gunicorn' in os.environ.get('SERVER_SOFTWARE', '')
    
    print(f"🚀 Starting Bazos Ad Tracker...")
    print(f"   Environment: {'Production' if is_production else 'Development'}")
    print(f"   Server: {'Gunicorn' if is_gunicorn else 'Flask Dev Server'}")
    print(f"   Host: {host}:{port}")
    
    # Only start scheduler in development mode or when explicitly enabled
    if not is_production and not is_gunicorn:
        # Development mode - use APScheduler
        check_interval = int(os.getenv('CHECK_INTERVAL', 300))
          # Only start scheduler in the main process (not in Flask's reloader subprocess)
        if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            print(f"📅 Starting scheduler with {check_interval} second intervals...")
            scheduler.add_job(check_for_new_ads, 'interval', seconds=check_interval, id='check_ads')
            scheduler.start()
            print("✅ Scheduler started successfully!")
    else:
        print("🏭 Production mode: Scheduler should be running as separate process")
        print("   Start scheduler with: python scheduler.py")
    
    print(f"🌐 Starting Flask app on http://{host}:{port}")
    print("   HTTPS handled by reverse proxy (Cloudflare/Coolify)")
    
    # Production vs Development mode
    debug_mode = not is_production and os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    try:
        socketio.run(
            app, 
            debug=debug_mode, 
            host=host, 
            port=port,
            # Additional production settings
            use_reloader=not is_production,
            log_output=not is_production
        )
    except (KeyboardInterrupt, SystemExit):
        if scheduler.running:
            scheduler.shutdown()

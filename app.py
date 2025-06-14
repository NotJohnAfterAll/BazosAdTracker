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
import threading
import stat
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory, send_file, make_response
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
    'http://localhost:5000', 'https://localhost:5000',
    'http://127.0.0.1:3000', 'https://127.0.0.1:3000',
    'http://127.0.0.1:5000', 'https://127.0.0.1:5000'
]

# Add your Cloudflare domain to CORS origins in production
if is_production:
    cors_origins = [
        'https://bazos.notjohn.net',
        'http://bazos.notjohn.net',
        '*'  # Allow all for now, can be restricted later
    ]

CORS(app, origins=cors_origins)

# Configure Socket.IO for Cloudflare compatibility
socketio = SocketIO(
    app, 
    cors_allowed_origins=cors_origins,
    # Cloudflare WebSocket configuration - prefer polling first
    transports=['polling'],  # Start with polling only, no websockets initially
    ping_timeout=120,  # Increased timeout for Cloudflare
    ping_interval=60,  # Increased interval
    # Additional settings for better Cloudflare compatibility
    logger=False,  # Disable logging for production
    engineio_logger=False,
    allow_upgrades=False,  # Disable upgrades to websockets for now
    http_compression=True,
    # Handle connection timeouts better
    max_http_buffer_size=1000000,
    # Cloudflare specific settings
    upgrade_timeout=120,
    async_mode='threading'
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

# Initialize data with debugging
print("Loading data from files...")
keywords = load_keywords()
all_ads = load_ads()

print(f"Loaded {len(keywords)} keywords: {keywords}")
print(f"Loaded {len(all_ads)} keyword groups for ads")
if all_ads:
    total_ads = sum(len(ad_list) for ad_list in all_ads.values())
    print(f"Total ads loaded: {total_ads}")
    print(f"Keyword groups: {list(all_ads.keys())}")
else:
    print("WARNING: No ads loaded from file!")
print("Data loading complete.")

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

# Add middleware for better Cloudflare compatibility
@app.before_request
def before_request():
    """Handle Cloudflare-specific headers and optimizations"""
    
    # Handle Cloudflare's real IP headers
    if 'CF-Connecting-IP' in request.headers:
        # Use Cloudflare's real IP
        request.environ['REMOTE_ADDR'] = request.headers['CF-Connecting-IP']
    elif 'X-Forwarded-For' in request.headers:
        # Fallback to X-Forwarded-For
        request.environ['REMOTE_ADDR'] = request.headers['X-Forwarded-For'].split(',')[0].strip()
    
    # Set CORS headers for preflight requests
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response

@app.after_request
def after_request(response):
    """Add headers for better Cloudflare caching and performance"""
    
    # Don't cache Socket.IO requests
    if request.path.startswith('/socket.io/'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    # Cache static assets for 1 hour
    elif request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=3600'
    
    # Don't cache dynamic API responses that need real-time updates
    elif request.path.startswith('/api/') and request.path in [
        '/api/recent-ads', '/api/ads', '/api/notifications', '/api/stats'
    ]:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    # Cache other API responses for 30 seconds (like /api/keywords, /api/info)
    elif request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'public, max-age=30'
    
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response

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

@app.route('/notification.mp3')
def notification_sound():
    """Serve notification audio file"""
    try:
        return send_from_directory('frontend/public', 'notification.mp3')
    except:
        # Fallback to silence if file not found
        return '', 404

@app.route('/api/keywords', methods=['GET', 'POST'])
def manage_keywords():
    global keywords
    
    if request.method == 'POST':
        try:
            data = request.json
            print(f"🔥 POST /api/keywords - Received data: {data}")
            
            if not data:
                print("❌ No JSON data received")
                return jsonify({'success': False, 'error': 'No data provided'})
            
            new_keyword = data.get('keyword')
            print(f"🔥 Extracted keyword: '{new_keyword}'")
            
            if not new_keyword:
                print("❌ Empty keyword")
                return jsonify({'success': False, 'error': 'Please enter a keyword'})
            
            new_keyword = new_keyword.strip()
            if not new_keyword:
                print("❌ Keyword is empty after strip")
                return jsonify({'success': False, 'error': 'Please enter a keyword'})
            
            if new_keyword in keywords:
                print(f"❌ Keyword '{new_keyword}' already exists")
                return jsonify({'success': False, 'error': 'This keyword is already being tracked'})
            
            print(f"✅ Adding keyword: '{new_keyword}'")
            
            try:
                # Add keyword first
                keywords.append(new_keyword)
                save_keywords(keywords)
                print(f"✅ Keyword '{new_keyword}' saved to file")
                
                # Try to get initial ads for this keyword (with error handling)
                try:
                    print(f"🔍 Attempting to fetch initial ads for keyword: {new_keyword}")
                    initial_ads = scraper.search(new_keyword)
                    all_ads[new_keyword] = initial_ads
                    save_ads(all_ads)
                    print(f"✅ Successfully fetched {len(initial_ads)} initial ads for '{new_keyword}'")
                except Exception as scraper_error:
                    # If scraping fails, still add the keyword but with empty ads list
                    print(f"⚠️ Failed to fetch initial ads for '{new_keyword}': {scraper_error}")
                    logger.error(f"Failed to fetch initial ads for '{new_keyword}': {scraper_error}")
                    all_ads[new_keyword] = []
                    save_ads(all_ads)
                
                return jsonify({
                    'success': True, 
                    'keywords': keywords,
                    'message': f"Keyword '{new_keyword}' added successfully. Initial ads will be loaded on next check."
                })
                
            except Exception as save_error:
                # If there's any error saving, remove the keyword from the list and report failure
                if new_keyword in keywords:
                    keywords.remove(new_keyword)
                    save_keywords(keywords)
                print(f"❌ Error adding keyword '{new_keyword}': {save_error}")
                logger.error(f"Error adding keyword '{new_keyword}': {save_error}")
                return jsonify({'success': False, 'error': f'Failed to add keyword: {str(save_error)}'})
                
        except Exception as e:
            print(f"❌ Unexpected error in manage_keywords: {e}")
            logger.error(f"Unexpected error in manage_keywords: {e}")
            return jsonify({'success': False, 'error': f'Server error: {str(e)}'})    # GET request - return keywords
    print(f"API /keywords GET called, returning {len(keywords)} keywords: {keywords}")
    
    if not keywords:
        print("WARNING: keywords is empty, trying to reload from file")
        keywords = load_keywords()
        print(f"Reloaded {len(keywords)} keywords: {keywords}")
        print(f"Reloaded {len(keywords)} keywords: {keywords}")
    
    response = jsonify({'keywords': keywords})
    # Disable caching for dynamic data
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

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
    global all_ads
    keyword = request.args.get('keyword')
    print(f"API /ads called with keyword='{keyword}', all_ads has {len(all_ads)} keyword groups")
    
    if not all_ads:
        print("WARNING: all_ads is empty, trying to reload from file")
        all_ads = load_ads()
        print(f"Reloaded {len(all_ads)} keyword groups")
    
    if keyword and keyword in all_ads:
        # Get ads for a specific keyword
        ads_to_return = all_ads[keyword]
        print(f"Returning {len(ads_to_return)} ads for keyword '{keyword}'")
        
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
    print(f"Returning all ads: {len(all_ads)} keyword groups")
    return jsonify({'ads': all_ads})

@app.route('/api/recent-ads')
def get_recent_ads():
    global all_ads
    print(f"API /recent-ads called. all_ads has {len(all_ads)} keyword groups")
    
    all_recent_ads = []
    seen_ad_ids = set()  # Track ad IDs to prevent duplicates
    
    if not all_ads:
        print("WARNING: all_ads is empty, trying to reload from file")
        all_ads = load_ads()
        print(f"Reloaded {len(all_ads)} keyword groups")
    
    for keyword, ads in all_ads.items():
        print(f"Processing keyword '{keyword}' with {len(ads)} ads")
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
                })    
    
    print(f"API /recent-ads returning {len(all_recent_ads)} ads")
    
    # Sort by date_added (actual ad posting date) if available, otherwise fall back to scraped_at
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
        
    except Exception as e:        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

@app.route('/api/debug')
def debug_api():
    """Debug endpoint to help diagnose production issues"""
    import sys
    debug_info = {
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "flask_env": os.environ.get('FLASK_ENV', 'not set'),
            "flask_debug": os.environ.get('FLASK_DEBUG', 'not set')
        },
        "file_system": {
            "data_dir_exists": os.path.exists("data"),
            "keywords_file_exists": os.path.exists("data/keywords.json"),
            "ads_file_exists": os.path.exists("data/ads.json"), 
            "stats_file_exists": os.path.exists("data/stats.json")
        },
        "data_status": {
            "keywords_in_memory": len(keywords),
            "keywords_list": keywords,
            "ads_groups_in_memory": len(all_ads),
            "ads_groups": list(all_ads.keys()),
            "total_ads_in_memory": sum(len(ad_list) for ad_list in all_ads.values()) if all_ads else 0
        }
    }
    
    # Try to read files directly
    try:
        if os.path.exists("data/keywords.json"):
            with open("data/keywords.json", 'r', encoding='utf-8-sig') as f:
                file_keywords = json.load(f)
                debug_info["file_status"] = {
                    "keywords_from_file": file_keywords,
                    "keywords_count": len(file_keywords)
                }
        
        if os.path.exists("data/ads.json"):
            with open("data/ads.json", 'r', encoding='utf-8-sig') as f:
                file_ads = json.load(f)
                debug_info["file_status"]["ads_from_file_count"] = sum(len(ad_list) for ad_list in file_ads.values()) if isinstance(file_ads, dict) else 0
                debug_info["file_status"]["ads_groups_from_file"] = list(file_ads.keys()) if isinstance(file_ads, dict) else "invalid format"
    except Exception as e:
        debug_info["file_read_error"] = str(e)
    
    return jsonify(debug_info)

# File monitoring for automatic data reloading
file_mtimes = {
    'keywords': 0,
    'ads': 0
}

def check_file_changes():
    """Check if data files have been modified and reload if necessary"""
    global keywords, all_ads, file_mtimes
    
    try:
        # Check keywords file
        if os.path.exists(KEYWORDS_FILE):
            keywords_mtime = os.path.getmtime(KEYWORDS_FILE)
            if keywords_mtime > file_mtimes['keywords']:
                print(f"🔄 Keywords file changed, reloading...")
                keywords = load_keywords()
                file_mtimes['keywords'] = keywords_mtime
                print(f"✅ Reloaded {len(keywords)} keywords: {keywords}")
        
        # Check ads file  
        if os.path.exists(ADS_FILE):
            ads_mtime = os.path.getmtime(ADS_FILE)
            if ads_mtime > file_mtimes['ads']:
                print(f"🔄 Ads file changed, reloading...")
                all_ads = load_ads()
                file_mtimes['ads'] = ads_mtime
                total_ads = sum(len(ad_list) for ad_list in all_ads.values()) if all_ads else 0
                print(f"✅ Reloaded {len(all_ads)} keyword groups with {total_ads} total ads")
                
                # Check for and handle notifications
                handle_pending_notifications()
                
    except Exception as e:
        print(f"❌ Error checking file changes: {e}")

def handle_pending_notifications():
    """Check for and process pending notifications from scheduler"""
    notifications_file = 'data/notifications.json'
    
    if os.path.exists(notifications_file):
        try:
            with open(notifications_file, 'r', encoding='utf-8') as f:
                notification = json.load(f)
            
            print(f"📢 Processing notification: {len(notification.get('new_ads', []))} new, {len(notification.get('deleted_ads', []))} deleted")
            
            # Emit Socket.IO event to connected clients
            if notification.get('new_ads') or notification.get('deleted_ads'):
                socketio.emit('ads_update', notification)
                print(f"✅ Notification sent to connected clients")
            
            # Delete the notification file after processing
            os.remove(notifications_file)
            
        except Exception as e:
            print(f"❌ Error processing notifications: {e}")

def start_file_monitoring():
    """Start background thread to monitor file changes"""
    def monitor_files():
        while True:
            try:
                check_file_changes()
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                print(f"❌ File monitoring error: {e}")
                time.sleep(10)  # Wait longer on error
    
    monitor_thread = threading.Thread(target=monitor_files, daemon=True)
    monitor_thread.start()
    print("🔍 Started file monitoring thread")

# Initialize file modification times
if os.path.exists(KEYWORDS_FILE):
    file_mtimes['keywords'] = os.path.getmtime(KEYWORDS_FILE)
if os.path.exists(ADS_FILE):
    file_mtimes['ads'] = os.path.getmtime(ADS_FILE)

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
    
    # Start file monitoring for production (to detect scheduler updates)
    if is_production or is_gunicorn:
        print("🔍 Starting file monitoring for production...")
        start_file_monitoring()
    
    # Only start scheduler in development mode or when explicitly enabled
    if not is_production and not is_gunicorn:
        # Development mode - use APScheduler
        check_interval = int(os.getenv('CHECK_INTERVAL', 300))
          # Only start scheduler in the main process (not in Flask's reloader subprocess)
        if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            print(f"📅 Starting scheduler with {check_interval} second intervals...")
            scheduler.add_job(check_for_new_ads, 'interval', seconds=check_interval, id='check_ads')
            scheduler.start()
        else:    
            print("✅ Scheduler started successfully!")
            print("🏭 Production mode: Scheduler should be running as separate process")
            print("   Start scheduler with: python scheduler.py")
    
    print(f"🌐 Starting Flask app on http://{host}:{port}")
    print("   HTTPS handled by reverse proxy (Cloudflare/Coolify)")
      # Production vs Development mode
    debug_mode = not is_production and os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    try:
        if is_production:
            # Production mode - allow unsafe Werkzeug or use app directly
            print("⚠️  Running with Werkzeug in production (use Gunicorn for better performance)")
            socketio.run(
                app, 
                debug=False, 
                host=host, 
                port=port,
                use_reloader=False,
                log_output=False,
                allow_unsafe_werkzeug=True  # Allow Werkzeug in production
            )
        else:
            # Development mode
            socketio.run(
                app, 
                debug=debug_mode, 
                host=host, 
                port=port,
                use_reloader=True,
                log_output=True
            )
    except (KeyboardInterrupt, SystemExit):
        if scheduler.running:
            scheduler.shutdown()

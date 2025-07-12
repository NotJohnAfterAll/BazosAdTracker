"""
User service for handling user-specific operations
"""
import json
import os
import time
from datetime import datetime, timedelta, timezone
from app.models import db, User, UserKeyword, UserAd, UserFavorite, UserStats
from app.utils.bazos_scraper_fixed import BazosScraper
import logging
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

def retry_db_operation(operation, max_retries=3, delay=0.1):
    """Retry database operation if it fails due to database lock"""
    for attempt in range(max_retries):
        try:
            return operation()
        except OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                logger.warning(f"Database locked, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                raise
    return None

class UserService:
    """Service for handling user-specific operations"""
    
    def __init__(self, scraper=None):
        self.scraper = scraper or BazosScraper()
    
    def get_user_keywords(self, user_id):
        """Get all keywords for a user"""
        keywords = UserKeyword.query.filter_by(user_id=user_id, is_active=True).all()
        return [kw.to_dict() for kw in keywords]
    
    def add_user_keyword(self, user_id, keyword):
        """Add a keyword for a user"""
        try:
            # Check if keyword already exists for this user
            existing = UserKeyword.query.filter_by(
                user_id=user_id, 
                keyword=keyword
            ).first()
            
            if existing:
                if existing.is_active:
                    return False, "Keyword already exists"
                else:
                    # Reactivate existing keyword
                    existing.is_active = True
                    db.session.commit()
                    return True, "Keyword reactivated"
            
            # Create new keyword
            user_keyword = UserKeyword(
                user_id=user_id,
                keyword=keyword
            )
            db.session.add(user_keyword)
            db.session.commit()
            
            # Try to fetch initial ads (don't mark as new for existing ads)
            try:
                initial_ads = self.scraper.search(keyword)
                self.save_user_ads(user_id, user_keyword.id, initial_ads, mark_as_new=False)
                logger.info(f"Added keyword '{keyword}' for user {user_id} with {len(initial_ads)} initial ads (not marked as new)")
            except Exception as e:
                logger.error(f"Failed to fetch initial ads for keyword '{keyword}': {e}")
            
            return True, "Keyword added successfully"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding keyword for user {user_id}: {e}")
            return False, "Failed to add keyword"
    
    def remove_user_keyword(self, user_id, keyword):
        """Remove a keyword for a user"""
        try:
            user_keyword = UserKeyword.query.filter_by(
                user_id=user_id,
                keyword=keyword
            ).first()
            
            if not user_keyword:
                return False, "Keyword not found"
            
            # Soft delete - mark as inactive
            user_keyword.is_active = False
            
            # Also mark all ads for this keyword as deleted
            UserAd.query.filter_by(
                user_id=user_id,
                keyword_id=user_keyword.id
            ).update({'is_deleted': True})
            
            db.session.commit()
            logger.info(f"Removed keyword '{keyword}' for user {user_id}")
            return True, "Keyword removed successfully"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing keyword for user {user_id}: {e}")
            return False, "Failed to remove keyword"
    
    def save_user_ads(self, user_id, keyword_id, ads, mark_as_new=True):
        """Save ads for a user and keyword"""
        try:
            for ad_data in ads:
                # Check if ad already exists
                existing = UserAd.query.filter_by(
                    user_id=user_id,
                    ad_id=ad_data['id']
                ).first()
                
                if existing:
                    # Update existing ad
                    existing.title = ad_data.get('title', existing.title)
                    existing.description = ad_data.get('description', existing.description)
                    existing.price = ad_data.get('price', existing.price)
                    existing.location = ad_data.get('location', existing.location)
                    existing.seller_name = ad_data.get('seller_name', existing.seller_name)
                    existing.is_deleted = False  # Mark as not deleted if it was
                else:
                    # Create new ad
                    date_added_str = ad_data.get('date_added', '')
                    current_time = datetime.utcnow()
                    user_ad = UserAd(
                        user_id=user_id,
                        keyword_id=keyword_id,
                        ad_id=ad_data['id'],
                        title=ad_data.get('title', ''),
                        description=ad_data.get('description', ''),
                        price=ad_data.get('price', ''),
                        location=ad_data.get('location', ''),
                        seller_name=ad_data.get('seller_name', ''),
                        link=ad_data.get('link', ''),
                        image_url=ad_data.get('image_url', ''),
                        date_added=date_added_str,
                        date_added_parsed=UserAd.parse_czech_date(date_added_str),
                        is_new=mark_as_new,
                        marked_new_at=current_time if mark_as_new else None
                    )
                    db.session.add(user_ad)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving ads for user {user_id}: {e}")
            return False
    
    def get_user_ads(self, user_id, keyword=None, include_deleted=False):
        """Get ads for a user"""
        query = UserAd.query.filter_by(user_id=user_id)
        
        if keyword:
            # Join with UserKeyword to filter by keyword
            query = query.join(UserKeyword).filter(UserKeyword.keyword == keyword)
        
        if not include_deleted:
            query = query.filter(UserAd.is_deleted == False)
        
        ads = query.order_by(UserAd.scraped_at.desc()).all()
        return [ad.to_dict() for ad in ads]
    
    def get_user_recent_ads(self, user_id, limit=100, include_deleted=False):
        """Get recent ads for a user, sorted by newest first (by posting date, then scrape time)"""
        def _get_ads():
            query = UserAd.query.filter_by(user_id=user_id)
            
            if not include_deleted:
                query = query.filter_by(is_deleted=False)
            
            ads = query.order_by(
                UserAd.date_added_parsed.desc().nulls_last(),
                UserAd.scraped_at.desc(),
                UserAd.id.desc()
            ).limit(limit).all()
            
            return [ad.to_dict() for ad in ads]
        
        try:
            result = retry_db_operation(_get_ads)
            logger.info(f"Retrieved {len(result)} recent ads for user {user_id} (limit: {limit}, include_deleted: {include_deleted})")
            return result
        except Exception as e:
            logger.error(f"Failed to get recent ads for user {user_id}: {e}")
            return []
    
    def toggle_user_favorite(self, user_id, bazos_ad_id):
        """Toggle favorite status for an ad using Bazos ad ID"""
        try:
            # Find the ad by Bazos ad_id (string)
            ad = UserAd.query.filter_by(user_id=user_id, ad_id=bazos_ad_id).first()
            if not ad:
                return False, "Ad not found"
            
            # Check if already favorited using database ID
            existing_favorite = UserFavorite.query.filter_by(
                user_id=user_id,
                ad_id=ad.id  # Use database ID for the favorite relationship
            ).first()
            
            if existing_favorite:
                # Remove favorite
                db.session.delete(existing_favorite)
                db.session.commit()
                return True, "Removed from favorites"
            else:
                # Add favorite using database ID
                favorite = UserFavorite(user_id=user_id, ad_id=ad.id)
                db.session.add(favorite)
                db.session.commit()
                return True, "Added to favorites"
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error toggling favorite for user {user_id}: {e}")
            return False, "Failed to update favorites"
    
    def get_user_favorites(self, user_id):
        """Get user's favorite ads"""
        favorites = UserFavorite.query.filter_by(user_id=user_id).all()
        return [fav.to_dict() for fav in favorites]
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        stats = UserStats.query.filter_by(user_id=user_id).first()
        if not stats:
            # Create default stats
            stats = UserStats(user_id=user_id)
            db.session.add(stats)
            db.session.commit()
        
        # Add additional calculated stats
        stats_dict = stats.to_dict()
        
        # Count active keywords
        active_keywords = UserKeyword.query.filter_by(
            user_id=user_id,
            is_active=True
        ).count()
        
        # Count total ads
        total_ads = UserAd.query.filter_by(
            user_id=user_id,
            is_deleted=False
        ).count()
        
        # Count favorites
        favorites_count = UserFavorite.query.filter_by(user_id=user_id).count()
        
        # Calculate system uptime from app start time (not user creation)
        import os
        uptime_seconds = 0
        try:
            # Try to get system uptime from stats file if available
            stats_file = "data/stats.json"
            if os.path.exists(stats_file):
                import json
                with open(stats_file, 'r', encoding='utf-8-sig') as f:
                    global_stats = json.load(f)
                    system_stats = global_stats.get('system', {})
                    start_time_str = system_stats.get('start_time')
                    if start_time_str:
                        from datetime import datetime
                        start_time = datetime.fromisoformat(start_time_str)
                        uptime_seconds = int((datetime.now() - start_time).total_seconds())
        except Exception as e:
            logger.warning(f"Could not calculate system uptime: {e}")
            # Fallback to user creation time
            user = User.query.get(user_id)
            if user and user.created_at:
                uptime_seconds = int((datetime.utcnow() - user.created_at).total_seconds())
        
        # Get check interval from environment
        check_interval = int(os.getenv('CHECK_INTERVAL', 300))
        check_interval_minutes = check_interval // 60
        
        # Format stats to match frontend expectations
        formatted_stats = {
            'total_checks': stats_dict.get('total_checks', 0),
            'total_ads': total_ads,
            'uptime': self._format_uptime(uptime_seconds),
            'uptime_seconds': uptime_seconds,
            'avg_duration': stats_dict.get('avg_check_duration_ms', 0),
            'active_keywords': active_keywords,
            'favorites_count': favorites_count,
            'check_interval': check_interval,
            'check_interval_minutes': check_interval_minutes,
            'last_check_at': stats_dict.get('last_check_at'),
        }
        
        return formatted_stats
    
    def update_user_stats(self, user_id, check_duration_ms=None, ads_found=0, ads_deleted=0):
        """Update user statistics"""
        try:
            stats = UserStats.query.filter_by(user_id=user_id).first()
            if not stats:
                stats = UserStats(user_id=user_id)
                db.session.add(stats)
            
            # Update stats
            stats.total_checks += 1
            stats.total_ads_found += ads_found
            stats.total_ads_deleted += ads_deleted
            stats.last_check_at = datetime.utcnow()
            
            if check_duration_ms:
                # Update performance metrics
                if stats.fastest_check_ms is None or check_duration_ms < stats.fastest_check_ms:
                    stats.fastest_check_ms = check_duration_ms
                
                if stats.slowest_check_ms is None or check_duration_ms > stats.slowest_check_ms:
                    stats.slowest_check_ms = check_duration_ms
                
                # Update average (simple moving average)
                if stats.avg_check_duration_ms == 0:
                    stats.avg_check_duration_ms = check_duration_ms
                else:
                    stats.avg_check_duration_ms = int(
                        (stats.avg_check_duration_ms * 0.8) + (check_duration_ms * 0.2)
                    )
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating stats for user {user_id}: {e}")
            return False
    
    def check_user_ads(self, user_id):
        """Check for new ads for a specific user"""
        try:
            start_time = datetime.utcnow()
            new_ads = []
            deleted_ads = []
            
            # Clear "NEW" tags from ads older than 6 hours
            # This gives users time to see new ads without them disappearing immediately
            six_hours_ago = datetime.now(timezone.utc) - timedelta(hours=6)
            old_new_ads = UserAd.query.filter(
                UserAd.user_id == user_id,
                UserAd.is_new == True,
                UserAd.marked_new_at < six_hours_ago
            ).update({'is_new': False})
            
            if old_new_ads > 0:
                logger.info(f"Cleared NEW tag from {old_new_ads} ads older than 6 hours for user {user_id}")
            
            # Get user's active keywords
            keywords = UserKeyword.query.filter_by(
                user_id=user_id,
                is_active=True
            ).all()
            
            logger.info(f"Checking ads for user {user_id} with {len(keywords)} keywords")
            
            for keyword_obj in keywords:
                keyword = keyword_obj.keyword
                
                # Get current ads from scraper
                try:
                    current_ads = self.scraper.search(keyword)
                    logger.info(f"Found {len(current_ads)} current ads for keyword '{keyword}'")
                except Exception as e:
                    logger.error(f"Failed to scrape ads for keyword '{keyword}': {e}")
                    continue
                
                # Get existing ads for this keyword (including deleted ones for resurrection logic)
                existing_ads = UserAd.query.filter_by(
                    user_id=user_id,
                    keyword_id=keyword_obj.id,
                    is_deleted=False
                ).all()
                
                # Also get deleted ads for this keyword to check for resurrection
                deleted_ads_for_keyword = UserAd.query.filter_by(
                    user_id=user_id,
                    keyword_id=keyword_obj.id,
                    is_deleted=True
                ).all()
                
                existing_ad_ids = {ad.ad_id for ad in existing_ads}
                current_ad_ids = {ad['id'] for ad in current_ads}
                deleted_ad_ids_for_keyword = {ad.ad_id for ad in deleted_ads_for_keyword}
                
                # Find ads to resurrect (were deleted but found again)
                resurrected_ad_ids = deleted_ad_ids_for_keyword & current_ad_ids
                
                # Resurrect deleted ads that are found again
                for deleted_ad in deleted_ads_for_keyword:
                    if deleted_ad.ad_id in resurrected_ad_ids:
                        logger.info(f"Resurrecting ad {deleted_ad.ad_id} for keyword '{keyword}'")
                        deleted_ad.is_deleted = False
                        deleted_ad.is_new = True
                        deleted_ad.marked_new_at = datetime.utcnow()
                        deleted_ad.scraped_at = datetime.utcnow()
                        
                        # Update ad data with current scraper results
                        current_ad_data = next((ad for ad in current_ads if ad['id'] == deleted_ad.ad_id), None)
                        if current_ad_data:
                            deleted_ad.title = current_ad_data.get('title', deleted_ad.title)
                            deleted_ad.description = current_ad_data.get('description', deleted_ad.description)
                            deleted_ad.price = current_ad_data.get('price', deleted_ad.price)
                            deleted_ad.link = current_ad_data.get('link', deleted_ad.link)
                            deleted_ad.image_url = current_ad_data.get('image_url', deleted_ad.image_url)
                            deleted_ad.date_added = current_ad_data.get('date_added', deleted_ad.date_added)
                            deleted_ad.date_added_parsed = UserAd.parse_czech_date(current_ad_data.get('date_added', ''))
                        
                        new_ads.append({
                            'keyword': keyword,
                            'ad': current_ad_data or deleted_ad.to_dict()
                        })
                
                # Update existing_ad_ids to include resurrected ads
                existing_ad_ids.update(resurrected_ad_ids)
                
                # Find new ads (in current results but not in existing or resurrected)
                new_ad_ids = current_ad_ids - existing_ad_ids
                
                for ad_data in current_ads:
                    if ad_data['id'] in new_ad_ids:
                        # Check if this ad already exists for this user (from other keywords)
                        existing_user_ad = UserAd.query.filter_by(
                            user_id=user_id,
                            ad_id=ad_data['id']
                        ).first()
                        
                        if existing_user_ad:
                            # Ad exists for another keyword, skip creating duplicate
                            continue
                            
                        
                        # Save new ad
                        date_added_str = ad_data.get('date_added', '')
                        current_time = datetime.utcnow()
                        user_ad = UserAd(
                            user_id=user_id,
                            keyword_id=keyword_obj.id,
                            ad_id=ad_data['id'],
                            title=ad_data.get('title', ''),
                            description=ad_data.get('description', ''),
                            price=ad_data.get('price', ''),
                            location=ad_data.get('location', ''),
                            seller_name=ad_data.get('seller_name', ''),
                            link=ad_data.get('link', ''),
                            image_url=ad_data.get('image_url', ''),
                            date_added=date_added_str,
                            date_added_parsed=UserAd.parse_czech_date(date_added_str),
                            scraped_at=current_time,
                            is_new=True,
                            marked_new_at=current_time
                        )
                        db.session.add(user_ad)
                        new_ads.append({
                            'keyword': keyword,
                            'ad': ad_data
                        })
                
                # Find deleted ads (active ads that are no longer in current results)
                deleted_ad_ids = existing_ad_ids - current_ad_ids
                for ad in existing_ads:
                    if ad.ad_id in deleted_ad_ids:
                        logger.info(f"Marking ad {ad.ad_id} as deleted for keyword '{keyword}'")
                        ad.is_deleted = True
                        deleted_ads.append({
                            'keyword': keyword,
                            'ad': ad.to_dict()
                        })
                
                # Update keyword last checked
                keyword_obj.last_checked = datetime.utcnow()
            
            # Commit with retry mechanism
            def _commit_changes():
                db.session.commit()
                return True
            
            try:
                retry_db_operation(_commit_changes)
                logger.info(f"Successfully committed {len(new_ads)} new ads and {len(deleted_ads)} deleted ads for user {user_id}")
            except Exception as commit_error:
                logger.error(f"Failed to commit changes for user {user_id}: {commit_error}")
                db.session.rollback()
                raise commit_error
            
            # Update user stats
            check_duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            self.update_user_stats(
                user_id=user_id,
                check_duration_ms=check_duration_ms,
                ads_found=len(new_ads),
                ads_deleted=len(deleted_ads)
            )
            
            logger.info(f"Check completed for user {user_id}: {len(new_ads)} new ads, {len(deleted_ads)} deleted ads")
            return True, new_ads, deleted_ads
            
        except Exception as e:
            
            import traceback
            traceback.print_exc()
            db.session.rollback()
            logger.error(f"Error checking ads for user {user_id}: {e}")
            return False, [], []
    
    def _format_uptime(self, seconds):
        """Format uptime in human readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"

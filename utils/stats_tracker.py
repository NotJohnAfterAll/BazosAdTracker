import os
import time
import json
from datetime import datetime


class StatsTracker:
    """
    Class for tracking system statistics and metrics
    """
    def __init__(self, stats_file="data/stats.json"):
        self.stats_file = stats_file
        self.stats = self._load_stats()
        self._ensure_stats_structure()
    
    def _ensure_stats_structure(self):
        """Ensure stats has the expected structure"""
        if "checks" not in self.stats:
            self.stats["checks"] = {
                "total": 0,
                "last_check": None,
                "avg_duration_ms": 0
            }
        
        if "ads" not in self.stats:
            self.stats["ads"] = {
                "total_found": 0,
                "total_deleted": 0,
                "by_keyword": {}
            }
        
        if "system" not in self.stats:
            self.stats["system"] = {
                "start_time": datetime.now().isoformat(),
                "uptime_seconds": 0,
                "restarts": 0
            }
    
    def _load_stats(self):
        """Load stats from file or create if doesn't exist"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, "r", encoding="utf-8-sig") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading stats file: {e}")
                return {}
        return {}
    
    def save_stats(self):
        """Save current stats to file"""
        try:
            os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving stats file: {e}")

    def reload_stats_from_file(self):
        """Force reload stats from file - important for multi-process environments"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, "r", encoding="utf-8-sig") as f:
                    file_stats = json.load(f)
                
                # Update memory stats with file data, preserving structure
                self.stats.update(file_stats)
                self._ensure_stats_structure()
                return True
            else:
                print(f"Stats file {self.stats_file} does not exist")
                return False
        except Exception as e:
            print(f"Error reloading stats from file: {e}")
            return False
    
    def record_check(self, duration_ms):
        """Record a completed check for ads"""
        self.stats["checks"]["total"] += 1
        self.stats["checks"]["last_check"] = datetime.now().isoformat()
        
        # Update average duration
        total = self.stats["checks"]["total"]
        current_avg = self.stats["checks"]["avg_duration_ms"]
        new_avg = ((current_avg * (total - 1)) + duration_ms) / total
        self.stats["checks"]["avg_duration_ms"] = round(new_avg, 2)
        
        self.save_stats()
    
    def record_ads_found(self, keyword, count):
        """Record ads found for a specific keyword"""
        self.stats["ads"]["total_found"] += count
        
        if keyword not in self.stats["ads"]["by_keyword"]:
            self.stats["ads"]["by_keyword"][keyword] = {
                "found": 0,
                "deleted": 0,
                "last_found": None
            }
        
        self.stats["ads"]["by_keyword"][keyword]["found"] += count
        self.stats["ads"]["by_keyword"][keyword]["last_found"] = datetime.now().isoformat()
        
        self.save_stats()
    
    def record_ads_deleted(self, keyword, count):
        """Record ads deleted for a specific keyword"""
        self.stats["ads"]["total_deleted"] += count
        
        if keyword not in self.stats["ads"]["by_keyword"]:
            self.stats["ads"]["by_keyword"][keyword] = {
                "found": 0, 
                "deleted": 0,
                "last_deleted": None
            }
        
        self.stats["ads"]["by_keyword"][keyword]["deleted"] += count
        self.stats["ads"]["by_keyword"][keyword]["last_deleted"] = datetime.now().isoformat()
        
        self.save_stats()
    
    def update_uptime(self):
        """Update system uptime"""
        start_time = datetime.fromisoformat(self.stats["system"]["start_time"])
        now = datetime.now()
        self.stats["system"]["uptime_seconds"] = int((now - start_time).total_seconds())
        self.save_stats()
    
    def record_system_start(self):
        """Record system start"""
        self.stats["system"]["restarts"] += 1
        self.save_stats()
    
    def remove_keyword_stats(self, keyword):
        """Remove all stats for a deleted keyword"""
        if keyword in self.stats["ads"]["by_keyword"]:
            keyword_stats = self.stats["ads"]["by_keyword"][keyword]
            
            # Subtract the keyword's stats from totals
            self.stats["ads"]["total_found"] -= keyword_stats.get("found", 0)
            self.stats["ads"]["total_deleted"] -= keyword_stats.get("deleted", 0)
            
            # Ensure totals don't go negative
            self.stats["ads"]["total_found"] = max(0, self.stats["ads"]["total_found"])
            self.stats["ads"]["total_deleted"] = max(0, self.stats["ads"]["total_deleted"])
            
            # Remove the keyword from stats
            del self.stats["ads"]["by_keyword"][keyword]
            
            print(f"Removed stats for keyword '{keyword}'")
            self.save_stats()
        else:
            print(f"No stats found for keyword '{keyword}' to remove")

    def get_stats(self):
        """Get current stats - always reload from file first for multi-process compatibility"""
        # Force reload from file to get latest stats from other processes (e.g., scheduler)
        self.reload_stats_from_file()
        
        self.update_uptime()
        
        # Note: Unique ads count calculation from JSON files is deprecated
        # The system now uses database storage, and individual user stats
        # are managed by the UserService class
        
        return self.stats
    
    def reset_uptime(self):
        """Reset system uptime and start time"""
        self.stats["system"]["start_time"] = datetime.now().isoformat()
        self.stats["system"]["uptime_seconds"] = 0
        print("System uptime reset")
        self.save_stats()
    
    def recalculate_stats_from_current_data(self, keywords_file="data/keywords.json", ads_file="data/ads.json"):
        """
        DEPRECATED: Recalculate and reset stats based on JSON files
        This method is kept for compatibility but should not be used.
        The system now uses database storage and individual user stats.
        """
        print("WARNING: recalculate_stats_from_current_data() is deprecated - system now uses database storage")
        return
        try:
            # Load current keywords
            current_keywords = []
            if os.path.exists(keywords_file):
                with open(keywords_file, "r", encoding="utf-8-sig") as f:
                    current_keywords = json.load(f)
            
            # Load current ads
            current_ads = {}
            if os.path.exists(ads_file):
                with open(ads_file, "r", encoding="utf-8-sig") as f:
                    current_ads = json.load(f)
            
            print("=" * 50)
            print("RECALCULATING STATS FROM CURRENT DATA")
            print("=" * 50)
            print(f"Current keywords: {current_keywords}")
            print(f"Current ads data keys: {list(current_ads.keys())}")
              # Reset ad stats
            unique_ads = set()  # Track unique ad IDs to avoid double counting
            new_by_keyword = {}
            
            # Calculate stats based on current actual data
            for keyword in current_keywords:
                if keyword in current_ads:
                    ad_count = len(current_ads[keyword])
                    
                    # Add unique ad IDs to the set
                    for ad in current_ads[keyword]:
                        if isinstance(ad, dict) and 'id' in ad:
                            unique_ads.add(ad['id'])
                    
                    new_by_keyword[keyword] = {
                        "found": ad_count,
                        "deleted": 0,  # Reset deleted count since we can't track historical deletions
                        "last_found": datetime.now().isoformat() if ad_count > 0 else None
                    }
                    print(f"Keyword '{keyword}': {ad_count} ads")
                else:
                    # Keyword exists but no ads found yet
                    new_by_keyword[keyword] = {
                        "found": 0,
                        "deleted": 0,
                        "last_found": None
                    }
                    print(f"Keyword '{keyword}': 0 ads")
            
            # Total unique ads count
            total_unique_ads = len(unique_ads)
            print(f"Total unique ads found: {total_unique_ads} (some ads may appear in multiple keywords)")
              # Update stats with recalculated values
            self.stats["ads"]["total_found"] = total_unique_ads
            self.stats["ads"]["total_deleted"] = 0  # Reset since we can't track historical deletions
            self.stats["ads"]["by_keyword"] = new_by_keyword
            
            print(f"Stats recalculated - Total unique ads: {total_unique_ads}")
            print("=" * 50)
            
            self.save_stats()
            return True
            
        except Exception as e:
            print(f"Error recalculating stats: {e}")
            return False
    
    def cleanup_invalid_keywords(self, valid_keywords):
        """Remove stats for keywords that no longer exist"""
        keywords_to_remove = []
        for keyword in self.stats["ads"]["by_keyword"]:
            if keyword not in valid_keywords:
                keywords_to_remove.append(keyword)
        
        for keyword in keywords_to_remove:
            print(f"Removing invalid keyword stats: {keyword}")
            self.remove_keyword_stats(keyword)

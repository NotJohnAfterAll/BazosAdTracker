"""
Database models for BazosChecker user system
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime
import json
import logging

db = SQLAlchemy()
bcrypt = Bcrypt()
logger = logging.getLogger(__name__)

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    keywords = db.relationship('UserKeyword', backref='user', lazy=True, cascade='all, delete-orphan')
    ads = db.relationship('UserAd', backref='user', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('UserFavorite', backref='user', lazy=True, cascade='all, delete-orphan')
    stats = db.relationship('UserStats', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Required for Flask-Login"""
        return str(self.id)
    
    def to_dict(self):
        """Convert user to dictionary for JSON responses"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'keywords_count': len(self.keywords),
            'ads_count': len(self.ads),
            'favorites_count': len(self.favorites)
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserKeyword(db.Model):
    """Keywords tracked by users"""
    __tablename__ = 'user_keywords'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    keyword = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_checked = db.Column(db.DateTime)
    
    # Unique constraint per user
    __table_args__ = (db.UniqueConstraint('user_id', 'keyword', name='unique_user_keyword'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'keyword': self.keyword,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None
        }
    
    def __repr__(self):
        return f'<UserKeyword {self.keyword} for User {self.user_id}>'

class UserAd(db.Model):
    """Ads found for users"""
    __tablename__ = 'user_ads'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    keyword_id = db.Column(db.Integer, db.ForeignKey('user_keywords.id'), nullable=False, index=True)
    
    # Ad data
    ad_id = db.Column(db.String(100), nullable=False)  # Original ad ID from Bazos
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    price = db.Column(db.String(100))
    location = db.Column(db.String(200))
    seller_name = db.Column(db.String(200))
    link = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    
    # Metadata
    date_added = db.Column(db.String(100))  # Date from Bazos (original format)
    date_added_parsed = db.Column(db.DateTime)  # Parsed date for sorting
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_new = db.Column(db.Boolean, default=True)
    marked_new_at = db.Column(db.DateTime, default=datetime.utcnow)  # When ad was marked as new
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Relationships
    keyword = db.relationship('UserKeyword', backref='ads')
    
    # Unique constraint per user and ad
    __table_args__ = (db.UniqueConstraint('user_id', 'ad_id', name='unique_user_ad'),)
    
    @staticmethod
    def parse_czech_date(date_str):
        """Parse Czech date format like '8.7. 2025' to datetime"""
        if not date_str or date_str in ['N/A', '', 'Date unknown']:
            return None
        
        try:
            # Handle Czech date format like "8.7. 2025"
            if '.' in date_str:
                # Remove extra spaces and split
                parts = date_str.strip().replace(' ', '').split('.')
                if len(parts) >= 3:
                    day = int(parts[0])
                    month = int(parts[1])
                    year = int(parts[2]) if parts[2] else datetime.utcnow().year
                    
                    # Create datetime object
                    return datetime(year, month, day)
        except (ValueError, IndexError) as e:
            # If parsing fails, return None
            logger.warning(f"Failed to parse date '{date_str}': {e}")
            return None
        
        return None

    def to_dict(self):
        return {
            'id': self.ad_id,  # Use ad_id as the primary identifier for frontend
            'db_id': self.id,  # Keep database ID for backend operations
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'location': self.location,
            'seller_name': self.seller_name,
            'link': self.link,
            'image': self.image_url,  # Map image_url to image for frontend compatibility
            'image_url': self.image_url,
            'date_added': self.date_added,
            'scraped_at': int(self.scraped_at.timestamp()) if self.scraped_at else None,
            'isNew': self.is_new,  # Map is_new to isNew for frontend
            'is_new': self.is_new,
            'is_deleted': self.is_deleted,
            'keyword': self.keyword.keyword if self.keyword else None
        }
    
    def __repr__(self):
        return f'<UserAd {self.ad_id} for User {self.user_id}>'

class UserFavorite(db.Model):
    """User's favorite ads"""
    __tablename__ = 'user_favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    ad_id = db.Column(db.Integer, db.ForeignKey('user_ads.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    ad = db.relationship('UserAd', backref='favorites')
    
    # Unique constraint per user and ad
    __table_args__ = (db.UniqueConstraint('user_id', 'ad_id', name='unique_user_favorite'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ad': self.ad.to_dict() if self.ad else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<UserFavorite Ad {self.ad_id} for User {self.user_id}>'

class UserStats(db.Model):
    """User statistics"""
    __tablename__ = 'user_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Statistics
    total_checks = db.Column(db.Integer, default=0)
    total_ads_found = db.Column(db.Integer, default=0)
    total_ads_deleted = db.Column(db.Integer, default=0)
    last_check_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Performance metrics
    avg_check_duration_ms = db.Column(db.Integer, default=0)
    fastest_check_ms = db.Column(db.Integer)
    slowest_check_ms = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'total_checks': self.total_checks,
            'total_ads_found': self.total_ads_found,
            'total_ads_deleted': self.total_ads_deleted,
            'last_check_at': self.last_check_at.isoformat() if self.last_check_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'avg_check_duration_ms': self.avg_check_duration_ms,
            'fastest_check_ms': self.fastest_check_ms,
            'slowest_check_ms': self.slowest_check_ms
        }
    
    def __repr__(self):
        return f'<UserStats for User {self.user_id}>'

class UserSession(db.Model):
    """User session tracking for security"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    ip_address = db.Column(db.String(45))  # Support IPv6
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref='sessions')
    
    def __repr__(self):
        return f'<UserSession {self.session_token[:8]}... for User {self.user_id}>'

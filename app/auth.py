"""
Authentication service for BazosChecker
Handles user registration, login, password management, and session security
"""
import os
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session, current_app
from flask_login import current_user, login_user, logout_user
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token, get_current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, UserSession
import re
import hashlib
import logging

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

class AuthService:
    """Service for handling authentication operations"""
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, "Password is valid"
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_username(username):
        """Validate username format"""
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 20:
            return False, "Username must be no more than 20 characters long"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        return True, "Username is valid"
    
    @staticmethod
    def register_user(username, email, password):
        """Register a new user"""
        try:
            # Validate input
            username_valid, username_msg = AuthService.validate_username(username)
            if not username_valid:
                return False, username_msg
            
            if not AuthService.validate_email(email):
                return False, "Invalid email format"
            
            password_valid, password_msg = AuthService.validate_password(password)
            if not password_valid:
                return False, password_msg
            
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                return False, "Username already exists"
            
            if User.query.filter_by(email=email).first():
                return False, "Email already registered"
            
            # Create new user
            user = User(
                username=username,
                email=email
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"New user registered: {username}")
            return True, "User registered successfully"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            return False, "Registration failed due to server error"
    
    @staticmethod
    def login_user_service(username_or_email, password, remember_me=False):
        """Login user and create session"""
        try:
            # Find user by username or email
            user = User.query.filter(
                (User.username == username_or_email) | 
                (User.email == username_or_email)
            ).first()
            
            if not user:
                return False, "Invalid username/email or password", None
            
            if not user.is_active:
                return False, "Account is disabled", None
            
            if not user.check_password(password):
                return False, "Invalid username/email or password", None
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Create Flask-Login session
            login_user(user, remember=remember_me)
            
            # Create JWT tokens
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            # Create session record
            session_token = secrets.token_urlsafe(32)
            user_session = UserSession(
                user_id=user.id,
                session_token=session_token,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                expires_at=datetime.utcnow() + timedelta(days=30 if remember_me else 1)
            )
            db.session.add(user_session)
            db.session.commit()
            
            logger.info(f"User logged in: {user.username}")
            return True, "Login successful", {
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token,
                'session_token': session_token
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Login error: {str(e)}")
            return False, "Login failed due to server error", None
    
    @staticmethod
    def logout_user_service(session_token=None):
        """Logout user and invalidate session"""
        try:
            # Logout from Flask-Login
            logout_user()
            
            # Invalidate session if provided
            if session_token:
                user_session = UserSession.query.filter_by(session_token=session_token).first()
                if user_session:
                    user_session.is_active = False
                    db.session.commit()
            
            logger.info("User logged out")
            return True, "Logout successful"
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return False, "Logout failed"
    
    @staticmethod
    def get_current_user():
        """Get current authenticated user"""
        if current_user.is_authenticated:
            return current_user
        return None
    
    @staticmethod
    def cleanup_expired_sessions():
        """Clean up expired sessions"""
        try:
            expired_sessions = UserSession.query.filter(
                UserSession.expires_at < datetime.utcnow()
            ).all()
            
            for session in expired_sessions:
                db.session.delete(session)
            
            db.session.commit()
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Session cleanup error: {str(e)}")

def require_auth(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        # Get the current user from JWT
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Convert string ID back to integer
        try:
            user_id = int(current_user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID'}), 401
        
        # Load the user object
        from app.models import User
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return jsonify({'error': 'User account not found or inactive'}), 401
            
        # Store current user in flask.g for access in the view
        from flask import g
        g.current_user = user
        
        return f(*args, **kwargs)
    return decorated_function

def require_verified_user(f):
    """Decorator to require verified user"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if not current_user.is_verified:
            return jsonify({'error': 'Account verification required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def rate_limit_auth(limit="5 per minute"):
    """Rate limiting decorator for auth endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Apply rate limiting
            return limiter.limit(limit)(f)(*args, **kwargs)
        return decorated_function
    return decorator

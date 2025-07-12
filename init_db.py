"""
Database initialization script for BazosChecker
Creates tables and handles migrations
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.models import db, User, UserKeyword, UserAd, UserFavorite, UserStats, UserSession

def setup_postgresql_support():
    """Setup PostgreSQL support before database initialization"""
    database_url = os.getenv('DATABASE_URL')
    
    # Fix URL format if needed
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        os.environ['DATABASE_URL'] = database_url
        print("✅ Fixed DATABASE_URL: postgres:// -> postgresql://")
    
    # Pre-load PostgreSQL modules if needed
    if database_url and 'postgresql' in database_url:
        try:
            import psycopg2
            import sqlalchemy.dialects.postgresql
            import sqlalchemy.dialects.postgresql.psycopg2
            from sqlalchemy.dialects import registry
            
            # Register dialect explicitly
            registry.register("postgresql", "sqlalchemy.dialects.postgresql", "dialect")
            registry.register("postgresql.psycopg2", "sqlalchemy.dialects.postgresql.psycopg2", "dialect")
            
            print(f"✅ PostgreSQL support loaded: psycopg2 {psycopg2.__version__}")
            return True
        except ImportError as e:
            print(f"❌ PostgreSQL import failed: {e}")
            return False
    return True

def create_app():
    """Create Flask app with database configuration"""
    app = Flask(__name__)
    
    # Setup PostgreSQL support first
    setup_postgresql_support()
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Fix URL format if needed (in case it wasn't fixed above)
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
            os.environ['DATABASE_URL'] = database_url
        
        # Production database (PostgreSQL via Coolify)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        print(f"✅ Using PostgreSQL database")
    else:
        # Development database (SQLite)
        # Use absolute path for SQLite
        base_dir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(base_dir, 'data', 'bazos_checker.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        print(f"✅ Using SQLite database: {db_path}")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Initialize extensions with enhanced error handling
    try:
        db.init_app(app)
        migrate = Migrate(app, db)
        print("✅ Database extensions initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    
    return app

def init_database():
    """Initialize database with tables"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False

def migrate_old_data():
    """Migrate data from old JSON files to new user system"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create a default admin user if no users exist
            if User.query.count() == 0:
                admin_user = User(
                    username='admin',
                    email='admin@localhost',
                    is_verified=True
                )
                admin_user.set_password('admin123')  # Default password - should be changed
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Default admin user created (username: admin, password: admin123)")
            
            # Try to migrate old keywords and ads
            import json
            from app.user_service import UserService
            
            keywords_file = 'data/keywords.json'
            ads_file = 'data/ads.json'
            
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                user_service = UserService()
                
                # Migrate keywords
                if os.path.exists(keywords_file):
                    with open(keywords_file, 'r', encoding='utf-8') as f:
                        old_keywords = json.load(f)
                    
                    for keyword in old_keywords:
                        user_service.add_user_keyword(admin_user.id, keyword)
                        print(f"✅ Migrated keyword: {keyword}")
                
                # Migrate ads
                if os.path.exists(ads_file):
                    with open(ads_file, 'r', encoding='utf-8') as f:
                        old_ads = json.load(f)
                    
                    for keyword, ads in old_ads.items():
                        # Find the keyword object
                        from app.models import UserKeyword
                        keyword_obj = UserKeyword.query.filter_by(
                            user_id=admin_user.id,
                            keyword=keyword
                        ).first()
                        
                        if keyword_obj:
                            # Convert old ad format to new format
                            new_ads = []
                            for ad in ads:
                                new_ads.append({
                                    'id': ad.get('id', ''),
                                    'title': ad.get('title', ''),
                                    'description': ad.get('description', ''),
                                    'price': ad.get('price', ''),
                                    'location': ad.get('location', ''),
                                    'seller_name': ad.get('seller_name', ''),
                                    'link': ad.get('link', ''),
                                    'image_url': ad.get('image_url', ''),
                                    'date_added': ad.get('date_added', '')
                                })
                            
                            user_service.save_user_ads(admin_user.id, keyword_obj.id, new_ads, mark_as_new=False)
                            print(f"✅ Migrated {len(new_ads)} ads for keyword: {keyword} (not marked as new)")
                
                print("✅ Data migration completed")
            
            return True
            
        except Exception as e:
            print(f"❌ Data migration failed: {e}")
            return False

if __name__ == '__main__':
    print("🔧 Initializing BazosChecker database...")
    
    try:
        # Setup PostgreSQL support first
        if not setup_postgresql_support():
            print("⚠️ PostgreSQL setup had issues, but continuing...")
        
        if init_database():
            print("🔄 Migrating old data...")
            migrate_old_data()
            print("✅ Database setup completed!")
        else:
            print("❌ Database setup failed!")
            exit(1)
            
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

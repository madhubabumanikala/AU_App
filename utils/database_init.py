"""
Database Initialization and Migration System
Automatically sets up database tables and default data on app startup
"""
from flask import current_app
from extensions import db
from models.user import Admin, Student
from models.event import Event
from models.social import Post
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with all required tables and default data"""
    try:
        # Create all tables from models
        db.create_all()
        
        # Check and create additional tables not in models
        create_additional_tables()
        
        # Create default admin account
        create_default_admin()
        
        # Commit all changes
        db.session.commit()
        
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        db.session.rollback()
        return False

def create_additional_tables():
    """Create additional tables that might not be in SQLAlchemy models"""
    
    # Create post_likes table
    db.engine.execute(text("""
        CREATE TABLE IF NOT EXISTS post_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            user_type VARCHAR(20) NOT NULL DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            UNIQUE(post_id, user_id, user_type)
        )
    """))
    
    # Create post_comments table
    db.engine.execute(text("""
        CREATE TABLE IF NOT EXISTS post_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            author_type VARCHAR(20) NOT NULL DEFAULT 'student',
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
        )
    """))
    
    # Create post_shares table
    db.engine.execute(text("""
        CREATE TABLE IF NOT EXISTS post_shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            user_type VARCHAR(20) NOT NULL DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
        )
    """))
    
    # Create indexes for performance
    try:
        db.engine.execute(text("CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author_id, author_type)"))
        db.engine.execute(text("CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at)"))
        db.engine.execute(text("CREATE INDEX IF NOT EXISTS idx_posts_is_active ON posts(is_active)"))
        db.engine.execute(text("CREATE INDEX IF NOT EXISTS idx_post_likes_post_id ON post_likes(post_id)"))
        db.engine.execute(text("CREATE INDEX IF NOT EXISTS idx_post_comments_post_id ON post_comments(post_id)"))
        db.engine.execute(text("CREATE INDEX IF NOT EXISTS idx_post_shares_post_id ON post_shares(post_id)"))
    except Exception as e:
        # Indexes might already exist, that's okay
        logger.debug(f"Index creation warning (likely already exists): {e}")

def create_default_admin():
    """Create default admin account if it doesn't exist"""
    
    # Check if admin already exists
    existing_admin = Admin.query.filter_by(email='admin@au.edu').first()
    if existing_admin:
        logger.info("Default admin account already exists")
        return
    
    # Create default admin
    admin = Admin(
        username='admin',
        first_name='System',
        last_name='Administrator',
        email='admin@au.edu',
        role='super_admin',
        department='Administration'
    )
    admin.set_password('admin123')
    
    db.session.add(admin)
    logger.info("Created default admin account: admin@au.edu / admin123")

def check_database_health():
    """Check if database is properly set up"""
    try:
        # Check if key tables exist
        admin_count = Admin.query.count()
        
        # Check if posts table exists and is accessible
        post_count = Post.query.count()
        
        logger.info(f"Database health check: {admin_count} admins, {post_count} posts")
        return True
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

def migrate_existing_database():
    """Handle migration of existing databases"""
    try:
        # Check if posts table has all required columns
        result = db.engine.execute(text("PRAGMA table_info(posts)")).fetchall()
        columns = [row[1] for row in result] if result else []
        
        # Add missing columns if needed
        required_columns = [
            'is_university_post', 'is_announcement', 'is_pinned',
            'likes_count', 'comments_count', 'shares_count',
            'visibility', 'views_count'
        ]
        
        for column in required_columns:
            if column not in columns:
                if 'count' in column:
                    db.engine.execute(text(f"ALTER TABLE posts ADD COLUMN {column} INTEGER DEFAULT 0"))
                elif column == 'visibility':
                    db.engine.execute(text(f"ALTER TABLE posts ADD COLUMN {column} VARCHAR(20) DEFAULT 'public'"))
                else:
                    db.engine.execute(text(f"ALTER TABLE posts ADD COLUMN {column} BOOLEAN DEFAULT 0"))
                
                logger.info(f"Added missing column: {column}")
        
        return True
        
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        return False

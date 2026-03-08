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
        # Create all tables from models first
        db.create_all()
        
        # Handle any missing columns in existing tables
        migrate_existing_database()
        
        # Check and create additional tables not in models
        create_additional_tables()
        
        # Create default admin account
        create_default_admin()
        
        # Commit all changes
        db.session.commit()
        
        print("SUCCESS: Database initialization completed successfully")
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        print(f"ERROR: Database initialization failed: {e}")
        logger.error(f"Database initialization failed: {e}")
        db.session.rollback()
        return False

def create_additional_tables():
    """Create additional tables that might not be in SQLAlchemy models"""
    
    with db.engine.connect() as conn:
        # Create post_likes table
        conn.execute(text("""
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
        conn.execute(text("""
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
        conn.execute(text("""
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
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author_id, author_type)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_posts_is_active ON posts(is_active)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_post_likes_post_id ON post_likes(post_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_post_comments_post_id ON post_comments(post_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_post_shares_post_id ON post_shares(post_id)"))
        except Exception as e:
            # Indexes might already exist, that's okay
            logger.debug(f"Index creation warning (likely already exists): {e}")
        
        conn.commit()

def create_default_admin():
    """Create default admin account if it doesn't exist"""
    
    # Check if admin already exists by email or username
    existing_admin_by_email = Admin.query.filter_by(email='admin@au.edu').first()
    existing_admin_by_username = Admin.query.filter_by(username='admin').first()
    
    # If admin exists by email, check password hash
    if existing_admin_by_email:
        hash_val = existing_admin_by_email.password_hash
        # Check for empty, null, or invalid hash
        if not hash_val or hash_val == '' or len(hash_val.strip()) < 10 or not hash_val.startswith(('pbkdf2:', 'scrypt:', 'bcrypt', '$2b$')):
            print(f"WARNING: Existing admin has invalid password hash: '{hash_val}', recreating...")
            db.session.delete(existing_admin_by_email)
            db.session.commit()
        else:
            print("SUCCESS: Default admin account already exists with valid hash")
            return
    
    # If different admin exists by username, check its hash too
    elif existing_admin_by_username:
        hash_val = existing_admin_by_username.password_hash
        if not hash_val or hash_val == '' or len(hash_val.strip()) < 10 or not hash_val.startswith(('pbkdf2:', 'scrypt:', 'bcrypt', '$2b$')):
            print(f"WARNING: Existing admin username has invalid password hash: '{hash_val}', recreating...")
            db.session.delete(existing_admin_by_username)
            db.session.commit()
        else:
            print("WARNING: Admin username already taken by different account with valid hash, skipping creation")
            return
    
    # Create default admin with proper password hash
    try:
        from werkzeug.security import generate_password_hash
        
        admin = Admin(
            username='admin',
            first_name='System',
            last_name='Administrator',
            email='admin@au.edu',
            role='super_admin',
            department='Administration',
            password_hash=generate_password_hash('admin123')
        )
        
        db.session.add(admin)
        db.session.flush()  # Check for constraint violations before commit
        print("✅ Created default admin account: admin@au.edu / admin123")
        logger.info("Created default admin account: admin@au.edu / admin123")
        
    except Exception as e:
        print(f"⚠️  Could not create admin account: {e}")
        logger.error(f"Admin creation failed: {e}")
        db.session.rollback()
        # Try to find existing admin that we can use
        existing_admin = Admin.query.first()
        if existing_admin:
            print(f"✅ Using existing admin account: {existing_admin.email}")
        else:
            print("❌ No admin account available - manual creation required")

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
        with db.engine.connect() as conn:
            # Check if posts table has all required columns
            result = conn.execute(text("PRAGMA table_info(posts)")).fetchall()
            columns = [row[1] for row in result] if result else []
            
            # Complete list of ALL Post model columns with proper types
            required_columns = {
                'content': 'TEXT NOT NULL',
                'media_type': 'VARCHAR(20)',
                'media_url': 'VARCHAR(255)',
                'media_thumbnail': 'VARCHAR(255)',
                'author_id': 'INTEGER NOT NULL',
                'author_type': 'VARCHAR(20) NOT NULL DEFAULT "student"',
                'event_id': 'INTEGER',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'is_active': 'BOOLEAN DEFAULT 1',
                'is_pinned': 'BOOLEAN DEFAULT 0',
                'is_university_post': 'BOOLEAN DEFAULT 0',
                'is_announcement': 'BOOLEAN DEFAULT 0',
                'visibility': 'VARCHAR(20) DEFAULT "public"',
                'likes_count': 'INTEGER DEFAULT 0',
                'comments_count': 'INTEGER DEFAULT 0',
                'shares_count': 'INTEGER DEFAULT 0',
                'views_count': 'INTEGER DEFAULT 0'
            }
            
            for column_name, column_def in required_columns.items():
                if column_name not in columns:
                    conn.execute(text(f"ALTER TABLE posts ADD COLUMN {column_name} {column_def}"))
                    print(f"✅ Added missing column: {column_name} ({column_def})")
                    logger.info(f"Added missing column: {column_name}")
                else:
                    print(f"✓ Column exists: {column_name}")
            
            # Also add foreign key constraint if missing
            try:
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_posts_event_id ON posts(event_id)"))
            except Exception as e:
                logger.debug(f"Index creation warning: {e}")
            
            conn.commit()
        
        return True
        
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        return False

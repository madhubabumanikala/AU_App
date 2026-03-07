#!/usr/bin/env python3
"""
Permanent Database Migration Script
Adds missing posts table to existing database
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Add posts table to existing database"""
    
    db_path = 'au_events.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking if posts table exists...")
        
        # Check if posts table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ Posts table already exists, checking schema...")
            
            # Check if is_university_post column exists
            cursor.execute("PRAGMA table_info(posts)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'is_university_post' not in columns:
                print("➕ Adding missing is_university_post column...")
                cursor.execute("ALTER TABLE posts ADD COLUMN is_university_post BOOLEAN DEFAULT 0")
            
            if 'is_announcement' not in columns:
                print("➕ Adding missing is_announcement column...")
                cursor.execute("ALTER TABLE posts ADD COLUMN is_announcement BOOLEAN DEFAULT 0")
                
            print("✅ Posts table schema updated!")
        else:
            print("➕ Creating posts table...")
            
            # Create complete posts table
            create_posts_table = """
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                media_type VARCHAR(20),
                media_url VARCHAR(255),
                media_thumbnail VARCHAR(255),
                author_id INTEGER NOT NULL,
                author_type VARCHAR(20) NOT NULL DEFAULT 'student',
                event_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                is_pinned BOOLEAN DEFAULT 0,
                is_university_post BOOLEAN DEFAULT 0,
                is_announcement BOOLEAN DEFAULT 0,
                visibility VARCHAR(20) DEFAULT 'public',
                likes_count INTEGER DEFAULT 0,
                comments_count INTEGER DEFAULT 0,
                shares_count INTEGER DEFAULT 0,
                views_count INTEGER DEFAULT 0,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE SET NULL
            )
            """
            
            cursor.execute(create_posts_table)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author_id, author_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_is_active ON posts(is_active)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_visibility ON posts(visibility)")
            
            print("✅ Posts table created successfully!")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("\n🎉 Database migration completed successfully!")
        print("✅ Your database now has the complete posts table schema")
        print("✅ Social media functionality should work perfectly")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting permanent database migration...")
    success = migrate_database()
    
    if success:
        print("\n✅ PERMANENT FIX COMPLETE!")
        print("The posts table is now properly defined in your database.")
        print("Restart your Flask app and everything should work.")
    else:
        print("\n❌ Migration failed! Please check the errors above.")

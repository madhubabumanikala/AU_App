#!/usr/bin/env python3
"""
Database migration script to add missing columns to posts table
Run this to fix the SQLAlchemy operational error
"""

import sqlite3
import sys
import os

def migrate_posts_table():
    """Add missing columns to posts table"""
    
    db_path = 'au_events.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking current posts table schema...")
        
        # Get current table info
        cursor.execute("PRAGMA table_info(posts)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # List of required columns that might be missing
        required_columns = [
            ('media_type', 'VARCHAR(20)'),
            ('media_url', 'VARCHAR(255)'),
            ('media_thumbnail', 'VARCHAR(255)'),
            ('author_id', 'INTEGER NOT NULL DEFAULT 1'),
            ('author_type', 'VARCHAR(20) NOT NULL DEFAULT "student"'),
            ('event_id', 'INTEGER'),
            ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
            ('updated_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
            ('is_active', 'BOOLEAN DEFAULT 1'),
            ('is_pinned', 'BOOLEAN DEFAULT 0'),
            ('is_university_post', 'BOOLEAN DEFAULT 0'),
            ('is_announcement', 'BOOLEAN DEFAULT 0'),
            ('visibility', 'VARCHAR(20) DEFAULT "public"'),
            ('likes_count', 'INTEGER DEFAULT 0'),
            ('comments_count', 'INTEGER DEFAULT 0'),
            ('shares_count', 'INTEGER DEFAULT 0'),
            ('views_count', 'INTEGER DEFAULT 0')
        ]
        
        # Add missing columns
        for col_name, col_type in required_columns:
            if col_name not in columns:
                print(f"➕ Adding missing column: {col_name}")
                try:
                    cursor.execute(f"ALTER TABLE posts ADD COLUMN {col_name} {col_type}")
                    print(f"✅ Added column: {col_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"⚠️  Column {col_name} already exists")
                    else:
                        print(f"❌ Error adding column {col_name}: {e}")
            else:
                print(f"✅ Column {col_name} already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify final schema
        print("\n🔍 Final posts table schema:")
        cursor.execute("PRAGMA table_info(posts)")
        final_columns = cursor.fetchall()
        for col in final_columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        print("\n✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting posts table migration...")
    success = migrate_posts_table()
    
    if success:
        print("\n🎉 Migration completed! You can now restart your Flask app.")
    else:
        print("\n💥 Migration failed! Please check the errors above.")
        sys.exit(1)

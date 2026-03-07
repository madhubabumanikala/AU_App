-- Fix posts table schema - Add missing columns
-- Run this SQL script to fix the database schema error

-- Add missing columns to posts table
ALTER TABLE posts ADD COLUMN is_university_post BOOLEAN DEFAULT 0;
ALTER TABLE posts ADD COLUMN is_announcement BOOLEAN DEFAULT 0;
ALTER TABLE posts ADD COLUMN media_type VARCHAR(20);
ALTER TABLE posts ADD COLUMN media_url VARCHAR(255);
ALTER TABLE posts ADD COLUMN media_thumbnail VARCHAR(255);
ALTER TABLE posts ADD COLUMN author_type VARCHAR(20) DEFAULT 'student';
ALTER TABLE posts ADD COLUMN visibility VARCHAR(20) DEFAULT 'public';
ALTER TABLE posts ADD COLUMN likes_count INTEGER DEFAULT 0;
ALTER TABLE posts ADD COLUMN comments_count INTEGER DEFAULT 0;
ALTER TABLE posts ADD COLUMN shares_count INTEGER DEFAULT 0;
ALTER TABLE posts ADD COLUMN views_count INTEGER DEFAULT 0;
ALTER TABLE posts ADD COLUMN is_pinned BOOLEAN DEFAULT 0;

-- Update existing posts with default values
UPDATE posts SET author_type = 'student' WHERE author_type IS NULL;
UPDATE posts SET visibility = 'public' WHERE visibility IS NULL;
UPDATE posts SET is_university_post = 0 WHERE is_university_post IS NULL;
UPDATE posts SET is_announcement = 0 WHERE is_announcement IS NULL;
UPDATE posts SET is_pinned = 0 WHERE is_pinned IS NULL;
UPDATE posts SET likes_count = 0 WHERE likes_count IS NULL;
UPDATE posts SET comments_count = 0 WHERE comments_count IS NULL;
UPDATE posts SET shares_count = 0 WHERE shares_count IS NULL;
UPDATE posts SET views_count = 0 WHERE views_count IS NULL;

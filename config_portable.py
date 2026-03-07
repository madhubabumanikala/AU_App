"""
Portable Configuration - Works on any system without path issues
"""

import os
import sys
from pathlib import Path

class PortableConfig:
    """Configuration that works on any system (Windows, Linux, Mac)"""
    
    def __init__(self):
        # Get the project root directory dynamically
        self.PROJECT_ROOT = Path(__file__).parent.absolute()
        
        # Database configuration (SQLite - portable)
        self.SQLALCHEMY_DATABASE_URI = f'sqlite:///{self.PROJECT_ROOT}/au_events.db'
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        
        # Flask configuration
        self.SECRET_KEY = 'au-events-secret-key-change-in-production'
        
        # Upload folders (dynamic paths)
        self.UPLOAD_FOLDER = self.PROJECT_ROOT / 'static' / 'uploads'
        self.QR_CODE_FOLDER = self.PROJECT_ROOT / 'static' / 'uploads' / 'qrcodes'
        
        # Email configuration (optional - can be set by environment variables)
        self.MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        self.MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
        self.MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
        self.MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
        self.MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
        
        # Flask-Login configuration
        self.LOGIN_DISABLED = False
        self.LOGIN_MESSAGE = 'Please log in to access this page.'
        self.LOGIN_MESSAGE_CATEGORY = 'info'
        
        # Ensure upload directories exist
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.UPLOAD_FOLDER,
            self.QR_CODE_FOLDER,
            self.PROJECT_ROOT / 'static' / 'css',
            self.PROJECT_ROOT / 'static' / 'js',
            self.PROJECT_ROOT / 'static' / 'images',
            self.PROJECT_ROOT / 'templates',
            self.PROJECT_ROOT / 'templates' / 'auth',
            self.PROJECT_ROOT / 'templates' / 'main',
            self.PROJECT_ROOT / 'templates' / 'main' / 'events',
            self.PROJECT_ROOT / 'templates' / 'admin',
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_absolute_path(self, relative_path):
        """Convert relative path to absolute path"""
        return self.PROJECT_ROOT / relative_path
    
    def __repr__(self):
        return f"PortableConfig(Root: {self.PROJECT_ROOT})"

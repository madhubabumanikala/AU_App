#!/usr/bin/env python3
"""
Quick Start - Bypass all checks and start Flask directly
"""

import sys
import os
from pathlib import Path

# Change to script directory
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)

print("=" * 50)
print("AU EVENT SYSTEM - QUICK START")
print("=" * 50)

try:
    print("🚀 Starting Flask application directly...")
    print("📱 Server will be available at: http://localhost:5000")
    print("🔑 Admin login: admin@au-events.com / admin123")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)
    
    # Import and run Flask app directly (no subprocess, runs in current terminal)
    from app import app
    print("✅ Flask app imported successfully")
    print("🌐 Starting server on http://localhost:5000...")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\n🔧 Run these commands in order:")
    print("1. pip install flask")
    print("2. pip install flask-sqlalchemy")
    print("3. pip install flask-login")
    print("4. pip install -r requirements.txt")
    print("\nThen run: python quick_start.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔧 Try manual startup:")
    print("python app.py")

print("\n" + "=" * 50)

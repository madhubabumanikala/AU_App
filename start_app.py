#!/usr/bin/env python3
"""
AU Event System Startup Script
This script checks system requirements and starts the application
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def print_header():
    print("=" * 60)
    print("AU Event Information System - Startup Script")
    print("=" * 60)

def check_python_version():
    """Check if Python version meets requirements"""
    print("\n1. Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.8+ required.")
        print("Please install Python 3.8 or higher from https://www.python.org/downloads/")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected - Compatible!")
    return True

def check_virtual_environment():
    """Check and create virtual environment if needed"""
    print("\n2. Checking virtual environment...")
    venv_path = Path("venv")
    
    if not venv_path.exists() or not (venv_path / "Scripts" / "python.exe").exists():
        print("❌ Virtual environment not found or corrupted")
        print("Creating new virtual environment...")
        
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✅ Virtual environment created successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            print("Please run: python -m venv venv")
            return False
    else:
        print("✅ Virtual environment exists!")
        return True

def install_dependencies():
    """Install required dependencies"""
    print("\n3. Installing dependencies...")
    
    # Determine the correct Python executable path
    if platform.system() == "Windows":
        python_exe = Path("venv") / "Scripts" / "python.exe"
        pip_exe = Path("venv") / "Scripts" / "pip.exe"
    else:
        python_exe = Path("venv") / "bin" / "python"
        pip_exe = Path("venv") / "bin" / "pip"
    
    if not python_exe.exists():
        print("❌ Virtual environment Python not found")
        return False
    
    try:
        # Upgrade pip first
        subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], check=True)
        
        # Install dependencies
        requirements_files = [
            "requirements.txt",
            "requirements_windows_fix.txt" if platform.system() == "Windows" else None
        ]
        
        for req_file in requirements_files:
            if req_file and Path(req_file).exists():
                print(f"Installing from {req_file}...")
                result = subprocess.run([str(pip_exe), "install", "-r", req_file], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"⚠️ Warning: Some packages from {req_file} failed to install")
                    print(result.stderr)
                else:
                    print(f"✅ Dependencies from {req_file} installed successfully!")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_database():
    """Check database configuration"""
    print("\n4. Checking database...")
    
    # Check if SQLite database exists (portable config)
    if Path("au_events.db").exists():
        print("✅ SQLite database found!")
        return True
    else:
        print("⚠️ Database not found - will be created on first run")
        return True

def check_config():
    """Check configuration files"""
    print("\n5. Checking configuration...")
    
    config_files = [
        "config_portable.py",
        "extensions.py",
        "config/config.py"
    ]
    
    missing_files = []
    for config_file in config_files:
        if not Path(config_file).exists():
            missing_files.append(config_file)
    
    if missing_files:
        print(f"❌ Missing configuration files: {', '.join(missing_files)}")
        return False
    
    print("✅ All configuration files present!")
    return True

def start_application():
    """Start the Flask application"""
    print("\n6. Starting application...")
    
    # Determine the correct Python executable path
    if platform.system() == "Windows":
        python_exe = Path("venv") / "Scripts" / "python.exe"
    else:
        python_exe = Path("venv") / "bin" / "python"
    
    try:
        print("🚀 Starting AU Event System...")
        print("📱 Application will be available at: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the application")
        print("-" * 60)
        
        # Start the application
        subprocess.run([str(python_exe), "app.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Application failed to start: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check the error messages above")
        print("2. Ensure all dependencies are installed")
        print("3. Check that port 5000 is not in use")
        print("4. Run 'python check_modules.py' to verify imports")

def show_troubleshooting():
    """Show troubleshooting information"""
    print("\n" + "=" * 60)
    print("TROUBLESHOOTING GUIDE")
    print("=" * 60)
    
    print("\n🔧 Common Issues and Solutions:")
    print("\n1. Python not found:")
    print("   - Install Python 3.8+ from https://www.python.org/downloads/")
    print("   - Make sure 'Add to PATH' is checked during installation")
    
    print("\n2. Virtual environment issues:")
    print("   - Delete 'venv' folder and run this script again")
    print("   - Or manually run: python -m venv venv")
    
    print("\n3. Dependency installation fails:")
    print("   - Run: venv/Scripts/pip install --upgrade pip")
    print("   - Try: venv/Scripts/pip install -r requirements_windows_fix.txt")
    
    print("\n4. Database errors:")
    print("   - The app uses SQLite by default (portable)")
    print("   - Database will be created automatically on first run")
    
    print("\n5. Port 5000 already in use:")
    print("   - Close other applications using port 5000")
    print("   - Or modify the port in app.py")
    
    print("\n📞 For more help:")
    print("   - Check README.md for detailed setup instructions")
    print("   - Check WINDOWS_SETUP.md for Windows-specific setup")
    print("   - Run 'python check_modules.py' to test module imports")

def main():
    """Main startup routine"""
    print_header()
    
    # Change to script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    all_checks_passed = True
    
    # Run all checks
    checks = [
        check_python_version,
        check_virtual_environment,
        install_dependencies,
        check_database,
        check_config
    ]
    
    for check in checks:
        if not check():
            all_checks_passed = False
            break
    
    if all_checks_passed:
        print("\n✅ All system checks passed!")
        start_application()
    else:
        print("\n❌ System checks failed!")
        show_troubleshooting()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

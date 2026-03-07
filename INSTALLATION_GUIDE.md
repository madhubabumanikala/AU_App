# Installation Guide - AU Event System

## ⚠️ Python Version Compatibility Issue

You're getting this error because **Python 3.14 is too new** and many packages haven't been updated to support it yet.

## 🚀 Recommended Solutions

### Option 1: Use Python 3.11.15 (Recommended)

1. **Install Python 3.11.15** (most compatible):
   ```bash
   # Download from python.org
   # https://www.python.org/downloads/release/python-31115/
   ```

2. **Create virtual environment**:
   ```bash
   # Windows (after installing Python 3.11.15)
   python -m venv venv
   
   # If python doesn't work, try:
   py -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   python3.11 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements_python311.txt
   ```

### Option 2: Use Python 3.10 (Most Stable)

1. **Install Python 3.10**:
   ```bash
   # Download from python.org
   # https://www.python.org/downloads/release/python-31012/
   ```

2. **Create virtual environment**:
   ```bash
   python3.10 -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements_python310.txt
   ```

### Option 3: Fix Current Python 3.14 (Advanced)

If you must use Python 3.14, try these steps:

1. **Update pip first**:
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Install packages individually** (some may fail):
   ```bash
   pip install Flask==2.3.3
   pip install Flask-SQLAlchemy==3.0.5
   pip install Flask-Login==0.6.3
   pip install Flask-WTF==1.1.1
   pip install Flask-Mail==0.9.1
   pip install PyMySQL==1.1.0
   pip install bcrypt==4.0.1
   pip install WTForms==3.0.1
   pip install Werkzeug==2.3.7
   pip install email-validator==2.0.0
   pip install python-dotenv==1.0.0
   
   # These might fail with Python 3.14
   pip install --no-cache-dir Pillow==10.0.1
   pip install --no-cache-dir qrcode==7.4.2
   pip install --no-cache-dir python-socketio==5.8.0
   pip install --no-cache-dir Flask-SocketIO==5.3.6
   ```

3. **If Pillow fails**:
   ```bash
   # Try installing without version
   pip install --no-cache-dir Pillow
   ```

4. **If SocketIO fails**:
   ```bash
   # Install older version
   pip install --no-cache-dir python-socketio==5.3.0
   pip install --no-cache-dir Flask-SocketIO==5.3.0
   ```

## 🔧 Quick Fix Commands

### For Windows Users:
```cmd
# Install Python 3.11.15 from python.org first
# Then run (use python or py command):
python -m venv venv
# or if that doesn't work:
py -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements_python311.txt
```

### For Linux/Mac Users:
```bash
# Install Python 3.11.15
sudo apt install python3.11 python3.11-venv  # Ubuntu/Debian
# or brew install python@3.11  # macOS

python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements_python311.txt
```

## 📋 Check Your Python Version

```bash
python --version
# Should be 3.10, 3.11, or 3.12 for best compatibility
```

## 🐛 Common Issues & Solutions

### Issue: "Failed to build Pillow"
**Solution**: Use Python 3.11 or install Pillow separately:
```bash
pip install --no-cache-dir Pillow
```

### Issue: "Microsoft Visual C++ 14.0 required"
**Solution**: Install Visual Studio Build Tools or use Python 3.11

### Issue: "bcrypt installation failed"
**Solution**: 
```bash
pip install bcrypt==4.0.1 --no-cache-dir
```

## 🎯 Best Practice

**Use Python 3.11.15** for this project. It's the most stable and compatible version for all the packages we're using.

## 📞 Still Having Issues?

1. Check Python version: `python --version`
2. Update pip: `python -m pip install --upgrade pip`
3. Use Python 3.11: Download from python.org
4. Follow the installation guide step by step

The project will work perfectly with Python 3.11.15!

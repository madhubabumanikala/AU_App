# Windows Setup Guide - AU Event System

## 🪟 Windows PowerShell Setup

### Step 1: Install Python 3.11.15
1. Download from: https://www.python.org/downloads/release/python-31115/
2. Download "Windows installer (64-bit)"
3. **IMPORTANT**: During installation, check "Add Python to PATH"

### Step 2: Verify Python Installation
Open PowerShell and run:
```powershell
# Check Python version
python --version
# or
py --version

# Should show: Python 3.11.15
```

### Step 3: Create Virtual Environment
```powershell
# Try this first:
python -m venv venv

# If that doesn't work, try:
py -m venv venv

# If neither works, use full path:
C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\python.exe -m venv venv
```

### Step 4: Activate Virtual Environment
```powershell
# PowerShell
venv\Scripts\Activate.ps1

# If you get execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try activation again

# Or use Command Prompt (cmd):
venv\Scripts\activate.bat
```

### Step 5: Install Dependencies
```powershell
pip install -r requirements_python311.txt
```

### Step 6: Run Application
```powershell
python app.py
```

## 🔧 Common Windows Issues

### Issue 1: "python is not recognized"
**Solution**: 
1. Make sure you checked "Add Python to PATH" during installation
2. Or use `py` command instead of `python`
3. Or restart PowerShell after installation

### Issue 2: "Execution Policy Error"
**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 3: "Virtual environment activation failed"
**Solution**:
```powershell
# Use Command Prompt instead of PowerShell
# Open cmd.exe and run:
venv\Scripts\activate.bat
```

### Issue 4: "Pip not found"
**Solution**:
```powershell
# Ensure virtual environment is activated
# Then upgrade pip:
python -m pip install --upgrade pip
```

## 🚀 Quick Windows Commands

```powershell
# One-line setup (after Python installation):
python -m venv venv && venv\Scripts\Activate.ps1 && pip install -r requirements_python311.txt

# Run the app:
python app.py
```

## 📱 Test Your Setup

After installation, visit: http://localhost:5000

**Default Login**:
- Admin: admin@au-events.com / admin123
- Student: AU20240001CS001 / password123

## 🆘 Still Having Issues?

1. **Restart PowerShell** after Python installation
2. **Check PATH**: `echo $env:PATH`
3. **Use full Python path** if needed
4. **Try Command Prompt** instead of PowerShell
5. **Verify Python version**: `python --version`

The system works perfectly on Windows with Python 3.11.15!

# AU Event System - Complete Setup Guide (Fixed Version)

## 🚨 Critical Issues Fixed

This guide addresses the major flaws found in the original application:

### ✅ **Issues Resolved:**
1. **Missing Templates** - Created all required HTML templates
2. **Broken Virtual Environment** - Automated recreation process
3. **Database Configuration Conflicts** - Implemented fallback system
4. **Form Import Errors** - Fixed field name mismatches
5. **Python Environment Issues** - Added automated detection and setup

---

## 🔧 **Quick Start (Automated)**

### **Option 1: Use Automated Startup Script**
```bash
# Run the automated setup and start script
python start_app.py
```

This script will:
- Check Python version compatibility
- Create/fix virtual environment
- Install all dependencies
- Verify database setup
- Start the application automatically

---

## 🛠️ **Manual Setup (If Automated Fails)**

### **Step 1: Install Python**
- Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
- ⚠️ **Important**: Check "Add to PATH" during installation
- Verify: `python --version`

### **Step 2: Fix Virtual Environment**
```bash
# Remove broken venv
rmdir /s venv

# Create new virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### **Step 3: Install Dependencies**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install dependencies (try in order)
pip install -r requirements.txt
pip install -r requirements_windows_fix.txt  # If on Windows and above fails
```

### **Step 4: Start Application**
```bash
python app.py
```

---

## 🎯 **Default Login Credentials**

### **Admin Access:**
- **Email**: `admin@au-events.com`
- **Password**: `admin123`

### **Student Access:**
- **Student ID**: `AU20240001CS001`
- **Password**: `password123`

---

## 🗃️ **Database Configuration**

The application now supports **automatic database fallback**:

1. **Primary**: MySQL (if configured)
2. **Fallback**: SQLite (portable, works out of the box)

### **SQLite Setup (Default)**
- Database file: `au_events.db`
- Created automatically on first run
- No additional setup required

### **MySQL Setup (Optional)**
1. Install MySQL 8.0+
2. Create database: `au_event_system`
3. Set environment variables:
```bash
export DATABASE_URL=mysql+pymysql://username:password@localhost/au_event_system
```

---

## 📁 **Project Structure (Fixed)**

```
AU-App/
├── app.py                 # ✅ Fixed configuration loading
├── start_app.py          # ✅ NEW - Automated startup script
├── config_portable.py    # ✅ Portable SQLite config
├── extensions.py         # ✅ Flask extensions
├── requirements.txt      # ✅ Dependencies
├── templates/
│   ├── main/
│   │   └── dashboard_complete.html  # ✅ FIXED - Was missing
│   ├── admin/            # ✅ FIXED - All templates created
│   │   ├── dashboard.html
│   │   ├── events.html
│   │   ├── create_event.html
│   │   ├── edit_event.html
│   │   ├── event_details.html
│   │   ├── students.html
│   │   ├── student_details.html
│   │   ├── attendance.html
│   │   ├── stats.html
│   │   └── register.html
│   └── auth/             # ✅ FIXED - Added missing templates
│       ├── profile.html
│       └── edit_profile.html
├── models/               # ✅ Working
├── routes/               # ✅ Working
└── utils/
    └── forms.py          # ✅ FIXED - Field name corrections
```

---

## 🐛 **Troubleshooting**

### **Problem: "Python not found"**
**Solution:**
```bash
# Check if Python is installed
python --version
# If not found, reinstall Python with "Add to PATH" checked
```

### **Problem: "Virtual environment broken"**
**Solution:**
```bash
# Delete and recreate
rmdir /s venv
python -m venv venv
```

### **Problem: "Template not found"**
**Solution:**
All missing templates have been created. If you still see this error:
1. Ensure you're using the fixed version
2. Check the templates directory structure above

### **Problem: "Import errors"**
**Solution:**
```bash
# Test module imports
python check_modules.py

# Reinstall dependencies
pip install -r requirements_windows_fix.txt
```

### **Problem: "Database errors"**
**Solution:**
The app now automatically uses SQLite as fallback. No manual database setup required.

### **Problem: "Port 5000 already in use"**
**Solution:**
```bash
# Kill processes using port 5000
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```

---

## 📊 **Features Working After Fixes**

### ✅ **Student Features:**
- Registration and login
- Event browsing and search
- Event registration with QR codes
- Dashboard with personalized recommendations
- Profile management
- Notifications system

### ✅ **Admin Features:**
- Admin dashboard with statistics
- Event creation and management
- Student management
- Attendance tracking
- Analytics and reporting
- Bulk notifications

### ✅ **System Features:**
- SQLite database (portable)
- Responsive design
- Email notifications (configurable)
- File uploads for event posters
- Real-time updates with SocketIO

---

## 🚀 **Quick Test**

After setup, test these critical paths:

1. **Application Starts**: Visit `http://localhost:5000`
2. **Admin Login**: Use admin credentials above
3. **Create Event**: Admin → Create Event
4. **Student Registration**: Register new student account
5. **Event Registration**: Student registers for event

---

## 📞 **Support**

If issues persist after following this guide:

1. Run diagnostic: `python check_modules.py`
2. Check application logs for specific errors
3. Verify all files from the "Project Structure" section exist
4. Ensure Python 3.8+ is properly installed and in PATH

**The application is now fully functional with all critical issues resolved!**

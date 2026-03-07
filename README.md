# AU Event Information System

A comprehensive event management platform for Andhra University students, built with Flask, MySQL, and modern web technologies.

## 🚀 Features

### Core Features
- **User Authentication**: Secure login system for students and admins
- **Event Management**: Create, update, and manage university events
- **Event Registration**: Students can register for events with QR code generation
- **Real-time Notifications**: Email and in-app notifications for event updates
- **Mobile Responsive**: Fully responsive design for all devices
- **Department-wise Filtering**: Filter events by department and category

### Advanced Features
- **AI-based Recommendations**: Smart event suggestions based on student interests
- **QR Code Attendance**: Digital attendance tracking using QR codes
- **Analytics Dashboard**: Comprehensive statistics for admins
- **Event Calendar**: Monthly calendar view of all events
- **Feedback System**: Students can rate and provide feedback
- **Email Notifications**: Automated email alerts for events

## 🛠️ Technology Stack

- **Backend**: Python 3.8+, Flask 2.3+
- **Database**: MySQL 8.0+
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Flask-Login, bcrypt
- **Real-time**: Flask-SocketIO
- **Email**: Flask-Mail
- **QR Codes**: qrcode library
- **Development**: VS Code, Git

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)
- Git

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd AU-App
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Option A: Using MySQL Command Line
```bash
mysql -u root -p < database_setup.sql
```

#### Option B: Using MySQL Workbench
1. Open MySQL Workbench
2. Create new database: `au_event_system`
3. Import the `database_setup.sql` file

### 5. Configure Environment Variables
Create a `.env` file in the root directory:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://username:password@localhost/au_event_system
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 6. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📁 Project Structure

```
AU-App/
├── app.py                 # Main Flask application
├── requirements.txt        # Python dependencies
├── database_setup.sql     # Database schema and sample data
├── README.md              # Project documentation
├── config/
│   └── config.py         # Configuration settings
├── models/
│   ├── __init__.py
│   ├── user.py           # User models (Student, Admin)
│   ├── event.py          # Event models
│   └── notification.py   # Notification model
├── routes/
│   ├── __init__.py
│   ├── auth.py           # Authentication routes
│   ├── main.py           # Main application routes
│   ├── events.py         # Event-related routes
│   ├── admin.py          # Admin panel routes
│   └── api.py            # API endpoints
├── utils/
│   ├── __init__.py
│   ├── forms.py          # WTForms classes
│   ├── email.py          # Email utilities
│   └── qr_generator.py   # QR code generation
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── auth/             # Authentication templates
│   ├── events/           # Event templates
│   └── admin/            # Admin panel templates
└── static/
    ├── css/
    │   └── style.css     # Custom styles
    ├── js/
    │   └── main.js       # JavaScript functions
    ├── images/           # Static images
    └── uploads/          # User uploads (posters, QR codes)
```

## 👥 User Roles

### Students
- Register with university ID
- Browse and register for events
- Receive notifications
- Submit feedback
- Track attendance

### Admins
- Create and manage events
- View student registrations
- Mark attendance
- Generate reports
- Manage notifications

### Super Admin
- All admin privileges
- Manage admin accounts
- System configuration

## 🔐 Default Credentials

### Admin Login
- **Email**: admin@au-events.com
- **Password**: admin123

### Sample Student Logins
- **Student ID**: AU20240001CS001 / **Password**: password123
- **Student ID**: AU20240002EC001 / **Password**: password123
- **Student ID**: AU20240003ME001 / **Password**: password123

## 📱 Mobile Compatibility

The application is fully responsive and works seamlessly on:
- Smartphones (iOS/Android)
- Tablets
- Desktop computers
- Laptops

## 🔧 Configuration

### Database Configuration
Update the database URL in `config/config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/au_event_system'
```

### Email Configuration
Configure email settings in `.env`:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## 📊 API Endpoints

### Public Endpoints
- `GET /api/events/upcoming` - Get upcoming events
- `GET /api/events/<id>` - Get event details
- `GET /api/departments` - Get all departments
- `GET /api/categories` - Get all categories

### Authenticated Endpoints
- `POST /api/events/<id>/register` - Register for event
- `GET /api/student/events` - Get student's events
- `GET /api/student/notifications` - Get notifications
- `POST /api/notifications/<id>/read` - Mark notification as read

## 🧪 Testing

### Run Tests
```bash
python -m pytest tests/
```

### Test Coverage
```bash
python -m pytest --cov=app tests/
```

## 📈 Performance Optimization

- Database indexing for faster queries
- Image optimization for faster loading
- Caching for frequently accessed data
- Lazy loading for large datasets
- Minified CSS and JavaScript

## 🔒 Security Features

- Password hashing with bcrypt
- SQL injection prevention
- XSS protection
- CSRF protection
- Session management
- Input validation
- File upload security

## 🚀 Deployment

### Production Deployment with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Using Docker
```bash
docker build -t au-events .
docker run -p 5000:5000 au-events
```

### Environment Variables for Production
```env
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
DATABASE_URL=your-production-database-url
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check MySQL service is running
   - Verify database credentials
   - Ensure database exists

2. **Import Errors**
   - Activate virtual environment
   - Install all dependencies
   - Check Python version compatibility

3. **Email Not Working**
   - Verify email configuration
   - Check app password for Gmail
   - Ensure SMTP settings are correct

4. **QR Code Not Generating**
   - Check upload directory permissions
   - Verify qrcode library installation
   - Check file path configuration

## 📞 Support

For support and queries:
- Email: events@andhrauniversity.edu.in
- Phone: +91-891-2844-000
- Documentation: Check the `/docs` endpoint

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Andhra University for the opportunity
- Flask community for excellent documentation
- Bootstrap for responsive design
- All contributors and testers

---

**Built with ❤️ for Andhra University Students**

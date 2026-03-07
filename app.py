from flask import Flask
import os

# Try to import config, fallback to portable config if needed
try:
    from config.config import config
except ImportError:
    # Fallback to portable config if main config fails
    config = {
        'default': None,
        'development': None,
        'production': None,
        'testing': None
    }

# Import extensions
from extensions import db, login_manager, mail, socketio

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    
    # Use portable config if main config is not available
    if config[config_name] is None:
        from config_portable import PortableConfig
        portable_config = PortableConfig()
        for key, value in vars(portable_config).items():
            if not key.startswith('_'):
                app.config[key] = value
    else:
        app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import Student, Admin
        # Try to load as student first
        student = Student.query.get(int(user_id))
        if student:
            return student
        
        # Try to load as admin
        admin = Admin.query.get(int(user_id))
        return admin
    
    # Create upload directories if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['QR_CODE_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.events import events_bp
    from routes.admin import admin_bp
    from routes.api import api_bp
    from routes.social import social_bp
    from routes.debug import debug_bp
    from routes.tasks import tasks_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(events_bp, url_prefix='/events')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(social_bp, url_prefix='/social')
    app.register_blueprint(debug_bp)
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    
    # Add mobile context processor
    from utils.mobile_detector import mobile_context_processor
    app.context_processor(mobile_context_processor)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

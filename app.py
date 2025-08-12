import os
import logging
from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from translations import get_text, get_available_languages

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Flask-Mail configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# initialize extensions
db.init_app(app)
login_manager.init_app(app)
mail.init_app(app)
csrf.init_app(app)

login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    
    # Create owner account if it doesn't exist
    from models import User
    from werkzeug.security import generate_password_hash
    
    # Check if any admin user exists
    admin_user = User.query.filter_by(is_admin=True).first()
    if not admin_user:
        # Create default admin user - user should change credentials
        admin_user = User(
            username='Admin',
            email='admin@portfolio.com',
            password_hash=generate_password_hash('changeme123'),
            is_admin=True,
            about_me='Portfolio administrator'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin account created successfully. Email: admin@portfolio.com, Password: changeme123")

# Add translation function to Jinja2 context
@app.context_processor
def inject_translations():
    lang = session.get('language', 'en')
    return {
        't': lambda key: get_text(key, lang),
        'current_lang': lang,
        'available_languages': get_available_languages()
    }

# Import routes
from routes import *

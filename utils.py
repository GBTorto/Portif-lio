import os
import secrets
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app, url_for
from flask_mail import Message
from app import mail

ALLOWED_EXTENSIONS = {
    'images': {'png', 'jpg', 'jpeg', 'gif'},
    'videos': {'mp4', 'webm', 'ogg'},
    'documents': {'pdf', 'doc', 'docx'}
}

def allowed_file(filename, file_type='images'):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(file_type, set())

def save_uploaded_file(file, subfolder, max_size=(800, 600)):
    """
    Save uploaded file to the uploads directory with proper security measures
    """
    if not file or not allowed_file(file.filename):
        return None
    
    # Create subfolder if it doesn't exist
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_path, exist_ok=True)
    
    # Generate secure filename
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    
    # Add random string to prevent conflicts
    random_hex = secrets.token_hex(8)
    filename = f"{name}_{random_hex}{ext}"
    
    file_path = os.path.join(upload_path, filename)
    
    try:
        # Save the file
        file.save(file_path)
        
        # If it's an image, resize it
        if ext.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
            resize_image(file_path, max_size)
        
        # Return the relative path for database storage
        return os.path.join(subfolder, filename)
    
    except Exception as e:
        current_app.logger.error(f"Error saving file: {e}")
        return None

def resize_image(file_path, max_size=(800, 600)):
    """
    Resize image to fit within max_size while maintaining aspect ratio
    """
    try:
        with Image.open(file_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Calculate new size maintaining aspect ratio
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save the resized image
            img.save(file_path, optimize=True, quality=85)
    
    except Exception as e:
        current_app.logger.error(f"Error resizing image: {e}")

def send_notification_email(project, comment, user):
    """
    Send email notification to the owner when a new comment is posted
    """
    try:
        subject = f"New comment on your project: {project.title}"
        
        body = f"""
Hi Gabriel,

You have received a new comment on your project "{project.title}".

Comment by: {user.username} ({user.email})
Comment: {comment.content}

You can view and manage this comment by logging into your admin dashboard.

Project URL: {url_for('project_detail', id=project.id, _external=True)}
Admin Dashboard: {url_for('admin_dashboard', _external=True)}

Best regards,
Your Portfolio System
        """
        
        msg = Message(
            subject=subject,
            recipients=['moraisgabriel867@gmail.com'],
            body=body
        )
        
        mail.send(msg)
        current_app.logger.info(f"Notification email sent for project {project.id}")
        
    except Exception as e:
        current_app.logger.error(f"Error sending notification email: {e}")

def format_date(date):
    """
    Format date for display
    """
    if date:
        return date.strftime('%B %Y')
    return 'Present'

def truncate_text(text, length=100):
    """
    Truncate text to specified length with ellipsis
    """
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'

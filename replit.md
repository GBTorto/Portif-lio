# Gabriel Morais Portfolio

## Overview

This is a personal portfolio website built with Flask that showcases Gabriel Morais's projects, achievements, and professional experience. The application serves as a comprehensive platform for displaying work samples, providing detailed project information, and enabling visitor interaction through comments and likes. It features both public-facing portfolio pages and an administrative interface for content management.

## User Preferences

Preferred communication style: Simple, everyday language.
Translation functionality: Removed per user request.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templating with Flask for server-side rendering
- **UI Framework**: Bootstrap 5 with dark theme variant for responsive design
- **Icons**: Font Awesome 6.4.0 for consistent iconography
- **JavaScript**: Vanilla JavaScript with Bootstrap components for interactivity
- **Custom Styling**: CSS customizations for portfolio-specific branding and animations

### Backend Architecture
- **Web Framework**: Flask with modular structure separating concerns
- **Database ORM**: SQLAlchemy with declarative base for database operations
- **Authentication**: Flask-Login for session management and user authentication
- **Form Handling**: WTForms with Flask-WTF for form validation and CSRF protection
- **File Management**: Werkzeug utilities for secure file uploads and processing
- **Image Processing**: PIL (Pillow) for image resizing and optimization

### Data Architecture
- **Database**: SQLAlchemy with SQLite default (configurable via DATABASE_URL)
- **Models**: User, Project, Category, Tag, Achievement, Experience, AboutMe, Comment, Like
- **Relationships**: Many-to-many associations between projects/achievements and tags
- **File Storage**: Local file system with organized upload directories

### Authentication & Authorization
- **User Management**: Email-based registration with password hashing
- **Admin System**: Role-based access control with is_admin flag
- **Password Security**: Werkzeug password hashing with reset token system
- **Session Management**: Flask-Login with remember_me functionality

### Content Management System
- **Project Management**: Full CRUD operations with image/video uploads
- **Achievement Tracking**: Certification and accomplishment showcase
- **Experience Timeline**: Work history and education management
- **Portfolio Customization**: Editable about page with skills and resume
- **Publishing System**: Draft/published status for content control

## External Dependencies

### Email Services
- **Flask-Mail**: Email functionality for password resets and notifications
- **SMTP Configuration**: Gmail SMTP with TLS encryption
- **Environment Variables**: MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD for secure configuration

### File Upload System
- **Upload Management**: Configurable upload folder with 16MB size limit
- **Security**: File type validation and secure filename generation
- **Image Processing**: Automatic resizing with PIL for web optimization

### Frontend Libraries
- **Bootstrap 5**: CSS framework via CDN with dark theme
- **Font Awesome 6**: Icon library for UI enhancement
- **JavaScript**: Bootstrap components for modals, tooltips, and responsive behavior

### Development Configuration
- **Environment Variables**: SESSION_SECRET, DATABASE_URL for secure deployment
- **Proxy Handling**: ProxyFix middleware for reverse proxy compatibility
- **Debug Mode**: Configurable debug settings for development vs production

### Database Configuration
- **Connection Pooling**: SQLAlchemy engine options with pool_recycle and pool_pre_ping
- **Migration Ready**: Declarative base structure prepared for Alembic migrations
- **Flexible Backend**: Environment-based database URL configuration supporting multiple database types
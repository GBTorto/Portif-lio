from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    about_me = db.Column(db.Text)
    profile_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Password reset token
    reset_token = db.Column(db.String(100))
    reset_token_expires = db.Column(db.DateTime)
    
    # Relationships
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic')
    
    def __init__(self, username, email, password_hash, is_admin=False, about_me=None, profile_image=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.about_me = about_me
        self.profile_image = profile_image

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    projects = db.relationship('Project', backref='category', lazy='dynamic')
    achievements = db.relationship('Achievement', backref='category', lazy='dynamic')
    experiences = db.relationship('Experience', backref='category', lazy='dynamic')

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    
    def __init__(self, name):
        self.name = name

# Association table for many-to-many relationship between projects and tags
project_tags = db.Table('project_tags',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

# Association table for achievements and tags
achievement_tags = db.Table('achievement_tags',
    db.Column('achievement_id', db.Integer, db.ForeignKey('achievement.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

# Association table for experiences and tags
experience_tags = db.Table('experience_tags',
    db.Column('experience_id', db.Integer, db.ForeignKey('experience.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    demo_link = db.Column(db.String(255))
    github_link = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    video_url = db.Column(db.String(255))
    is_published = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    
    # Relationships
    tags = db.relationship('Tag', secondary=project_tags, lazy='subquery',
                          backref=db.backref('projects', lazy=True))
    comments = db.relationship('Comment', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, title, description, demo_link=None, github_link=None, 
                 image_url=None, video_url=None, is_published=True, 
                 is_featured=False, category_id=None):
        self.title = title
        self.description = description
        self.demo_link = demo_link
        self.github_link = github_link
        self.image_url = image_url
        self.video_url = video_url
        self.is_published = is_published
        self.is_featured = is_featured
        self.category_id = category_id
    
    @property
    def like_count(self):
        return self.likes.count()
    
    @property
    def comment_count(self):
        return self.comments.count()

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_achieved = db.Column(db.Date, nullable=False)
    image_url = db.Column(db.String(255))
    certificate_url = db.Column(db.String(255))
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    
    # Relationships
    tags = db.relationship('Tag', secondary=achievement_tags, lazy='subquery',
                          backref=db.backref('achievements', lazy=True))
    
    def __init__(self, title, description, date_achieved, image_url=None,
                 certificate_url=None, is_published=True, category_id=None):
        self.title = title
        self.description = description
        self.date_achieved = date_achieved
        self.image_url = image_url
        self.certificate_url = certificate_url
        self.is_published = is_published
        self.category_id = category_id

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)  # Nullable for current positions
    location = db.Column(db.String(100))
    is_current = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    
    # Relationships
    tags = db.relationship('Tag', secondary=experience_tags, lazy='subquery',
                          backref=db.backref('experiences', lazy=True))
    
    def __init__(self, title, company, description, start_date, end_date=None,
                 location=None, is_current=False, is_published=True, category_id=None):
        self.title = title
        self.company = company
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.location = location
        self.is_current = is_current
        self.is_published = is_published
        self.category_id = category_id

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    def __init__(self, content, user_id, project_id, is_approved=True):
        self.content = content
        self.user_id = user_id
        self.project_id = project_id
        self.is_approved = is_approved

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    def __init__(self, user_id, project_id):
        self.user_id = user_id
        self.project_id = project_id
    
    # Unique constraint to prevent duplicate likes
    __table_args__ = (db.UniqueConstraint('user_id', 'project_id', name='unique_user_project_like'),)

class AboutMe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    profile_image = db.Column(db.String(255))
    resume_url = db.Column(db.String(255))
    skills = db.Column(db.Text)  # JSON string of skills
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, content, profile_image=None, resume_url=None, skills=None):
        self.content = content
        self.profile_image = profile_image
        self.resume_url = resume_url
        self.skills = skills

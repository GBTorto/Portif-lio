from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectField, DateField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, URL
from wtforms.widgets import TextArea
from models import Category, Tag

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', 
                            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', 
                            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', 
                                   validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class ProfileForm(FlaskForm):
    username = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=64)])
    about_me = TextAreaField('About Me', validators=[Optional(), Length(max=500)])
    profile_image = FileField('Profile Image', validators=[
        Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Update Profile')

class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    demo_link = StringField('Demo Link', validators=[Optional(), URL()])
    github_link = StringField('GitHub Link', validators=[Optional(), URL()])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    tags = StringField('Tags (comma-separated)', validators=[Optional()])
    image = FileField('Project Image', validators=[
        Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    video = FileField('Project Video', validators=[
        Optional(), FileAllowed(['mp4', 'webm', 'ogg'], 'Videos only!')
    ])
    is_published = BooleanField('Publish immediately')
    is_featured = BooleanField('Featured project')
    submit = SubmitField('Save Project')
    
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        from models import Category
        self.category_id.choices = [('0', 'No Category')] + [
            (str(c.id), c.name) for c in Category.query.all()
        ]

class AchievementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    date_achieved = DateField('Date Achieved', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    tags = StringField('Tags (comma-separated)', validators=[Optional()])
    image = FileField('Achievement Image', validators=[
        Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    certificate = FileField('Certificate', validators=[
        Optional(), FileAllowed(['pdf', 'jpg', 'png', 'jpeg'], 'PDFs and Images only!')
    ])
    is_published = BooleanField('Publish immediately')
    submit = SubmitField('Save Achievement')
    
    def __init__(self, *args, **kwargs):
        super(AchievementForm, self).__init__(*args, **kwargs)
        from models import Category
        self.category_id.choices = [('0', 'No Category')] + [
            (str(c.id), c.name) for c in Category.query.all()
        ]

class ExperienceForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(max=100)])
    company = StringField('Company', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    is_current = BooleanField('Currently working here')
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    tags = StringField('Tags (comma-separated)', validators=[Optional()])
    is_published = BooleanField('Publish immediately')
    submit = SubmitField('Save Experience')
    
    def __init__(self, *args, **kwargs):
        super(ExperienceForm, self).__init__(*args, **kwargs)
        from models import Category
        self.category_id.choices = [('0', 'No Category')] + [
            (str(c.id), c.name) for c in Category.query.all()
        ]

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Category')

class AboutMeForm(FlaskForm):
    content = TextAreaField('About Me Content', validators=[DataRequired()], 
                           widget=TextArea(), render_kw={"rows": 10})
    skills = TextAreaField('Skills (one per line)', validators=[Optional()], 
                          render_kw={"rows": 5})
    profile_image = FileField('Profile Image', validators=[
        Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    resume = FileField('Resume PDF', validators=[
        Optional(), FileAllowed(['pdf'], 'PDF files only!')
    ])
    submit = SubmitField('Update About Me')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Post Comment')

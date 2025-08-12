import os
import secrets
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app, send_from_directory, session, render_template_string
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Message
from sqlalchemy import or_, desc
from app import app, db, mail
from models import *
from forms import *
from utils import allowed_file, save_uploaded_file, send_notification_email

@app.route('/set_language/<language>')
def set_language(language=None):
    session['language'] = language
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    # Get featured projects
    featured_projects = Project.query.filter_by(is_published=True, is_featured=True).limit(3).all()
    
    # Get recent projects
    recent_projects = Project.query.filter_by(is_published=True).order_by(desc(Project.created_at)).limit(6).all()
    
    # Get sorting preference from query params
    sort_by = request.args.get('sort', 'recent')
    
    if sort_by == 'popular':
        # Sort by likes count
        projects = Project.query.filter_by(is_published=True).join(Like, isouter=True).group_by(Project.id).order_by(desc(func.count(Like.id))).limit(6).all()
    else:
        projects = recent_projects
    
    return render_template('index.html', 
                         featured_projects=featured_projects, 
                         projects=projects,
                         sort_by=sort_by)

@app.route('/about')
def about():
    about_me = AboutMe.query.first()
    achievements = Achievement.query.filter_by(is_published=True).order_by(desc(Achievement.date_achieved)).all()
    experiences = Experience.query.filter_by(is_published=True).order_by(desc(Experience.start_date)).all()
    
    return render_template('about.html', 
                         about_me=about_me,
                         achievements=achievements,
                         experiences=experiences)

@app.route('/portfolio')
def portfolio():
    # Get filter parameters
    category_id = request.args.get('category', type=int)
    tag_name = request.args.get('tag')
    search = request.args.get('search', '')
    
    # Base query
    query = Project.query.filter_by(is_published=True)
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if tag_name:
        query = query.join(Project.tags).filter(Tag.name == tag_name)
    
    if search:
        query = query.filter(or_(
            Project.title.contains(search),
            Project.description.contains(search)
        ))
    
    projects = query.order_by(desc(Project.created_at)).all()
    categories = Category.query.all()
    tags = Tag.query.all()
    
    return render_template('portfolio.html', 
                         projects=projects,
                         categories=categories,
                         tags=tags,
                         current_category=category_id,
                         current_tag=tag_name,
                         search=search)

@app.route('/project/<int:id>')
def project_detail(id):
    project = Project.query.get_or_404(id)
    
    # Only show published projects to non-admin users
    if not project.is_published and (not current_user.is_authenticated or not current_user.is_admin):
        flash('Project not found.', 'error')
        return redirect(url_for('portfolio'))
    
    comments = Comment.query.filter_by(project_id=id, is_approved=True).order_by(desc(Comment.created_at)).all()
    comment_form = CommentForm()
    
    # Check if current user liked this project
    user_liked = False
    if current_user.is_authenticated:
        user_liked = Like.query.filter_by(user_id=current_user.id, project_id=id).first() is not None
    
    return render_template('project_detail.html', 
                         project=project,
                         comments=comments,
                         comment_form=comment_form,
                         user_liked=user_liked)

@app.route('/project/<int:id>/like', methods=['POST'])
@login_required
def like_project(id):
    project = Project.query.get_or_404(id)
    
    # Check if user already liked this project
    existing_like = Like.query.filter_by(user_id=current_user.id, project_id=id).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        liked = False
        message = 'Project unliked'
    else:
        # Like
        like = Like(user_id=current_user.id, project_id=id)
        db.session.add(like)
        liked = True
        message = 'Project liked!'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'liked': liked,
        'like_count': project.like_count,
        'message': message
    })

@app.route('/project/<int:id>/comment', methods=['POST'])
@login_required
def comment_project(id):
    project = Project.query.get_or_404(id)
    
    # Handle both form submissions and AJAX requests
    if request.content_type == 'application/json' or request.is_json:
        data = request.get_json()
        content = data.get('content', '').strip()
    else:
        form = CommentForm()
        if not form.validate_on_submit():
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'message': 'Invalid form data'})
            flash('Error posting comment. Please try again.', 'error')
            return redirect(url_for('project_detail', id=id))
        content = form.content.data.strip()
    
    if not content:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': 'Comment cannot be empty'})
        flash('Comment cannot be empty.', 'error')
        return redirect(url_for('project_detail', id=id))
    
    comment = Comment(
        content=content,
        user_id=current_user.id,
        project_id=id
    )
    db.session.add(comment)
    db.session.commit()
    
    if request.headers.get('Content-Type') == 'application/json':
        # Return JSON response for AJAX requests
        comment_html = render_template_string('''
            <div class="comment mb-4 pb-3 border-bottom" data-aos="fade-in">
                <div class="d-flex">
                    <div class="me-3">
                        <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center" 
                             style="width: 40px; height: 40px;">
                            <i class="fas fa-user text-white"></i>
                        </div>
                    </div>
                    <div class="flex-grow-1">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <h6 class="mb-0">{{ comment.author.username }}</h6>
                            <small class="text-muted">Just now</small>
                        </div>
                        <p class="mb-0">{{ comment.content }}</p>
                    </div>
                </div>
            </div>
        ''', comment=comment)
        
        return jsonify({
            'success': True,
            'message': 'Comment posted successfully!',
            'comment_html': comment_html
        })
    else:
        flash('Your comment has been posted!', 'success')
        return redirect(url_for('project_detail', id=id))

@app.route('/share_project/<int:id>')
def share_project(id):
    project = Project.query.get_or_404(id)
    
    # Generate LinkedIn share URL
    linkedin_url = f"https://www.linkedin.com/sharing/share-offsite/?url={request.host_url}project/{id}"
    
    return redirect(linkedin_url)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if email already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'error')
            return render_template('auth/register.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generate reset token
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # Send reset email
            try:
                msg = Message(
                    'Password Reset Request',
                    recipients=[user.email],
                    body=f'''To reset your password, visit the following link:
{url_for('reset_password', token=token, _external=True)}

If you did not make this request, simply ignore this email.

This link will expire in 1 hour.
'''
                )
                mail.send(msg)
                flash('A password reset link has been sent to your email.', 'info')
            except Exception as e:
                flash('Error sending email. Please try again later.', 'error')
                app.logger.error(f"Email sending error: {e}")
        else:
            flash('Email not found.', 'error')
    
    return render_template('auth/forgot_password.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or user.reset_token_expires < datetime.utcnow():
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.password.data)
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        
        flash('Your password has been reset!', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/reset_password.html', form=form)

# Profile routes
@app.route('/profile')
@login_required
def profile():
    return render_template('profile_enhanced.html', user=current_user)

@app.route('/profile/<int:user_id>')
def view_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('profile_enhanced.html', user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.linkedin_url = form.linkedin_url.data
        current_user.github_url = form.github_url.data
        current_user.website_url = form.website_url.data
        current_user.twitter_url = form.twitter_url.data
        current_user.instagram_url = form.instagram_url.data
        
        # Handle profile image upload
        if form.profile_image.data:
            filename = save_uploaded_file(form.profile_image.data, 'profiles')
            if filename:
                current_user.profile_image = filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    # Pre-populate form
    form.username.data = current_user.username
    form.about_me.data = current_user.about_me
    form.linkedin_url.data = current_user.linkedin_url
    form.github_url.data = current_user.github_url
    form.website_url.data = current_user.website_url
    form.twitter_url.data = current_user.twitter_url
    form.instagram_url.data = current_user.instagram_url
    
    return render_template('edit_profile.html', form=form)

@app.route('/add_social_network', methods=['POST'])
@login_required
def add_social_network():
    form = SocialNetworkForm()
    if form.validate_on_submit():
        network = SocialNetwork(
            name=form.name.data,
            url=form.url.data,
            icon=form.icon.data or 'fas fa-link',
            user_id=current_user.id
        )
        db.session.add(network)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Social network added successfully!'})
    
    return jsonify({'success': False, 'message': 'Please fill in all required fields.'})

@app.route('/remove_social_network/<int:network_id>', methods=['DELETE'])
@login_required
def remove_social_network(network_id):
    network = SocialNetwork.query.filter_by(id=network_id, user_id=current_user.id).first()
    if network:
        db.session.delete(network)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Social network removed successfully!'})
    
    return jsonify({'success': False, 'message': 'Social network not found.'})

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    # Get statistics
    total_projects = Project.query.count()
    total_achievements = Achievement.query.count()
    total_experiences = Experience.query.count()
    total_users = User.query.count()
    recent_comments = Comment.query.order_by(desc(Comment.created_at)).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_projects=total_projects,
                         total_achievements=total_achievements,
                         total_experiences=total_experiences,
                         total_users=total_users,
                         recent_comments=recent_comments)

@app.route('/admin/change_password', methods=['GET', 'POST'])
@login_required
def admin_change_password():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.current_password.data):
            current_user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Current password is incorrect.', 'error')
    
    return render_template('admin/change_password.html', form=form)

# Admin project management
@app.route('/admin/projects')
@login_required
def admin_projects():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    projects = Project.query.order_by(desc(Project.created_at)).all()
    return render_template('admin/manage_projects.html', projects=projects)

@app.route('/admin/projects/new', methods=['GET', 'POST'])
@login_required
def admin_new_project():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            description=form.description.data,
            demo_link=form.demo_link.data,
            github_link=form.github_link.data,
            category_id=form.category_id.data if form.category_id.data else None,
            is_published=form.is_published.data,
            is_featured=form.is_featured.data
        )
        
        # Handle file uploads
        if form.image.data:
            filename = save_uploaded_file(form.image.data, 'projects')
            if filename:
                project.image_url = filename
        
        if form.video.data:
            filename = save_uploaded_file(form.video.data, 'projects')
            if filename:
                project.video_url = filename
        
        # Handle tags
        if form.tags.data:
            tag_names = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                project.tags.append(tag)
        
        db.session.add(project)
        db.session.commit()
        
        flash('Project created successfully!', 'success')
        return redirect(url_for('admin_projects'))
    
    return render_template('admin/edit_project.html', form=form, project=None)

@app.route('/admin/projects/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_project(id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    project = Project.query.get_or_404(id)
    form = ProjectForm()
    
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.demo_link = form.demo_link.data
        project.github_link = form.github_link.data
        project.category_id = form.category_id.data if form.category_id.data else None
        project.is_published = form.is_published.data
        project.is_featured = form.is_featured.data
        project.updated_at = datetime.utcnow()
        
        # Handle file uploads
        if form.image.data:
            filename = save_uploaded_file(form.image.data, 'projects')
            if filename:
                project.image_url = filename
        
        if form.video.data:
            filename = save_uploaded_file(form.video.data, 'projects')
            if filename:
                project.video_url = filename
        
        # Handle tags
        project.tags.clear()
        if form.tags.data:
            tag_names = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                project.tags.append(tag)
        
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('admin_projects'))
    
    # Pre-populate form
    form.title.data = project.title
    form.description.data = project.description
    form.demo_link.data = project.demo_link
    form.github_link.data = project.github_link
    form.category_id.data = project.category_id
    form.is_published.data = project.is_published
    form.is_featured.data = project.is_featured
    form.tags.data = ', '.join([tag.name for tag in project.tags])
    
    return render_template('admin/edit_project.html', form=form, project=project)

@app.route('/admin/projects/<int:id>/delete', methods=['POST'])
@login_required
def admin_delete_project(id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('admin_projects'))

# Admin achievement management (similar structure to projects)
@app.route('/admin/achievements')
@login_required
def admin_achievements():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    achievements = Achievement.query.order_by(desc(Achievement.date_achieved)).all()
    return render_template('admin/manage_achievements.html', achievements=achievements)

@app.route('/admin/achievements/new', methods=['GET', 'POST'])
@login_required
def admin_new_achievement():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    form = AchievementForm()
    if form.validate_on_submit():
        achievement = Achievement(
            title=form.title.data,
            description=form.description.data,
            date_achieved=form.date_achieved.data,
            category_id=form.category_id.data if form.category_id.data else None,
            is_published=form.is_published.data
        )
        
        # Handle file uploads
        if form.image.data:
            filename = save_uploaded_file(form.image.data, 'achievements')
            if filename:
                achievement.image_url = filename
        
        if form.certificate.data:
            filename = save_uploaded_file(form.certificate.data, 'achievements')
            if filename:
                achievement.certificate_url = filename
        
        # Handle tags
        if form.tags.data:
            tag_names = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                achievement.tags.append(tag)
        
        db.session.add(achievement)
        db.session.commit()
        
        flash('Achievement created successfully!', 'success')
        return redirect(url_for('admin_achievements'))
    
    return render_template('admin/edit_achievement.html', form=form, achievement=None)

@app.route('/admin/achievements/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_achievement(id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    achievement = Achievement.query.get_or_404(id)
    form = AchievementForm()
    
    if form.validate_on_submit():
        achievement.title = form.title.data
        achievement.description = form.description.data
        achievement.date_achieved = form.date_achieved.data
        achievement.category_id = form.category_id.data if form.category_id.data else None
        achievement.is_published = form.is_published.data
        
        # Handle file uploads
        if form.image.data:
            filename = save_uploaded_file(form.image.data, 'achievements')
            if filename:
                achievement.image_url = filename
        
        if form.certificate.data:
            filename = save_uploaded_file(form.certificate.data, 'achievements')
            if filename:
                achievement.certificate_url = filename
        
        # Handle tags
        achievement.tags.clear()
        if form.tags.data:
            tag_names = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                achievement.tags.append(tag)
        
        db.session.commit()
        flash('Achievement updated successfully!', 'success')
        return redirect(url_for('admin_achievements'))
    
    # Pre-populate form
    form.title.data = achievement.title
    form.description.data = achievement.description
    form.date_achieved.data = achievement.date_achieved
    form.category_id.data = achievement.category_id
    form.is_published.data = achievement.is_published
    form.tags.data = ', '.join([tag.name for tag in achievement.tags])
    
    return render_template('admin/edit_achievement.html', form=form, achievement=achievement)

@app.route('/admin/achievements/<int:id>/delete', methods=['POST'])
@login_required
def admin_delete_achievement(id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    achievement = Achievement.query.get_or_404(id)
    db.session.delete(achievement)
    db.session.commit()
    
    flash('Achievement deleted successfully!', 'success')
    return redirect(url_for('admin_achievements'))

# Admin experience management
@app.route('/admin/experiences')
@login_required
def admin_experiences():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    experiences = Experience.query.order_by(desc(Experience.start_date)).all()
    return render_template('admin/manage_experiences.html', experiences=experiences)

@app.route('/admin/experiences/new', methods=['GET', 'POST'])
@login_required
def admin_new_experience():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    form = ExperienceForm()
    if form.validate_on_submit():
        experience = Experience(
            title=form.title.data,
            company=form.company.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data if not form.is_current.data else None,
            location=form.location.data,
            is_current=form.is_current.data,
            category_id=form.category_id.data if form.category_id.data else None,
            is_published=form.is_published.data
        )
        
        # Handle tags
        if form.tags.data:
            tag_names = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                experience.tags.append(tag)
        
        db.session.add(experience)
        db.session.commit()
        
        flash('Experience created successfully!', 'success')
        return redirect(url_for('admin_experiences'))
    
    return render_template('admin/edit_experience.html', form=form, experience=None)

@app.route('/admin/experiences/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_experience(id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    experience = Experience.query.get_or_404(id)
    form = ExperienceForm()
    
    if form.validate_on_submit():
        experience.title = form.title.data
        experience.company = form.company.data
        experience.description = form.description.data
        experience.start_date = form.start_date.data
        experience.end_date = form.end_date.data if not form.is_current.data else None
        experience.location = form.location.data
        experience.is_current = form.is_current.data
        experience.category_id = form.category_id.data if form.category_id.data else None
        experience.is_published = form.is_published.data
        
        # Handle tags
        experience.tags.clear()
        if form.tags.data:
            tag_names = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                experience.tags.append(tag)
        
        db.session.commit()
        flash('Experience updated successfully!', 'success')
        return redirect(url_for('admin_experiences'))
    
    # Pre-populate form
    form.title.data = experience.title
    form.company.data = experience.company
    form.description.data = experience.description
    form.start_date.data = experience.start_date
    form.end_date.data = experience.end_date
    form.location.data = experience.location
    form.is_current.data = experience.is_current
    form.category_id.data = experience.category_id
    form.is_published.data = experience.is_published
    form.tags.data = ', '.join([tag.name for tag in experience.tags])
    
    return render_template('admin/edit_experience.html', form=form, experience=experience)

@app.route('/admin/experiences/<int:id>/delete', methods=['POST'])
@login_required
def admin_delete_experience(id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    experience = Experience.query.get_or_404(id)
    db.session.delete(experience)
    db.session.commit()
    
    flash('Experience deleted successfully!', 'success')
    return redirect(url_for('admin_experiences'))

# Admin about me management
@app.route('/admin/about', methods=['GET', 'POST'])
@login_required
def admin_edit_about():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    about_me = AboutMe.query.first()
    if not about_me:
        about_me = AboutMe(content='', skills='')
        db.session.add(about_me)
        db.session.commit()
    
    form = AboutMeForm()
    
    if form.validate_on_submit():
        about_me.content = form.content.data
        about_me.skills = form.skills.data
        about_me.updated_at = datetime.utcnow()
        
        # Handle file uploads
        if form.profile_image.data:
            filename = save_uploaded_file(form.profile_image.data, 'about')
            if filename:
                about_me.profile_image = filename
        
        if form.resume.data:
            filename = save_uploaded_file(form.resume.data, 'about')
            if filename:
                about_me.resume_url = filename
        
        db.session.commit()
        flash('About Me section updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    # Pre-populate form
    form.content.data = about_me.content
    form.skills.data = about_me.skills
    
    return render_template('admin/edit_about.html', form=form, about_me=about_me)

# File serving route
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

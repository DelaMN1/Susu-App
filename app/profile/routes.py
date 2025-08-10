from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User

# Create blueprint
profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/settings')
@login_required
def settings():
    """Profile settings page"""
    return render_template('profile/settings.html', user=current_user)


@profile_bp.route('/settings', methods=['POST'])
@login_required
def update_settings():
    """Update user profile settings"""
    try:
        # Get form data
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Update basic info
        if full_name and full_name != current_user.full_name:
            current_user.full_name = full_name
        
        if email and email != current_user.email:
            # Check if email is already taken
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != current_user.id:
                flash('Email address is already in use.', 'error')
                return redirect(url_for('profile.settings'))
            current_user.email = email
        
        if phone and phone != current_user.phone:
            # Check if phone is already taken
            existing_user = User.query.filter_by(phone=phone).first()
            if existing_user and existing_user.id != current_user.id:
                flash('Phone number is already in use.', 'error')
                return redirect(url_for('profile.settings'))
            current_user.phone = phone
        
        # Update password if provided
        if current_password and new_password and confirm_password:
            if not current_user.verify_password(current_password):
                flash('Current password is incorrect.', 'error')
                return redirect(url_for('profile.settings'))
            
            if new_password != confirm_password:
                flash('New passwords do not match.', 'error')
                return redirect(url_for('profile.settings'))
            
            if len(new_password) < 6:
                flash('Password must be at least 6 characters long.', 'error')
                return redirect(url_for('profile.settings'))
            
            current_user.password = new_password
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating your profile.', 'error')
    
    return redirect(url_for('profile.settings')) 
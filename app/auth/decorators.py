from functools import wraps
from flask import request, session, g, current_app, flash, redirect, url_for
from flask_login import current_user, login_user
from app.models import User
from app.supabase_client import get_supabase_client
import logging

logger = logging.getLogger(__name__)

def supabase_auth_required(f):
    """
    Decorator that checks for Supabase JWT token in Authorization header
    and validates it server-side. Falls back to session-based auth.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for Bearer token in Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                # Validate token with Supabase
                supabase = get_supabase_client()
                user_data = supabase.auth.get_user(token)
                
                if user_data.user:
                    # Find or create local user
                    local_user = User.find_by_supabase_id(user_data.user.id)
                    if not local_user:
                        # Create local user profile if doesn't exist
                        local_user = User(
                            supabase_id=user_data.user.id,
                            email=user_data.user.email,
                            full_name=user_data.user.user_metadata.get('full_name', 'Unknown'),
                            phone=user_data.user.phone or ''
                        )
                        from app.extensions import db
                        db.session.add(local_user)
                        db.session.commit()
                    
                    # Set current user
                    g.current_user = local_user
                    if not current_user.is_authenticated:
                        login_user(local_user)
                    
                    return f(*args, **kwargs)
                else:
                    flash('Invalid authentication token', 'error')
                    return redirect(url_for('auth.login'))
                    
            except Exception as e:
                logger.error(f"Supabase token validation failed: {e}")
                flash('Authentication failed', 'error')
                return redirect(url_for('auth.login'))
        
        # Fallback to session-based auth
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        
        flash('Please log in to access this page', 'error')
        return redirect(url_for('auth.login'))
    
    return decorated_function

def get_current_user_from_token():
    """
    Helper function to get current user from JWT token or session
    Returns User object or None
    """
    # Check for Bearer token
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            supabase = get_supabase_client()
            user_data = supabase.auth.get_user(token)
            
            if user_data.user:
                return User.find_by_supabase_id(user_data.user.id)
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
    
    # Fallback to session
    if current_user.is_authenticated:
        return current_user
    
    return None 
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User
from app.auth.forms import RegistrationForm, LoginForm
from app.supabase_client import get_supabase_client, get_supabase_anon_client
from app.auth.decorators import supabase_auth_required
import logging

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration with Supabase"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegistrationForm()
    
    # Debug logging
    logger.info(f"Register route accessed - Method: {request.method}")
    if request.method == 'POST':
        logger.info(f"Form data received: {request.form}")
        logger.info(f"Form validation result: {form.validate()}")
        if form.errors:
            logger.warning(f"Form validation errors: {form.errors}")
    
    if form.validate_on_submit():
        try:
            logger.info(f"Starting registration for email: {form.email.data}")
            
            # Create user in Supabase
            supabase = get_supabase_client()
            auth_response = supabase.auth.admin.create_user({
                "email": form.email.data.lower(),
                "password": form.password.data,
                "email_confirm": True,
                "user_metadata": {
                    "username": form.username.data.lower(),
                    "full_name": form.full_name.data,
                    "phone": f"{form.country_code.data}{form.phone.data}"
                }
            })
            
            logger.info(f"Supabase auth response: {auth_response}")
            
            if hasattr(auth_response, 'user') and auth_response.user:
                logger.info(f"User created in Supabase with ID: {auth_response.user.id}")
                
                # Combine country code with phone number
                full_phone = f"{form.country_code.data}{form.phone.data}"
                
                # Create local user profile
                user = User(
                    supabase_id=auth_response.user.id,
                    username=form.username.data.lower(),
                    full_name=form.full_name.data,
                    email=form.email.data.lower(),
                    phone=full_phone
                )
                
                db.session.add(user)
                db.session.commit()
                
                logger.info(f"User created in local database with ID: {user.id}")
                
                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                logger.error(f"Supabase user creation failed: {auth_response}")
                flash('Registration failed. Please try again.', 'error')
                
        except Exception as e:
            logger.error(f"Supabase registration failed: {e}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Exception args: {e.args}")
            flash(f'Registration failed: {str(e)}', 'error')
    else:
        # Log form validation errors
        if form.errors:
            logger.warning(f"Form validation errors: {form.errors}")
    
    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with Supabase only"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            # Authenticate with Supabase only
            supabase = get_supabase_client()
            auth_response = supabase.auth.sign_in_with_password({
                "email": form.email.data.lower(),
                "password": form.password.data
            })
            
            if auth_response.user:
                # Find or create local user
                local_user = User.find_by_supabase_id(auth_response.user.id)
                if not local_user:
                    # Create local user profile if doesn't exist
                    local_user = User(
                        supabase_id=auth_response.user.id,
                        email=auth_response.user.email,
                        full_name=auth_response.user.user_metadata.get('full_name', 'Unknown'),
                        phone=auth_response.user.user_metadata.get('phone', '')
                    )
                    db.session.add(local_user)
                    db.session.commit()
                
                # Log in user
                login_user(local_user, remember=form.remember.data)
                next_page = request.args.get('next')
                flash('Login successful!', 'success')
                return redirect(next_page or url_for('dashboard.index'))
            else:
                flash('Invalid email or password', 'error')
                
        except Exception as e:
            logger.error(f"Supabase login failed: {e}")
            flash('Login failed. Please check your credentials or create a new account.', 'error')
    
    return render_template('login.html', form=form)


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """Handle user logout"""
    try:
        # Sign out from Supabase if user has supabase_id
        if current_user.supabase_id:
            supabase = get_supabase_client()
            supabase.auth.admin.sign_out(current_user.supabase_id)
    except Exception as e:
        logger.error(f"Supabase logout failed: {e}")
    
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/google-login')
def google_login():
    """Redirect to Google OAuth with enhanced debugging"""
    try:
        supabase = get_supabase_anon_client()
        
        # Try different redirect URL formats
        redirect_url = request.host_url.rstrip('/') + "/auth/callback"
        
        logger.info(f"Generating OAuth URL with redirect_to: {redirect_url}")
        
        # Try with different OAuth options
        auth_url = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": redirect_url,
                "query_params": {
                    "access_type": "offline",
                    "prompt": "consent"
                }
            }
        })
        
        logger.info(f"Generated OAuth URL: {auth_url.url}")
        
        # Add a note about Chrome tracking issue
        flash('If you see "Authentication failed", try using Firefox or Edge instead of Chrome.', 'info')
        
        return redirect(auth_url.url)
    except Exception as e:
        logger.error(f"Google OAuth failed: {e}")
        flash('Google login is not available at the moment.', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/callback')
def auth_callback():
    """Handle OAuth callback"""
    try:
        # Enhanced Debug: Log everything
        logger.info("=" * 50)
        logger.info("OAUTH CALLBACK DEBUG")
        logger.info("=" * 50)
        logger.info(f"Request URL: {request.url}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request args: {dict(request.args)}")
        logger.info(f"Request form: {dict(request.form)}")
        logger.info(f"Request cookies: {dict(request.cookies)}")
        logger.info(f"Request referrer: {request.referrer}")
        logger.info(f"Request user_agent: {request.user_agent}")
        
        # Get parameters from the callback
        code = request.args.get('code')
        error = request.args.get('error')
        error_description = request.args.get('error_description')
        access_token = request.args.get('access_token')
        refresh_token = request.args.get('refresh_token')
        
        # Log what we received
        logger.info(f"Code received: {code}")
        logger.info(f"Error received: {error}")
        logger.info(f"Error description: {error_description}")
        logger.info(f"Access token received: {access_token}")
        logger.info(f"Refresh token received: {refresh_token}")
        
        # Check if we have any parameters at all
        all_args = dict(request.args)
        if not all_args:
            logger.error("❌ NO PARAMETERS RECEIVED - This means Supabase is not redirecting properly")
            logger.error("❌ Check Supabase Dashboard > Authentication > URL Configuration")
            logger.error("❌ Site URL should be: http://localhost:5000")
            logger.error("❌ Redirect URLs should include: http://localhost:5000/auth/callback")
        
        if error:
            flash(f'OAuth error: {error} - {error_description}', 'error')
            return redirect(url_for('auth.login'))
        
        # Try different approaches to get user data
        supabase = get_supabase_anon_client()
        
        # Method 1: Try to exchange code for session
        if code:
            try:
                logger.info("Attempting to exchange code for session...")
                session_response = supabase.auth.exchange_code_for_session(code)
                logger.info(f"Session response: {session_response}")
                
                if session_response.session and session_response.user:
                    user_data = session_response.user
                    logger.info(f"User data from session: {user_data}")
                else:
                    raise Exception("No user data in session response")
                    
            except Exception as e:
                logger.error(f"Code exchange failed: {e}")
                # Fall back to other methods
                user_data = None
        
        # Method 2: Try to get user from access token
        elif access_token:
            try:
                logger.info("Attempting to get user from access token...")
                user_response = supabase.auth.get_user(access_token)
                logger.info(f"User response: {user_response}")
                
                if user_response.user:
                    user_data = user_response.user
                    logger.info(f"User data from token: {user_data}")
                else:
                    raise Exception("No user data in token response")
                    
            except Exception as e:
                logger.error(f"Token validation failed: {e}")
                user_data = None
        
        # Method 3: Try to get current session
        else:
            try:
                logger.info("Attempting to get current session...")
                session_response = supabase.auth.get_session()
                logger.info(f"Current session: {session_response}")
                
                if session_response.user:
                    user_data = session_response.user
                    logger.info(f"User data from current session: {user_data}")
                else:
                    raise Exception("No user data in current session")
                    
            except Exception as e:
                logger.error(f"Current session failed: {e}")
                user_data = None
        
        # Process user data if we got it
        if user_data:
            # Find or create local user
            local_user = User.find_by_supabase_id(user_data.id)
            if not local_user:
                # Generate a unique username from email if not provided
                email_username = user_data.email.split('@')[0]
                base_username = email_username
                counter = 1
                username = base_username
                
                # Ensure username is unique
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                local_user = User(
                    supabase_id=user_data.id,
                    username=username,
                    email=user_data.email,
                    full_name=user_data.user_metadata.get('full_name', 'Unknown'),
                    phone=user_data.user_metadata.get('phone', '')
                )
                db.session.add(local_user)
                db.session.commit()
                logger.info(f"Created new local user: {local_user.id}")
            
            # Log in user
            login_user(local_user)
            flash('Login successful!', 'success')
            logger.info(f"User logged in successfully: {local_user.email}")
            return redirect(url_for('dashboard.index'))
        else:
            # Fallback: Check if user exists in Supabase by email
            logger.warning("No user data received from OAuth callback, trying fallback...")
            
            # Get the email from the request (if available)
            email = request.args.get('email') or request.form.get('email')
            
            if email:
                logger.info(f"Trying to find user by email: {email}")
                try:
                    # Find user in Supabase
                    supabase = get_supabase_client()
                    supabase_users_response = supabase.auth.admin.list_users()
                    
                    if hasattr(supabase_users_response, 'users') and supabase_users_response.users:
                        supabase_users = supabase_users_response.users
                    elif isinstance(supabase_users_response, list):
                        supabase_users = supabase_users_response
                    else:
                        supabase_users = []
                    
                    # Find user by email
                    supabase_user = next((u for u in supabase_users if u.email == email), None)
                    
                    if supabase_user:
                        logger.info(f"Found user in Supabase: {supabase_user.id}")
                        
                        # Find or create local user
                        local_user = User.find_by_supabase_id(supabase_user.id)
                        if not local_user:
                            # Generate a unique username from email if not provided
                            email_username = supabase_user.email.split('@')[0]
                            base_username = email_username
                            counter = 1
                            username = base_username
                            
                            # Ensure username is unique
                            while User.query.filter_by(username=username).first():
                                username = f"{base_username}{counter}"
                                counter += 1
                            
                            local_user = User(
                                supabase_id=supabase_user.id,
                                username=username,
                                email=supabase_user.email,
                                full_name=supabase_user.user_metadata.get('full_name', 'Unknown'),
                                phone=supabase_user.user_metadata.get('phone', '')
                            )
                            db.session.add(local_user)
                            db.session.commit()
                            logger.info(f"Created local user profile: {local_user.id}")
                        
                        # Log in user
                        login_user(local_user)
                        flash('Login successful! (fallback method)', 'success')
                        logger.info(f"User logged in via fallback: {local_user.email}")
                        return redirect(url_for('dashboard.index'))
                
                except Exception as e:
                    logger.error(f"Fallback method failed: {e}")
            
            flash('Authentication failed - no user data received', 'error')
            logger.error("No user data received from any OAuth method")
            return redirect(url_for('auth.login'))
            
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    """API endpoint for Supabase signup"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    try:
        # Create user in Supabase
        supabase = get_supabase_client()
        auth_response = supabase.auth.admin.create_user({
            "email": data['email'].lower(),
            "password": data['password'],
            "email_confirm": True,
            "user_metadata": {
                "full_name": data.get('full_name', 'Unknown'),
                "phone": data.get('phone', '')
            }
        })
        
        if auth_response.user:
            # Create local user profile
            user = User(
                supabase_id=auth_response.user.id,
                full_name=data.get('full_name', 'Unknown'),
                email=data['email'].lower(),
                phone=data.get('phone', '')
            )
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'message': 'User created successfully',
                'user_id': user.id,
                'supabase_id': user.supabase_id
            }), 201
        else:
            return jsonify({'error': 'Failed to create user'}), 400
            
    except Exception as e:
        logger.error(f"API signup failed: {e}")
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for Supabase login"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    try:
        # Authenticate with Supabase
        supabase = get_supabase_client()
        auth_response = supabase.auth.sign_in_with_password({
            "email": data['email'].lower(),
            "password": data['password']
        })
        
        if auth_response.user:
            # Find or create local user
            local_user = User.find_by_supabase_id(auth_response.user.id)
            if not local_user:
                local_user = User(
                    supabase_id=auth_response.user.id,
                    email=auth_response.user.email,
                    full_name=auth_response.user.user_metadata.get('full_name', 'Unknown'),
                    phone=auth_response.user.user_metadata.get('phone', '')
                )
                db.session.add(local_user)
                db.session.commit()
            
            # Log in user
            login_user(local_user)
            
            return jsonify({
                'message': 'Login successful',
                'user_id': local_user.id,
                'access_token': auth_response.session.access_token if auth_response.session else None
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        logger.error(f"API login failed: {e}")
        return jsonify({'error': 'Login failed'}), 500


@auth_bp.route('/api/verify-token', methods=['POST'])
def verify_token():
    """API endpoint to verify Supabase JWT token"""
    data = request.get_json()
    token = data.get('token') if data else None
    
    if not token:
        return jsonify({'error': 'Token is required'}), 400
    
    try:
        supabase = get_supabase_client()
        user_data = supabase.auth.get_user(token)
        
        if user_data.user:
            # Find local user
            local_user = User.find_by_supabase_id(user_data.user.id)
            if local_user:
                return jsonify({
                    'valid': True,
                    'user_id': local_user.id,
                    'email': local_user.email
                }), 200
            else:
                return jsonify({'error': 'Local user not found'}), 404
        else:
            return jsonify({'error': 'Invalid token'}), 401
            
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return jsonify({'error': 'Token verification failed'}), 500


# ==================================================
# DIRECT GOOGLE OAUTH ROUTES
# ==================================================

@auth_bp.route('/google-login-direct')
def google_login_direct():
    """Direct Google OAuth login (not using Supabase OAuth)"""
    try:
        from app.google_oauth import get_google_oauth_service
        google_oauth = get_google_oauth_service()
        auth_url = google_oauth.get_authorization_url()
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"Google OAuth failed: {e}")
        flash('Google login is not available at the moment.', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        code = request.args.get('code')
        error = request.args.get('error')
        
        logger.info(f"Google OAuth callback - Code: {code}, Error: {error}")
        
        if error:
            flash(f'Google OAuth error: {error}', 'error')
            return redirect(url_for('auth.login'))
        
        if not code:
            flash('No authorization code received', 'error')
            return redirect(url_for('auth.login'))
        
        # Get user info from Google
        from app.google_oauth import get_google_oauth_service
        google_oauth = get_google_oauth_service()
        user_info = google_oauth.get_user_info(code)
        
        if not user_info:
            flash('Failed to get user information from Google', 'error')
            return redirect(url_for('auth.login'))
        
        logger.info(f"Retrieved user info from Google: {user_info}")
        
        # Check if user exists in local database
        user = User.find_by_email(user_info['email'])
        
        if not user:
            # Create user in Supabase first
            supabase = get_supabase_client()
            
            # Generate a random password for Supabase
            import secrets
            import string
            random_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
            
            auth_response = supabase.auth.admin.create_user({
                "email": user_info['email'],
                "password": random_password,
                "email_confirm": True,
                "user_metadata": {
                    "full_name": user_info.get('name', 'Unknown'),
                    "phone": user_info.get('phone', ''),
                    "google_id": user_info.get('id'),
                    "auth_provider": "google"
                }
            })
            
            if hasattr(auth_response, 'user') and auth_response.user:
                # Generate a unique username from email
                email_username = user_info['email'].split('@')[0]
                base_username = email_username
                counter = 1
                username = base_username
                
                # Ensure username is unique
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                # Create user in local database
                user = User(
                    supabase_id=auth_response.user.id,
                    username=username,
                    full_name=user_info.get('name', 'Unknown'),
                    email=user_info['email'],
                    phone=user_info.get('phone', '') or '0000000000'  # Default phone
                )
                
                db.session.add(user)
                db.session.commit()
                
                logger.info(f"Created new user via Google OAuth: {user.email}")
            else:
                flash('Failed to create user account', 'error')
                return redirect(url_for('auth.login'))
        else:
            logger.info(f"Existing user logged in via Google OAuth: {user.email}")
        
        # Log in the user
        login_user(user, remember=True)
        flash('Successfully logged in with Google!', 'success')
        return redirect(url_for('dashboard.index'))
        
    except Exception as e:
        logger.error(f"Google OAuth callback failed: {e}")
        flash('Google login failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))
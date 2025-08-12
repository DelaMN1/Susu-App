"""
Google OAuth Service for Flask App
Handles Google OAuth authentication directly while syncing with Supabase
"""

import os
import requests
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from flask import current_app, url_for, request, session
import logging

logger = logging.getLogger(__name__)

class GoogleOAuthService:
    """Google OAuth service for direct authentication"""
    
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/google/callback')
        
        # Google OAuth endpoints
        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        # Scopes we need
        self.scopes = [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]
    
    def get_authorization_url(self):
        """Generate Google OAuth authorization URL"""
        try:
            # Create OAuth flow
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": self.auth_url,
                        "token_uri": self.token_url,
                        "redirect_uris": [self.redirect_uri],
                        "scopes": self.scopes
                    }
                },
                scopes=self.scopes
            )
            
            flow.redirect_uri = self.redirect_uri
            
            # Generate authorization URL
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            # Store state in session for security
            session['oauth_state'] = state
            
            logger.info(f"Generated Google OAuth URL: {authorization_url}")
            return authorization_url
            
        except Exception as e:
            logger.error(f"Failed to generate Google OAuth URL: {e}")
            raise
    
    def get_user_info(self, authorization_code):
        """Exchange authorization code for user info"""
        try:
            # Create OAuth flow
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": self.auth_url,
                        "token_uri": self.token_url,
                        "redirect_uris": [self.redirect_uri],
                        "scopes": self.scopes
                    }
                },
                scopes=self.scopes
            )
            
            flow.redirect_uri = self.redirect_uri
            
            # Exchange code for tokens
            flow.fetch_token(code=authorization_code)
            
            # Get user info from Google
            user_info_response = requests.get(
                self.userinfo_url,
                headers={'Authorization': f'Bearer {flow.credentials.token}'}
            )
            
            if user_info_response.status_code == 200:
                user_info = user_info_response.json()
                logger.info(f"Retrieved user info from Google: {user_info.get('email')}")
                return user_info
            else:
                logger.error(f"Failed to get user info: {user_info_response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None
    
    def verify_id_token(self, id_token_string):
        """Verify Google ID token"""
        try:
            idinfo = id_token.verify_oauth2_token(
                id_token_string, 
                google_requests.Request(), 
                self.client_id
            )
            
            # ID token is valid
            logger.info(f"Verified ID token for user: {idinfo.get('email')}")
            return idinfo
            
        except Exception as e:
            logger.error(f"Failed to verify ID token: {e}")
            return None

def get_google_oauth_service():
    """Get Google OAuth service instance"""
    return GoogleOAuthService() 
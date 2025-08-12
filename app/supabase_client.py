import os
from supabase import create_client, Client
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    """
    Get or create a Supabase client instance.
    Uses service role key for server-side operations.
    """
    try:
        url = current_app.config.get('SUPABASE_URL')
        service_role_key = current_app.config.get('SUPABASE_SERVICE_ROLE_KEY')
        
        if not url or not service_role_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        
        return create_client(url, service_role_key)
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        raise

def get_supabase_anon_client() -> Client:
    """
    Get or create a Supabase client instance using anonymous key.
    Use this for client-side operations or when service role is not needed.
    """
    try:
        url = current_app.config.get('SUPABASE_URL')
        anon_key = current_app.config.get('SUPABASE_ANON_KEY')
        
        if not url or not anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        
        return create_client(url, anon_key)
    except Exception as e:
        logger.error(f"Failed to create Supabase anon client: {e}")
        raise 
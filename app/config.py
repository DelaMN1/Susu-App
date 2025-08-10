import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Base configuration class with common settings
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-development-only'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Mail configuration (for future use)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')


class DevelopmentConfig(Config):
    """
    Development environment configuration
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///susu_dev.db'


class TestingConfig(Config):
    """
    Testing environment configuration
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///susu_test.db'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """
    Production environment configuration
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Ensure production has a valid secret key
    @classmethod
    def init_app(cls, app):
        # Production-specific configuration
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-key-for-development-only':
            app.logger.error('Production environment requires a secure SECRET_KEY to be set')


# Configuration dictionary to map environment names to config classes
config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
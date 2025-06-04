"""
Configuration settings for the edu-app application.
"""
import os

# PostgreSQL Database Configuration
POSTGRES_CONFIG = {
    'dbname': os.environ.get('POSTGRES_DB', 'edu_app'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'port': os.environ.get('POSTGRES_PORT', '5432')
}

# Flask Configuration
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.environ.get('FLASK_PORT', '5000'))

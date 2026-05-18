import os

class Config:
    """Application configuration"""

    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'workverse_secret_key_2026'

    # Railway MySQL Database configuration
    DB_HOST = os.environ.get('DB_HOST') or 'mainline.proxy.rlwy.net'
    DB_PORT = int(os.environ.get('DB_PORT') or 43679)
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'lYsTdHBWArwwUmxMBqdNWNXQfRDqNrAT'
    DB_NAME = os.environ.get('DB_NAME') or 'railway'

    # File upload configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'ppt', 'pptx'}

    # Application settings
    QUIZ_PASS_PERCENTAGE = 60

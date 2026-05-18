import os

class Config:
    """Application configuration"""

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'

    # Railway MySQL Configuration
    DB_HOST = os.environ.get('DB_HOST') or 'mainline.proxy.rlwy.net'
    DB_PORT = os.environ.get('DB_PORT') or '43679'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'lYsTdHBWArwwUmxMBqdNWNXQfRDqNrAT'
    DB_NAME = os.environ.get('DB_NAME') or 'railway'

    # File upload configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'ppt', 'pptx'}

    # Application settings
    QUIZ_PASS_PERCENTAGE = 60

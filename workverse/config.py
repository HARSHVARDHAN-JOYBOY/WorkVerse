import os

class Config:
    """Application configuration"""

    # Secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-super-secret-key'

    # Railway MySQL configuration
    DB_HOST = os.environ.get('DB_HOST') or 'mainline.proxy.rlwy.net'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'lYsTdHBWArwwUmxMBqdNWNXQfRDqNrAT'
    DB_NAME = os.environ.get('DB_NAME') or 'railway'
    DB_PORT = int(os.environ.get('DB_PORT') or 43679)

    # File upload configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'ppt', 'pptx'}

    # Application settings
    QUIZ_PASS_PERCENTAGE = 60

import os
import logging

logger = logging.getLogger(__name__)

class Config:
    """Application configuration for WorkVerse"""
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        # Development fallback with warning; in production, SECRET_KEY should be set
        SECRET_KEY = 'dev-secret-key-change-in-production'
        logger.warning("SECRET_KEY environment variable is not set! Using development default.")
    
    # MySQL Database configuration
    # Supports both custom DB_* variables (Render standard) and MYSQL* variables (Railway standard)
    DB_HOST = os.environ.get('DB_HOST') or os.environ.get('MYSQLHOST')
    DB_PORT = int(os.environ.get('DB_PORT') or os.environ.get('MYSQLPORT') or 3306)
    DB_USER = os.environ.get('DB_USER') or os.environ.get('MYSQLUSER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or os.environ.get('MYSQLPASSWORD')
    DB_NAME = os.environ.get('DB_NAME') or os.environ.get('MYSQLDATABASE')
    
    # SSL/TLS configuration: 'auto', 'true', 'false'
    DB_SSL = os.environ.get('DB_SSL', 'auto').strip().lower()
    
    # Timeouts and retries for Railway Serverless cold-start resilience
    DB_CONNECT_TIMEOUT = int(os.environ.get('DB_CONNECT_TIMEOUT', 15))
    DB_READ_TIMEOUT = int(os.environ.get('DB_READ_TIMEOUT', 15))
    DB_WRITE_TIMEOUT = int(os.environ.get('DB_WRITE_TIMEOUT', 15))
    DB_MAX_RETRIES = int(os.environ.get('DB_MAX_RETRIES', 5))
    DB_RETRY_BACKOFF = float(os.environ.get('DB_RETRY_BACKOFF', 2.0))
    
    # File upload configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'ppt', 'pptx'}
    
    # Application settings
    QUIZ_PASS_PERCENTAGE = 60  # Minimum percentage to pass quiz

    @classmethod
    def validate_db_config(cls, config_source=None):
        """
        Validate that required database parameters are present.
        Accepts an optional dict/mapping (like app.config) or defaults to cls attributes.
        Returns (is_valid: bool, missing_keys: list, message: str).
        Does NOT expose passwords or sensitive values.
        """
        cfg = config_source if config_source is not None else cls
        
        def get_val(key, fallback_key=None):
            if isinstance(cfg, dict) or hasattr(cfg, '__getitem__'):
                val = cfg.get(key)
                if val is None and fallback_key:
                    val = cfg.get(fallback_key)
                return val
            val = getattr(cfg, key, None)
            if val is None and fallback_key:
                val = getattr(cfg, fallback_key, None)
            return val

        host = get_val('DB_HOST', 'MYSQLHOST')
        user = get_val('DB_USER', 'MYSQLUSER')
        password = get_val('DB_PASSWORD', 'MYSQLPASSWORD')
        database = get_val('DB_NAME', 'MYSQLDATABASE')

        missing = []
        if not host:
            missing.append('DB_HOST (or MYSQLHOST)')
        if not user:
            missing.append('DB_USER (or MYSQLUSER)')
        if password is None:
            missing.append('DB_PASSWORD (or MYSQLPASSWORD)')
        if not database:
            missing.append('DB_NAME (or MYSQLDATABASE)')
            
        if missing:
            msg = f"Database configuration incomplete. Missing required environment variables: {', '.join(missing)}"
            return False, missing, msg
        return True, [], "Database configuration complete."

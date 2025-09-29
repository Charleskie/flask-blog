import os
from datetime import timedelta

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///personal_website.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 邮件配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_FROM = os.environ.get('MAIL_FROM')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    
    # 分页配置
    POSTS_PER_PAGE = 5
    
    # 安全配置
    SESSION_COOKIE_SECURE = False  # 生产环境设为True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # HTTPS 配置
    PREFERRED_URL_SCHEME = 'https'  # 生产环境使用 HTTPS
    SERVER_NAME = os.environ.get('SERVER_NAME')  # 如：www.shiheng.info
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_RETENTION_DAYS = int(os.environ.get('LOG_RETENTION_DAYS') or 7)
    
    # 根据环境设置日志路径
    @staticmethod
    def get_log_dir():
        """根据环境获取日志目录"""
        env = os.environ.get('FLASK_ENV', 'development')
        if env == 'production':
            return os.environ.get('LOG_DIR') or '/root/kim/temp/blog/logs'
        else:
            return os.environ.get('LOG_DIR') or 'logs'
    
    @staticmethod
    def get_log_file():
        """根据环境获取日志文件名"""
        env = os.environ.get('FLASK_ENV', 'development')
        if env == 'production':
            return os.environ.get('LOG_FILE') or 'app.log'
        else:
            return os.environ.get('LOG_FILE') or 'app.log'

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = True
    
    # 生产环境安全设置
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # HTTPS 强制配置
    PREFERRED_URL_SCHEME = 'https'
    FORCE_HTTPS = True

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 
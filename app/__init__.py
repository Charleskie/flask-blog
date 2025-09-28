from flask import Flask
from flask_login import LoginManager
from app.models.user import db
from app.utils.filters import nl2br_filter, markdown_filter, html_filter
from app.utils.logger import setup_app_logging, log_manager
import os

def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///personal_website.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化扩展
    db.init_app(app)
    
    # 初始化登录管理器
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # 注册自定义过滤器
    app.template_filter('nl2br')(nl2br_filter)
    app.template_filter('markdown')(markdown_filter)
    app.template_filter('html')(html_filter)
    
    # 注册蓝图
    from app.routes import main_bp, admin_bp, auth_bp
    from app.routes.settings import settings_bp
    from app.routes.interaction import interaction_bp
    from app.routes.version import version_bp
    from app.routes.notifications import notification_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(interaction_bp, url_prefix='/api')
    app.register_blueprint(version_bp)
    app.register_blueprint(notification_bp)
    
    # 设置日志
    setup_app_logging(app)
    app.logger.info("应用初始化完成")
    
    # 初始化 HTTPS 重定向（生产环境）
    if app.config.get('FORCE_HTTPS', False):
        from ssl_redirect import init_ssl_redirect
        init_ssl_redirect(app)
    
    # 错误处理
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        app.logger.warning(f"404错误: {error}")
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        app.logger.warning(f"403错误: {error}")
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        app.logger.error(f"500内部服务器错误: {error}", exc_info=True)
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app 
"""
HTTPS 重定向中间件
用于在生产环境中强制使用 HTTPS
"""
from flask import request, redirect, url_for
import os

def init_ssl_redirect(app):
    """初始化 SSL 重定向"""
    
    @app.before_request
    def force_https():
        """强制 HTTPS 重定向"""
        # 只在生产环境且配置了 FORCE_HTTPS 时启用
        if (app.config.get('FORCE_HTTPS', False) and 
            not request.is_secure and 
            request.headers.get('X-Forwarded-Proto') != 'https'):
            
            # 构建 HTTPS URL
            https_url = request.url.replace('http://', 'https://', 1)
            return redirect(https_url, code=301)
    
    @app.before_request
    def force_www():
        """强制使用 www 子域名"""
        if (app.config.get('FORCE_WWW', False) and 
            request.host and 
            not request.host.startswith('www.')):
            
            # 构建带 www 的 URL
            www_url = request.url.replace(
                f'://{request.host}', 
                f'://www.{request.host}', 
                1
            )
            return redirect(www_url, code=301)

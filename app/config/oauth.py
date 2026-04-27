"""
OAuth 配置文件
用于配置 Google 和 GitHub 的社交登录
使用 Authlib 库
"""

import os
from authlib.integrations.flask_client import OAuth

def init_oauth(app):
    """初始化 OAuth 配置"""
    oauth = OAuth(app)
    
    # Google OAuth 配置
    google = oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        access_token_url='https://oauth2.googleapis.com/token',
        authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    
    # GitHub OAuth 配置
    github = oauth.register(
        name='github',
        client_id=os.getenv('GITHUB_CLIENT_ID'),
        client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        client_kwargs={
            'scope': 'user:email'
        }
    )
    
    # 微信 OAuth 配置
    wechat = oauth.register(
        name='wechat',
        client_id=os.getenv('WECHAT_APP_ID'),
        client_secret=os.getenv('WECHAT_APP_SECRET'),
        access_token_url='https://api.weixin.qq.com/sns/oauth2/access_token',
        authorize_url='https://open.weixin.qq.com/connect/qrconnect',
        api_base_url='https://api.weixin.qq.com/',
        client_kwargs={
            'scope': 'snsapi_login'
        }
    )
    
    return oauth, google, github, wechat

#!/usr/bin/env python3
"""
WSGI入口文件
用于生产环境部署
"""

import os
from app import app

if __name__ == "__main__":
    # 获取环境变量
    env = os.environ.get('FLASK_ENV', 'development')
    
    if env == 'production':
        # 生产环境配置
        app.config.from_object('config.ProductionConfig')
    else:
        # 开发环境配置
        app.config.from_object('config.DevelopmentConfig')
    
    # 运行应用
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=(env == 'development')
    ) 
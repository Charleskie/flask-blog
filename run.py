#!/usr/bin/env python3
"""
简单的启动脚本
用于快速启动开发服务器
"""

from app import app

if __name__ == '__main__':
    print("🚀 启动个人网站...")
    print("📱 访问地址: http://localhost:5000")
    print("🔧 开发模式已启用")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    ) 
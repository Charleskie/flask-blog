#!/usr/bin/env python3
"""
智能端口选择启动脚本
自动选择可用端口启动服务器
"""

import socket
import sys
from app import app

def find_free_port(start_port=5000, max_attempts=10):
    """查找可用端口"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def main():
    """主函数"""
    print("🚀 启动个人网站...")
    print("🔍 正在查找可用端口...")
    
    # 查找可用端口
    port = find_free_port(5000, 10)
    
    if port is None:
        print("❌ 无法找到可用端口 (5000-5009)")
        print("💡 请手动指定端口或关闭占用端口的程序")
        sys.exit(1)
    
    print(f"✅ 找到可用端口: {port}")
    print(f"📱 访问地址: http://localhost:{port}")
    print("🔧 开发模式已启用")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == '__main__':
    main() 
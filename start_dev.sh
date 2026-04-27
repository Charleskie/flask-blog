#!/bin/bash

# 开发环境启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 启动个人网站服务器 (开发环境)..."
echo "📁 工作目录: $SCRIPT_DIR"

# 设置开发环境变量
export FLASK_ENV=development
export FLASK_DEBUG=True
export LOG_LEVEL=DEBUG
export LOG_DIR=logs
export LOG_FILE=app.log
export MAIL_SERVER=smtp.gmail.com
export MAIL_PORT=587
export MAIL_USE_TLS=True
export MAIL_USERNAME=wdws851421092@gmail.com
export MAIL_PASSWORD=zzgozjfssthlsrpb
export MAIL_FROM=wdws851421092@gmail.com
export MAIL_DEFAULT_SENDER=wdws851421092@gmail.com

# 检查Python是否可用
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请确保已安装Python3"
    exit 1
fi

# 检查依赖是否安装
echo "📦 检查依赖..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "⚠️  检测到缺少依赖，正在安装..."
    pip3 install -r requirements.txt
fi

# 检查日志目录
if [ ! -d "logs" ]; then
    mkdir -p logs
    echo "📝 创建日志目录: logs/"
fi

# 启动服务器
echo "🌐 启动开发服务器..."
echo "📱 访问地址: http://localhost:8000"
echo "🔧 管理后台: http://localhost:8000/admin"
echo "📝 日志目录: logs/"
echo "⏹️  按 Ctrl+C 停止服务器"
echo ""

# 启动应用
python3 run.py

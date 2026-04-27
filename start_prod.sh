#!/bin/bash

# 生产环境启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 启动个人网站服务器 (生产环境)..."
echo "📁 工作目录: $SCRIPT_DIR"

# 设置生产环境变量
export FLASK_ENV=production
export FLASK_DEBUG=False
export LOG_LEVEL=INFO
export LOG_DIR=/root/kim/temp/blog/logs
export LOG_FILE=app.log
export PYTHONUNBUFFERED=1

APP_HOST="${APP_HOST:-127.0.0.1}"
APP_PORT="${APP_PORT:-8000}"
GUNICORN_WORKERS="${GUNICORN_WORKERS:-2}"
GUNICORN_THREADS="${GUNICORN_THREADS:-4}"
GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-120}"

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
if [ ! -d "/root/kim/temp/blog/logs" ]; then
    mkdir -p /root/kim/temp/blog/logs
    echo "📝 创建日志目录: /root/kim/temp/blog/logs/"
fi

# 初始化数据库
echo "🗄️ 初始化数据库..."
python3 - <<'PY'
from app import create_app
from app.models.user import db

app = create_app()
with app.app_context():
    db.create_all()
print("✅ 数据库初始化完成")
PY

if ! python3 -c "import gunicorn" &> /dev/null; then
    echo "❌ 未找到 gunicorn，请先安装 requirements.txt 中的依赖"
    exit 1
fi

echo "🌐 启动生产服务器 (Gunicorn)..."
echo "📱 访问地址: http://${APP_HOST}:${APP_PORT}"
echo "🔧 管理后台: http://${APP_HOST}:${APP_PORT}/admin"
echo "📝 日志目录: /root/kim/temp/blog/logs/"
echo "⏹️  按 Ctrl+C 停止服务器"
echo ""

# 启动应用
exec python3 -m gunicorn \
    --bind "${APP_HOST}:${APP_PORT}" \
    --workers "${GUNICORN_WORKERS}" \
    --threads "${GUNICORN_THREADS}" \
    --timeout "${GUNICORN_TIMEOUT}" \
    --access-logfile - \
    --error-logfile - \
    'app:create_app()'

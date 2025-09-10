#!/bin/bash

# 最简单的部署脚本（使用Flask开发服务器）
# 使用方法: ./deploy_simple.sh [服务器IP] [用户名]

set -e

SERVER_IP=${1:-"47.112.96.87"}
SERVER_USER=${2:-"root"}

echo "🚀 开始简单部署个人网站到 $SERVER_USER@$SERVER_IP"

# 步骤1: 打包项目
echo "📦 步骤1: 打包项目..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="website_simple_${TIMESTAMP}.tar.gz"

# 创建临时目录
TEMP_DIR=$(mktemp -d)
echo "📋 复制项目文件到临时目录..."
cp -r app $TEMP_DIR/
cp run.py $TEMP_DIR/
cp requirements.txt $TEMP_DIR/
cp requirements_compatible.txt $TEMP_DIR/
cp requirements_python36.txt $TEMP_DIR/
cp README.md $TEMP_DIR/
cp db_manager.py $TEMP_DIR/
cp db_tools.py $TEMP_DIR/
cp check_status.sh $TEMP_DIR/
cp check_website.sh $TEMP_DIR/
cp restart_website.sh $TEMP_DIR/



# 创建压缩包
cd $TEMP_DIR
tar -czf ../$PACKAGE_NAME .
cd - > /dev/null
mv $TEMP_DIR/../$PACKAGE_NAME .
rm -rf $TEMP_DIR

echo "✅ 项目打包完成: $PACKAGE_NAME"

# 步骤2: 上传到服务器
echo "📤 步骤2: 上传到服务器..."
scp $PACKAGE_NAME $SERVER_USER@$SERVER_IP:/tmp/

# 步骤3: 在服务器上部署
echo "🔧 步骤3: 在服务器上部署..."
ssh $SERVER_USER@$SERVER_IP << EOF
set -e

echo "📁 创建项目目录..."
mkdir -p /home/website
cd /home/website

echo "📦 解压项目文件..."
tar -xzf /tmp/$PACKAGE_NAME
rm /tmp/$PACKAGE_NAME

echo "🔧 设置端口管理脚本权限..."
chmod +x quick_port_fix.sh 2>/dev/null || true
chmod +x port_manager.py 2>/dev/null || true

echo "🐍 检查Python版本..."
python3 --version || echo "Python3 未安装，尝试安装..."
if ! command -v python3 &> /dev/null; then
    echo "📦 安装Python3..."
    sudo yum install -y python3 python3-pip
fi

echo "🌐 安装Nginx..."
sudo yum install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx

echo "🔧 创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

echo "📦 检测Python版本并选择依赖..."
PYTHON_VERSION=\$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python版本: \$PYTHON_VERSION"

if [[ "\$PYTHON_VERSION" == "3.12" ]] || [[ "\$PYTHON_VERSION" == "3.11" ]]; then
    echo "✅ 使用最新版本依赖..."
    pip install --upgrade pip
    pip install -r requirements.txt
elif [[ "\$PYTHON_VERSION" == "3.8" ]] || [[ "\$PYTHON_VERSION" == "3.9" ]] || [[ "\$PYTHON_VERSION" == "3.10" ]]; then
    echo "⚠️ 使用兼容版本依赖..."
    pip install --upgrade pip
    pip install -r requirements_compatible.txt
elif [[ "\$PYTHON_VERSION" == "3.6" ]] || [[ "\$PYTHON_VERSION" == "3.7" ]]; then
    echo "⚠️ 使用Python 3.6兼容版本依赖..."
    pip install --upgrade pip
    pip install -r requirements_python36.txt
else
    echo "❌ Python版本太旧，不支持。建议升级到Python 3.6+"
    exit 1
fi

echo "🧪 测试应用导入..."
python -c "from app import create_app; print('✅ 应用导入成功')"

echo "🔧 端口管理..."
echo "🔍 检查端口8000占用情况..."

# 检查端口占用并关闭进程
echo "🔍 检查lsof命令是否可用..."
if command -v lsof &> /dev/null; then
    echo "✅ lsof命令可用，检查端口占用..."
    pids=\$(lsof -ti :8000 2>/dev/null || echo "")
    if [ -n "\$pids" ]; then
        echo "❌ 端口8000被占用，正在关闭占用进程..."
        for pid in \$pids; do
            echo "关闭进程 \$pid..."
            # 尝试优雅关闭
            kill -TERM \$pid 2>/dev/null || true
            sleep 1
            # 检查进程是否还存在
            if kill -0 \$pid 2>/dev/null; then
                echo "强制关闭进程 \$pid..."
                kill -KILL \$pid 2>/dev/null || true
                sleep 1
            fi
        done
        echo "✅ 端口8000已释放"
    else
        echo "✅ 端口8000未被占用"
    fi
else
    echo "⚠️  lsof不可用，使用pkill关闭Python进程..."
    pkill -f "python.*run.py" 2>/dev/null || true
    pkill -f "python3.*run.py" 2>/dev/null || true
    pkill -f "python.*8000" 2>/dev/null || true
    pkill -f "python3.*8000" 2>/dev/null || true
    sleep 2
fi

# 验证端口是否已释放
echo "🔍 验证端口释放..."
sleep 2
if command -v lsof &> /dev/null; then
    echo "🔍 使用lsof验证端口状态..."
    if lsof -i :8000 >/dev/null 2>&1; then
        echo "⚠️  端口8000仍被占用，强制关闭所有相关进程..."
        pkill -f "python.*run.py" 2>/dev/null || true
        pkill -f "python3.*run.py" 2>/dev/null || true
        pkill -f "flask" 2>/dev/null || true
        pkill -f "gunicorn" 2>/dev/null || true
        sleep 3
        echo "✅ 强制清理完成"
    else
        echo "✅ 端口8000已成功释放"
    fi
else
    echo "⚠️  lsof不可用，使用netstat验证..."
    if command -v netstat &> /dev/null; then
        if netstat -tlnp | grep :8000 >/dev/null 2>&1; then
            echo "⚠️  端口8000仍被占用，强制关闭所有相关进程..."
            pkill -f "python.*run.py" 2>/dev/null || true
            pkill -f "python3.*run.py" 2>/dev/null || true
            pkill -f "flask" 2>/dev/null || true
            pkill -f "gunicorn" 2>/dev/null || true
            sleep 3
        else
            echo "✅ 端口8000已成功释放"
        fi
    else
        echo "✅ 端口管理完成（无法验证）"
    fi
fi

echo "🗄️ 初始化数据库..."
python run.py &
sleep 5
pkill -f run.py || true

echo "🌐 创建Nginx配置..."
sudo tee /etc/nginx/conf.d/website.conf << 'NGINX_EOF'
server {
    listen 80;
    server_name shiheng.info www.shiheng.info;
    
    # 静态文件配置 - 使用root而不是alias
    location /static/ {
        root /home/website/app;
        expires 1h;
        add_header Cache-Control "public, no-transform";
        add_header X-Content-Type-Options nosniff;
        
        # 确保文件存在时才提供
        try_files $uri =404;
    }
    
    # 主应用代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX_EOF

echo "🔄 重启Nginx..."
sudo systemctl restart nginx

echo "🔍 测试Nginx配置:"
sudo nginx -t

echo "🔧 设置静态文件权限..."
# 设置目录权限，确保nginx用户可以访问
sudo chown -R root:root /home/website/
sudo chmod -R 755 /home/website/
sudo chmod -R 644 /home/website/app/static/css/*.css
sudo chmod -R 644 /home/website/app/static/js/*.js
sudo chmod -R 644 /home/website/app/static/images/*
sudo chmod -R 644 /home/website/app/static/avatar/*

echo "🔍 验证静态文件权限:"
ls -la /home/website/app/static/css/main.css
ls -la /home/website/app/static/js/main.js

echo "🧹 清理Nginx缓存..."
sudo rm -rf /var/cache/nginx/* 2>/dev/null || true

echo "⚙️ 创建systemd服务..."
sudo tee /etc/systemd/system/website.service << 'SERVICE_EOF'
[Unit]
Description=Personal Website
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/home/website
Environment=PATH=/home/website/venv/bin
ExecStart=/home/website/venv/bin/python run.py
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

echo "🚀 启动服务..."
echo "🔧 确保端口8000可用..."

# 停止可能存在的website服务
echo "停止website服务..."
sudo systemctl stop website 2>/dev/null || true
sleep 2

# 再次检查端口占用
echo "🔍 再次检查端口占用..."
if command -v lsof &> /dev/null; then
    echo "🔍 使用lsof检查端口..."
    pids=\$(lsof -ti :8000 2>/dev/null || echo "")
    if [ -n "\$pids" ]; then
        echo "❌ 端口8000仍被占用，强制关闭..."
        for pid in \$pids; do
            echo "强制关闭进程 \$pid..."
            kill -KILL \$pid 2>/dev/null || true
        done
        sleep 2
        echo "✅ 强制清理完成"
    else
        echo "✅ 端口8000可用"
    fi
else
    echo "⚠️  lsof不可用，使用pkill清理..."
    pkill -f "python.*run.py" 2>/dev/null || true
    pkill -f "python3.*run.py" 2>/dev/null || true
    pkill -f "flask" 2>/dev/null || true
    pkill -f "gunicorn" 2>/dev/null || true
    sleep 2
    echo "✅ 清理完成"
fi

sudo systemctl daemon-reload
sudo systemctl start website
sudo systemctl enable website

echo "✅ 部署完成！"

echo "🔍 验证部署结果..."
echo "📋 检查服务状态:"
sudo systemctl status website --no-pager -l

echo "🔍 检查端口占用:"
if command -v lsof &> /dev/null; then
    lsof -i :8000 || echo "✅ 端口8000未被占用"
else
    netstat -tlnp | grep :8000 || echo "✅ 端口8000未被占用"
fi

echo "🔍 验证静态文件部署:"
echo "📁 检查CSS文件:"
ls -la /home/website/app/static/css/ || echo "❌ CSS目录不存在"
echo "📁 检查JS文件:"
ls -la /home/website/app/static/js/ || echo "❌ JS目录不存在"
echo "📁 检查主CSS文件:"
ls -la /home/website/app/static/css/main.css || echo "❌ main.css不存在"

echo "🔍 测试静态文件访问:"
curl -I http://localhost/static/css/main.css || echo "❌ 静态文件无法访问"

echo "🌐 网站地址: http://$SERVER_IP"
echo "🔧 管理后台: http://$SERVER_IP/admin"
echo "📋 默认管理员: admin / admin123"
echo "💡 如果样式有问题，请清除浏览器缓存或使用Ctrl+F5强制刷新"
EOF

echo "🎉 部署完成！"
echo "🌐 网站地址: http://$SERVER_IP"
echo "🔧 管理后台: http://$SERVER_IP/admin"
echo "📋 默认管理员: admin / admin123"

# 清理本地文件
rm $PACKAGE_NAME 
#!/bin/bash

# 部署脚本（支持HTTP和HTTPS）
# 使用方法: ./deploy_sample.sh [服务器IP] [用户名] [是否启用HTTPS] [SSH密钥路径] [SSH端口]
# 示例: ./deploy_sample.sh YOUR_SERVER_IP root true ~/.ssh/id_rsa 22

set -e

SERVER_IP=${1:-"YOUR_SERVER_IP"}
SERVER_USER=${2:-"root"}
ENABLE_HTTPS=${3:-"false"}
SSH_KEY_PATH=${4:-${SSH_KEY_PATH:-""}}
SSH_PORT=${5:-${SSH_PORT:-"22"}}
DOMAIN="www.example.com"

# 设置生产环境变量
export FLASK_ENV=production
export FLASK_DEBUG=False
export LOG_LEVEL=INFO
export LOG_DIR=/var/log/your-site
export LOG_FILE=app.log
export SERVER_NAME=$DOMAIN
export FORCE_HTTPS=$ENABLE_HTTPS
export FORCE_WWW=true

echo "🚀 开始部署个人网站到 $SERVER_USER@$SERVER_IP"
echo "🌐 域名: $DOMAIN"
echo "🔐 HTTPS: $ENABLE_HTTPS"
echo "🔌 SSH端口: $SSH_PORT"
echo ""
echo "📋 使用说明:"
echo "  HTTP部署:  ./deploy_simple.sh [IP] [用户] false [密钥路径] [端口]"
echo "  HTTPS部署: ./deploy_simple.sh [IP] [用户] true [密钥路径] [端口]"
echo "  示例:      ./deploy_simple.sh YOUR_SERVER_IP root true ~/.ssh/id_rsa 22"
echo ""

SSH_OPTS=(-o ConnectTimeout=10 -o StrictHostKeyChecking=no -p "$SSH_PORT")
SCP_OPTS=(-o ConnectTimeout=10 -o StrictHostKeyChecking=no -P "$SSH_PORT")

if [ -n "$SSH_KEY_PATH" ]; then
    if [ ! -f "$SSH_KEY_PATH" ]; then
        echo "❌ 指定的SSH密钥不存在: $SSH_KEY_PATH"
        exit 1
    fi
    SSH_OPTS+=(-i "$SSH_KEY_PATH")
    SCP_OPTS+=(-i "$SSH_KEY_PATH")
    echo "🔑 使用SSH密钥: $SSH_KEY_PATH"
else
    echo "🔑 使用系统默认SSH身份（ssh-agent 或 ~/.ssh/id_*）"
fi

echo "🔍 步骤0: 测试SSH连接..."
if ssh "${SSH_OPTS[@]}" "$SERVER_USER@$SERVER_IP" "echo 'SSH连接成功'" 2>/dev/null; then
    echo "✅ SSH连接成功"
else
    echo "❌ SSH连接失败"
    echo ""
    echo "如果报错是 Permission denied (publickey)，真正的问题不是上面的 post-quantum 警告，而是服务器没有接受你的SSH身份。"
    echo "请检查："
    echo "1. 用户名是否正确：当前是 $SERVER_USER"
    echo "2. 如果服务器禁用 root 直登，请改用有 sudo 权限的用户"
    echo "3. 私钥是否与服务器 ~/.ssh/authorized_keys 中的公钥匹配"
    echo "4. 如果不是默认密钥，请显式传入第4个参数"
    echo "5. 如果SSH不是22端口，请显式传入第5个参数"
    echo ""
    echo "示例："
    echo "  ./deploy_simple.sh $SERVER_IP $SERVER_USER $ENABLE_HTTPS ~/.ssh/id_rsa $SSH_PORT"
    exit 1
fi

# 步骤1: 打包项目
echo "📦 步骤1: 打包项目..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="website_simple_${TIMESTAMP}.tar.gz"

# 创建临时目录
TEMP_DIR=$(mktemp -d)
echo "📋 复制项目文件到临时目录..."
cp -r app $TEMP_DIR/
cp -r static $TEMP_DIR/ 2>/dev/null || echo "⚠️ static目录不存在，跳过"
cp app.py $TEMP_DIR/
cp run.py $TEMP_DIR/
cp config.py $TEMP_DIR/
cp .env $TEMP_DIR/ 2>/dev/null || echo "⚠️ .env不存在，跳过"
cp requirements.txt $TEMP_DIR/
cp requirements_compatible.txt $TEMP_DIR/
cp requirements_python36.txt $TEMP_DIR/
cp README.md $TEMP_DIR/
cp db_manager.py $TEMP_DIR/
cp db_tools.py $TEMP_DIR/
cp cleanup_logs.py $TEMP_DIR/
cp setup_log_cleanup.sh $TEMP_DIR/
cp start_prod.sh $TEMP_DIR/
cp ssl_redirect.py $TEMP_DIR/



# 创建压缩包
cd $TEMP_DIR
tar -czf ../$PACKAGE_NAME .
cd - > /dev/null
mv $TEMP_DIR/../$PACKAGE_NAME .
rm -rf $TEMP_DIR

echo "✅ 项目打包完成: $PACKAGE_NAME"

# 步骤2: 上传到服务器
echo "📤 步骤2: 上传到服务器..."
scp "${SCP_OPTS[@]}" $PACKAGE_NAME $SERVER_USER@$SERVER_IP:/tmp/

# 步骤3: 在服务器上部署
echo "🔧 步骤3: 在服务器上部署..."
ssh "${SSH_OPTS[@]}" $SERVER_USER@$SERVER_IP << EOF
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

# 如果启用HTTPS，安装Certbot
if [ "$ENABLE_HTTPS" = "true" ]; then
    echo "🔐 安装Certbot for HTTPS..."
    
    # 检查是否已有EPEL源
    if rpm -qa | grep -q epel; then
        echo "✅ EPEL源已存在，跳过安装"
    else
        echo "📦 安装EPEL源..."
        sudo yum install -y epel-release
    fi
    
    # 尝试安装Certbot
    echo "📦 安装Certbot..."
    if sudo yum install -y certbot python3-certbot-nginx; then
        echo "✅ Certbot 安装完成"
    else
        echo "⚠️ 标准安装失败，尝试替代方案..."
        
        # 尝试使用snap安装
        if command -v snap &> /dev/null; then
            echo "📦 使用snap安装Certbot..."
            sudo snap install --classic certbot
            sudo ln -sf /snap/bin/certbot /usr/bin/certbot
        else
            echo "📦 安装snapd..."
            sudo yum install -y snapd
            sudo systemctl enable --now snapd.socket
            sudo ln -sf /var/lib/snapd/snap /snap
            sudo snap install --classic certbot
            sudo ln -sf /snap/bin/certbot /usr/bin/certbot
        fi
        
        # 验证安装
        if certbot --version &> /dev/null; then
            echo "✅ Certbot 安装成功"
        else
            echo "❌ Certbot 安装失败，将跳过HTTPS配置"
            echo "💡 您可以稍后手动安装Certbot"
        fi
    fi
fi

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
python - <<'PY'
from app import create_app
from app.models.user import db

app = create_app()
with app.app_context():
    db.create_all()

print("✅ 数据库初始化完成")
PY

echo "🌐 创建Nginx配置..."

write_http_nginx_config() {
    sudo tee /etc/nginx/conf.d/website.conf > /dev/null << 'NGINX_HTTP_EOF'
server {
    listen 80;
    server_name example.com www.example.com;

    location ~ ^/(favicon\.(ico|png|svg)|robots\.txt|sitemap\.xml)$ {
        root /home/website/app/static/images;
        expires 1d;
        add_header Cache-Control "public, no-transform";
        add_header X-Content-Type-Options nosniff;
        try_files \$uri =404;
    }

    location /static/ {
        root /home/website/app;
        expires 1h;
        add_header Cache-Control "public, no-transform";
        add_header X-Content-Type-Options nosniff;
        try_files \$uri =404;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
NGINX_HTTP_EOF
}

write_https_nginx_config() {
    sudo tee /etc/nginx/conf.d/website.conf > /dev/null << 'NGINX_HTTPS_EOF'
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com www.example.com;

    ssl_certificate /etc/letsencrypt/live/www.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.example.com/privkey.pem;

    location ~ ^/(favicon\.(ico|png|svg)|robots\.txt|sitemap\.xml)$ {
        root /home/website/app/static/images;
        expires 1d;
        add_header Cache-Control "public, no-transform";
        add_header X-Content-Type-Options nosniff;
        try_files \$uri =404;
    }

    location /static/ {
        root /home/website/app;
        expires 1h;
        add_header Cache-Control "public, no-transform";
        add_header X-Content-Type-Options nosniff;
        try_files \$uri =404;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
NGINX_HTTPS_EOF
}

validate_and_reload_nginx() {
    echo "🔍 测试Nginx配置语法..."
    if ! sudo nginx -t; then
        echo "❌ Nginx配置语法错误"
        echo "📋 当前配置："
        sudo cat /etc/nginx/conf.d/website.conf || true
        exit 1
    fi

    echo "🔄 重载Nginx..."
    if sudo systemctl reload nginx; then
        echo "✅ Nginx重载成功"
        return 0
    fi

    echo "⚠️ 重载失败，尝试重启Nginx..."
    if sudo systemctl restart nginx; then
        echo "✅ Nginx重启成功"
        return 0
    fi

    echo "❌ Nginx启动失败"
    sudo systemctl status nginx --no-pager -l || true
    sudo journalctl -u nginx --no-pager -n 20 || true
    exit 1
}

echo "🌐 先写入HTTP配置，确保Nginx可以稳定启动..."
write_http_nginx_config
validate_and_reload_nginx

# 如果启用HTTPS，获取SSL证书
if [ "$ENABLE_HTTPS" = "true" ]; then
    echo "🔐 获取SSL证书..."
    echo "⚠️  请确保域名 $DOMAIN 已正确解析到服务器IP: $SERVER_IP"
    echo "⚠️  如果域名解析不正确，SSL证书获取将失败"

    if ! command -v certbot &> /dev/null; then
        echo "❌ Certbot未安装，保持HTTP配置不变"
    elif sudo certbot --nginx -d $DOMAIN -d example.com --non-interactive --agree-tos --email admin@example.com; then
        echo "✅ SSL证书获取成功"
        echo "🔐 写入HTTPS配置..."
        write_https_nginx_config
        validate_and_reload_nginx

        echo "⏰ 设置证书自动续期..."
        (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
        echo "✅ 自动续期设置完成"
    else
        echo "❌ SSL证书获取失败"
        echo "请检查："
        echo "1. 域名解析是否正确"
        echo "2. 80端口是否可访问"
        echo "3. 防火墙设置"
        echo "4. 安全组是否放行80/443端口"
        echo "继续保持HTTP配置。"
    fi
fi

echo "🔧 设置静态文件权限..."
# 设置目录权限，确保nginx用户可以访问
sudo chown -R root:root /home/website/
sudo chmod -R 755 /home/website/

# 安全地设置静态文件权限（只对存在的文件）
echo "📁 设置CSS文件权限..."
find /home/website/app/static/css -name "*.css" -type f -exec chmod 644 {} \; 2>/dev/null || true

echo "📁 设置JS文件权限..."
find /home/website/app/static/js -name "*.js" -type f -exec chmod 644 {} \; 2>/dev/null || true

echo "📁 设置图片文件权限..."
find /home/website/app/static/images -type f -exec chmod 644 {} \; 2>/dev/null || true

echo "📁 设置头像文件权限..."
find /home/website/app/static/avatar -type f -exec chmod 644 {} \; 2>/dev/null || true

echo "📁 设置其他静态文件权限..."
find /home/website/app/static -type f -exec chmod 644 {} \; 2>/dev/null || true

echo "🔍 验证静态文件权限:"
echo "📁 检查CSS文件:"
ls -la /home/website/app/static/css/main.css 2>/dev/null || echo "⚠️ main.css不存在"
echo "📁 检查JS文件:"
ls -la /home/website/app/static/js/main.js 2>/dev/null || echo "⚠️ main.js不存在"
echo "📁 检查静态文件目录结构:"
find /home/website/app/static -type f | head -10 || echo "⚠️ 静态文件目录为空"

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
Environment=PATH=/home/website/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
Environment=FLASK_ENV=production
Environment=FLASK_DEBUG=False
Environment=PYTHONUNBUFFERED=1
ExecStartPre=/home/website/venv/bin/python -c "from app import create_app; from app.models.user import db; app=create_app(); ctx=app.app_context(); ctx.push(); db.create_all(); ctx.pop()"
ExecStart=/home/website/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 2 --threads 4 --timeout 120 --access-logfile - --error-logfile - 'app:create_app()'
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

# 根据HTTPS配置显示不同的访问地址
if [ "$ENABLE_HTTPS" = "true" ]; then
    echo "🌐 网站地址: https://$DOMAIN"
    echo "🔧 管理后台: https://$DOMAIN/admin"
    echo "🔗 HTTP访问: http://$DOMAIN (自动重定向到HTTPS)"
else
    echo "🌐 网站地址: http://$SERVER_IP"
    echo "🔧 管理后台: http://$SERVER_IP/admin"
    echo "🌐 域名访问: http://$DOMAIN"
fi
echo "💡 如果样式有问题，请清除浏览器缓存或使用Ctrl+F5强制刷新"
EOF

echo "🎉 部署完成！"

# 根据HTTPS配置显示不同的访问地址
if [ "$ENABLE_HTTPS" = "true" ]; then
    echo "🌐 网站地址: https://$DOMAIN"
    echo "🔧 管理后台: https://$DOMAIN/admin"
    echo "🔗 HTTP访问: http://$DOMAIN (自动重定向到HTTPS)"
    echo "✅ HTTPS 配置完成，SSL证书已安装"
else
    echo "🌐 网站地址: http://$SERVER_IP"
    echo "🔧 管理后台: http://$SERVER_IP/admin"
    echo "🌐 域名访问: http://$DOMAIN"
    echo "💡 如需启用HTTPS，请运行: ./deploy_simple.sh $SERVER_IP $SERVER_USER true"
fi

# 清理本地文件
rm $PACKAGE_NAME 

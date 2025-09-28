#!/bin/bash

# 一键部署脚本（支持HTTP和HTTPS，自动处理各种问题）
# 使用方法: ./deploy.sh [服务器IP] [用户名] [是否启用HTTPS] [SSH密码]
# 示例: ./deploy.sh 47.112.96.87 root true your_password

set -e

SERVER_IP=${1:-"47.112.96.87"}
SERVER_USER=${2:-"root"}
ENABLE_HTTPS=${3:-"false"}
SSH_PASSWORD=${4:-""}
DOMAIN="www.shiheng.info"

# 设置生产环境变量
export FLASK_ENV=production
export FLASK_DEBUG=False
export LOG_LEVEL=INFO
export LOG_DIR=/root/kim/temp/blog/logs
export LOG_FILE=app.log
export SERVER_NAME=$DOMAIN
export FORCE_HTTPS=$ENABLE_HTTPS
export FORCE_WWW=true

echo "🚀 开始部署个人网站到阿里云服务器 $SERVER_USER@$SERVER_IP"
echo "🌐 域名: $DOMAIN"
echo "🔐 HTTPS: $ENABLE_HTTPS"
echo ""
echo "📋 使用说明:"
echo "  HTTP部署:  ./deploy.sh [IP] [用户] false [密码]"
echo "  HTTPS部署: ./deploy.sh [IP] [用户] true [密码]"
echo "  示例:      ./deploy.sh 47.112.96.87 root true your_password"
echo ""

# 检查SSH密码是否提供
if [ -z "$SSH_PASSWORD" ]; then
    echo "❌ 错误：请提供SSH密码"
    echo "使用方法: ./deploy.sh $SERVER_IP $SERVER_USER $ENABLE_HTTPS your_password"
    exit 1
fi

# 安装sshpass（如果不存在）
if ! command -v sshpass &> /dev/null; then
    echo "📦 安装sshpass..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install hudochenkov/sshpass/sshpass
        else
            echo "❌ 请先安装Homebrew: https://brew.sh/"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update && sudo apt-get install -y sshpass
    else
        echo "❌ 不支持的操作系统，请手动安装sshpass"
        exit 1
    fi
fi

# 测试SSH连接
echo "🔍 测试SSH连接..."
if sshpass -p "$SSH_PASSWORD" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "echo 'SSH连接成功'" 2>/dev/null; then
    echo "✅ SSH连接成功"
else
    echo "❌ SSH连接失败"
    echo "请检查："
    echo "1. 服务器IP地址是否正确: $SERVER_IP"
    echo "2. 用户名是否正确: $SERVER_USER"
    echo "3. 密码是否正确"
    echo "4. 服务器SSH服务是否运行"
    echo "5. 防火墙是否允许SSH连接（端口22）"
    exit 1
fi

# 步骤1: 打包项目
echo "📦 步骤1: 打包项目..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="website_aliyun_${TIMESTAMP}.tar.gz"

# 创建临时目录
TEMP_DIR=$(mktemp -d)
echo "📋 复制项目文件到临时目录..."
cp -r app $TEMP_DIR/
cp -r static $TEMP_DIR/ 2>/dev/null || echo "⚠️ static目录不存在，跳过"
cp run.py $TEMP_DIR/
cp config.py $TEMP_DIR/
cp requirements.txt $TEMP_DIR/
cp requirements_compatible.txt $TEMP_DIR/
cp requirements_python36.txt $TEMP_DIR/
cp README.md $TEMP_DIR/
cp db_manager.py $TEMP_DIR/
cp db_tools.py $TEMP_DIR/
cp cleanup_logs.py $TEMP_DIR/
cp setup_log_cleanup.sh $TEMP_DIR/
cp ssl_redirect.py $TEMP_DIR/
# cp HTTPS_SETUP.md $TEMP_DIR/  # 文件已删除

# 创建压缩包
cd $TEMP_DIR
tar -czf ../$PACKAGE_NAME .
cd - > /dev/null
mv $TEMP_DIR/../$PACKAGE_NAME .
rm -rf $TEMP_DIR

echo "✅ 项目打包完成: $PACKAGE_NAME"

# 步骤2: 上传到服务器
echo "📤 步骤2: 上传到服务器..."
if sshpass -p "$SSH_PASSWORD" scp -o StrictHostKeyChecking=no $PACKAGE_NAME $SERVER_USER@$SERVER_IP:/tmp/; then
    echo "✅ 文件上传成功"
else
    echo "❌ 文件上传失败"
    exit 1
fi

# 步骤3: 在服务器上部署
echo "🔧 步骤3: 在服务器上部署..."
sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << EOF
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

# 阿里云服务器HTTPS配置
if [ "$ENABLE_HTTPS" = "true" ]; then
    echo "🔐 配置阿里云服务器HTTPS..."
    
    # 检查EPEL源冲突
    echo "🔍 检查EPEL源状态..."
    if rpm -qa | grep -q "epel-aliyuncs"; then
        echo "⚠️ 检测到阿里云EPEL源，处理冲突..."
        
        # 尝试移除冲突的包
        sudo yum remove -y epel-aliyuncs-release 2>/dev/null || true
        
        # 清理yum缓存
        sudo yum clean all
        sudo yum makecache
    fi
    
    # 安装EPEL源
    echo "📦 安装EPEL源..."
    if ! rpm -qa | grep -q epel-release; then
        sudo yum install -y epel-release
    else
        echo "✅ EPEL源已存在"
    fi
    
    # 尝试安装Certbot
    echo "📦 安装Certbot..."
    if sudo yum install -y certbot python3-certbot-nginx; then
        echo "✅ Certbot 安装完成"
    else
        echo "⚠️ 标准安装失败，尝试替代方案..."
        
        # 方案1：使用pip安装
        echo "📦 尝试使用pip安装Certbot..."
        sudo pip3 install certbot certbot-nginx
        
        # 方案2：手动下载安装
        if ! command -v certbot &> /dev/null; then
            echo "📦 手动下载Certbot..."
            cd /tmp
            wget https://dl.eff.org/certbot-auto
            chmod a+x certbot-auto
            sudo mv certbot-auto /usr/local/bin/certbot
        fi
        
        # 验证安装
        if certbot --version &> /dev/null; then
            echo "✅ Certbot 安装成功"
        else
            echo "❌ Certbot 安装失败，将跳过HTTPS配置"
            echo "💡 您可以稍后手动安装Certbot或使用阿里云SSL证书"
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
python run.py &
sleep 5
pkill -f run.py || true

echo "🌐 创建Nginx配置..."

# 根据是否启用HTTPS创建不同的配置
if [ "$ENABLE_HTTPS" = "true" ]; then
    echo "🔐 创建HTTPS Nginx配置..."
    sudo tee /etc/nginx/conf.d/website.conf << 'NGINX_HTTPS_EOF'
# HTTP 服务器配置 - 重定向到 HTTPS
server {
    listen 80;
    server_name shiheng.info www.shiheng.info;
    
    # 重定向所有 HTTP 请求到 HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS 服务器配置
server {
    listen 443 ssl http2;
    server_name shiheng.info www.shiheng.info;
    
    # SSL 配置将由 Certbot 自动添加
    # 临时SSL配置（Certbot会自动替换）
    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;
    
    # 根目录静态文件配置（favicon等）
    location ~ ^/(favicon\.(ico|png|svg)|robots\.txt|sitemap\.xml)$ {
        root /home/website/static/images;
        expires 1d;
        add_header Cache-Control "public, no-transform";
        add_header X-Content-Type-Options nosniff;
        
        # 确保文件存在时才提供
        try_files \$uri =404;
    }
    
    # 应用静态文件配置
    location /static/ {
        root /home/website/app;
        expires 1h;
        add_header Cache-Control "public, no-transform";
        add_header X-Content-Type-Options nosniff;
        
        # 确保文件存在时才提供
        try_files \$uri =404;
    }
    
    # 主应用代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
NGINX_HTTPS_EOF
else
    echo "🌐 创建HTTP Nginx配置..."
    sudo tee /etc/nginx/conf.d/website.conf << 'NGINX_HTTP_EOF'
server {
    listen 80;
    server_name shiheng.info www.shiheng.info;
    
    # 根目录静态文件配置（favicon等）
    location ~ ^/(favicon\.(ico|png|svg)|robots\.txt|sitemap\.xml)$ {
        root /home/website/static/images;
        expires 1d;
        add_header Cache-Control "public, no-transform";
        add_header X-Content-Type-Options nosniff;
        
        # 确保文件存在时才提供
        try_files \$uri =404;
    }
    
    # 应用静态文件配置
    location /static/ {
        root /home/website/app;
        expires 1h;
        add_header Cache-Control "public, no-transform";
        add_header X-Content-Type-Options nosniff;
        
        # 确保文件存在时才提供
        try_files \$uri =404;
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
NGINX_HTTP_EOF
fi

echo "🔄 重启Nginx..."

# 检查Nginx配置语法
echo "🔍 测试Nginx配置语法..."
if sudo nginx -t; then
    echo "✅ Nginx配置语法正确"
    
    # 尝试重启Nginx
    if sudo systemctl restart nginx; then
        echo "✅ Nginx重启成功"
    else
        echo "❌ Nginx重启失败，开始故障排除..."
        
        # 检查错误日志
        echo "📋 检查Nginx错误日志..."
        if [ -f /var/log/nginx/error.log ]; then
            echo "最近的错误日志："
            sudo tail -10 /var/log/nginx/error.log
        fi
        
        # 检查端口占用
        echo "📋 检查端口占用..."
        if lsof -i :80 >/dev/null 2>&1; then
            echo "⚠️ 80端口被占用："
            lsof -i :80
            echo "尝试停止占用进程..."
            sudo pkill -f "nginx" || true
            sleep 2
        fi
        
        # 检查配置文件
        echo "📋 检查配置文件..."
        if [ -f /etc/nginx/conf.d/website.conf ]; then
            echo "当前配置文件："
            sudo cat /etc/nginx/conf.d/website.conf
        fi
        
        # 创建简化的测试配置
        echo "🔧 创建简化的测试配置..."
        sudo tee /etc/nginx/conf.d/website.conf << 'NGINX_SIMPLE_EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
NGINX_SIMPLE_EOF
        
        # 再次测试配置
        echo "🔍 再次测试配置..."
        if sudo nginx -t; then
            echo "✅ 简化配置语法正确"
            
            # 尝试启动
            if sudo systemctl start nginx; then
                echo "✅ Nginx启动成功"
            else
                echo "❌ Nginx仍然启动失败"
                echo "📋 系统日志："
                sudo journalctl -u nginx --no-pager -l -n 10
                echo "⚠️ 请检查防火墙和SELinux设置"
            fi
        else
            echo "❌ 简化配置仍有语法错误"
            sudo nginx -t
        fi
    fi
else
    echo "❌ Nginx配置语法错误"
    sudo nginx -t
    echo "🔧 使用简化配置..."
    
    # 创建最基本的配置
    sudo tee /etc/nginx/conf.d/website.conf << 'NGINX_BASIC_EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
NGINX_BASIC_EOF
    
    # 测试并启动
    if sudo nginx -t && sudo systemctl start nginx; then
        echo "✅ 使用基本配置启动成功"
    else
        echo "❌ 基本配置也无法启动，请手动检查"
    fi
fi

# 如果启用HTTPS，获取SSL证书
if [ "$ENABLE_HTTPS" = "true" ]; then
    echo "🔐 获取SSL证书..."
    echo "⚠️  请确保域名 $DOMAIN 已正确解析到服务器IP: $SERVER_IP"
    echo "⚠️  如果域名解析不正确，SSL证书获取将失败"
    
    # 获取SSL证书
    if command -v certbot &> /dev/null; then
        sudo certbot --nginx -d $DOMAIN -d shiheng.info --non-interactive --agree-tos --email admin@$DOMAIN || {
            echo "❌ SSL证书获取失败"
            echo "请检查："
            echo "1. 域名解析是否正确"
            echo "2. 80端口是否可访问"
            echo "3. 防火墙设置"
            echo "4. 阿里云安全组设置"
            echo "继续使用HTTP配置..."
        }
        
        if [ $? -eq 0 ]; then
            echo "✅ SSL证书获取成功"
            
            # 设置自动续期
            echo "⏰ 设置证书自动续期..."
            (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
            echo "✅ 自动续期设置完成"
            
            # 重新加载Nginx配置
            sudo systemctl reload nginx
        fi
    else
        echo "❌ Certbot未安装，跳过SSL证书配置"
        echo "💡 建议："
        echo "1. 使用阿里云SSL证书服务"
        echo "2. 手动安装Certbot"
        echo "3. 使用其他SSL证书提供商"
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
    echo "💡 如需启用HTTPS，请运行: ./deploy.sh $SERVER_IP $SERVER_USER true $SSH_PASSWORD"
fi

# 清理本地文件
rm $PACKAGE_NAME

#!/bin/bash

# 网站重启脚本
# 使用方法: ./restart_website.sh

echo "🔄 === 个人网站重启脚本 ==="
echo "📅 重启时间: $(date)"
echo ""

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  建议使用sudo运行此脚本以获得最佳效果"
    echo "   运行命令: sudo ./restart_website.sh"
    echo ""
fi

# 1. 停止服务
echo "1️⃣ 停止服务..."
echo "----------------------------------------"
if systemctl stop website 2>/dev/null; then
    echo "✅ 网站服务已停止"
else
    echo "⚠️  网站服务停止失败或未运行"
fi

if systemctl stop nginx 2>/dev/null; then
    echo "✅ Nginx服务已停止"
else
    echo "⚠️  Nginx服务停止失败或未运行"
fi
echo ""

# 2. 等待服务完全停止
echo "2️⃣ 等待服务完全停止..."
echo "----------------------------------------"
sleep 3

# 检查进程是否还在运行
if pgrep -f "app.py" > /dev/null; then
    echo "⚠️  检测到Flask进程仍在运行，强制终止..."
    pkill -f "app.py"
    sleep 2
fi

if pgrep -f "nginx" > /dev/null; then
    echo "⚠️  检测到Nginx进程仍在运行，强制终止..."
    pkill -f "nginx"
    sleep 2
fi

echo "✅ 所有相关进程已停止"
echo ""

# 3. 清理端口
echo "3️⃣ 清理端口占用..."
echo "----------------------------------------"
# 检查端口8000是否被占用
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  端口8000仍被占用，尝试释放..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null
fi

# 检查端口80是否被占用
if lsof -i :80 > /dev/null 2>&1; then
    echo "⚠️  端口80仍被占用，尝试释放..."
    lsof -ti :80 | xargs kill -9 2>/dev/null
fi

echo "✅ 端口清理完成"
echo ""

# 4. 重新加载systemd配置
echo "4️⃣ 重新加载systemd配置..."
echo "----------------------------------------"
if systemctl daemon-reload; then
    echo "✅ systemd配置重新加载成功"
else
    echo "❌ systemd配置重新加载失败"
fi
echo ""

# 5. 启动服务
echo "5️⃣ 启动服务..."
echo "----------------------------------------"

# 启动网站服务
echo "🚀 启动网站服务..."
if systemctl start website; then
    echo "✅ 网站服务启动成功"
else
    echo "❌ 网站服务启动失败"
    echo "📄 查看错误日志:"
    journalctl -u website --no-pager -n 10
    echo ""
fi

# 等待网站服务启动
echo "⏳ 等待网站服务启动..."
sleep 5

# 启动Nginx服务
echo "🚀 启动Nginx服务..."
if systemctl start nginx; then
    echo "✅ Nginx服务启动成功"
else
    echo "❌ Nginx服务启动失败"
    echo "📄 查看错误日志:"
    journalctl -u nginx --no-pager -n 10
    echo ""
fi

echo ""

# 6. 验证服务状态
echo "6️⃣ 验证服务状态..."
echo "----------------------------------------"
sleep 3

# 检查服务状态
if systemctl is-active --quiet website; then
    echo "✅ 网站服务: 运行中"
else
    echo "❌ 网站服务: 未运行"
fi

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx服务: 运行中"
else
    echo "❌ Nginx服务: 未运行"
fi

# 检查端口监听
echo ""
echo "📡 端口监听状态:"
if netstat -tlnp | grep -q ":8000 "; then
    echo "✅ 端口8000: 已监听"
else
    echo "❌ 端口8000: 未监听"
fi

if netstat -tlnp | grep -q ":80 "; then
    echo "✅ 端口80: 已监听"
else
    echo "❌ 端口80: 未监听"
fi

echo ""

# 7. 测试访问
echo "7️⃣ 测试访问..."
echo "----------------------------------------"

# 等待服务完全启动
echo "⏳ 等待服务完全启动..."
sleep 5

# 测试本地访问
echo "🌐 测试本地访问:"
if curl -f -s http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ Flask应用: 本地访问正常 (端口8000)"
else
    echo "❌ Flask应用: 本地访问失败 (端口8000)"
fi

if curl -f -s http://localhost > /dev/null 2>&1; then
    echo "✅ Nginx代理: 本地访问正常 (端口80)"
else
    echo "❌ Nginx代理: 本地访问失败 (端口80)"
fi

# 测试外部访问
echo ""
echo "🌍 测试外部访问:"
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "未知")
echo "服务器公网IP: $SERVER_IP"

if curl -f -s http://$SERVER_IP > /dev/null 2>&1; then
    echo "✅ 外部HTTP访问: 正常"
else
    echo "❌ 外部HTTP访问: 失败"
fi

if curl -f -s http://$SERVER_IP/admin > /dev/null 2>&1; then
    echo "✅ 管理后台访问: 正常"
else
    echo "❌ 管理后台访问: 失败"
fi

echo ""

# 8. 显示服务信息
echo "8️⃣ 服务信息..."
echo "----------------------------------------"
echo "📋 网站服务状态:"
systemctl status website --no-pager -l

echo ""
echo "📋 Nginx服务状态:"
systemctl status nginx --no-pager -l

echo ""

# 9. 总结
echo "📊 === 重启总结 ==="
echo "----------------------------------------"

# 检查关键指标
SUCCESS=true

if ! systemctl is-active --quiet website; then
    SUCCESS=false
fi

if ! systemctl is-active --quiet nginx; then
    SUCCESS=false
fi

if ! netstat -tlnp | grep -q ":80 "; then
    SUCCESS=false
fi

if ! netstat -tlnp | grep -q ":8000 "; then
    SUCCESS=false
fi

if [ "$SUCCESS" = true ]; then
    echo "🎉 网站重启成功！"
    echo "✅ 所有服务都在正常运行"
    echo ""
    echo "🌐 网站地址: http://$SERVER_IP"
    echo "🔧 管理后台: http://$SERVER_IP/admin"
else
    echo "⚠️  网站重启过程中遇到问题"
    echo ""
    echo "🔧 建议的故障排查步骤:"
    echo "   1. 查看详细日志: sudo journalctl -u website -f"
    echo "   2. 检查配置文件: sudo nginx -t"
    echo "   3. 检查防火墙: sudo firewall-cmd --list-all"
    echo "   4. 手动启动测试: cd /home/website && source venv/bin/activate && python app.py"
fi

echo ""
echo "📝 重启完成时间: $(date)"
echo "🔍 监控日志: sudo journalctl -u website -f" 
#!/bin/bash

# 日志清理定时任务设置脚本
# 用于设置每天自动清理过期日志的cron任务

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLEANUP_SCRIPT="$SCRIPT_DIR/cleanup_logs.py"
PYTHON_PATH="$(which python3)"

echo "🔧 设置日志自动清理任务..."

# 检查Python脚本是否存在
if [ ! -f "$CLEANUP_SCRIPT" ]; then
    echo "❌ 清理脚本不存在: $CLEANUP_SCRIPT"
    exit 1
fi

# 检查Python是否可用
if [ -z "$PYTHON_PATH" ]; then
    echo "❌ 未找到Python3，请确保已安装Python3"
    exit 1
fi

echo "📝 Python路径: $PYTHON_PATH"
echo "📝 清理脚本路径: $CLEANUP_SCRIPT"

# 创建cron任务（每天凌晨2点执行）
CRON_JOB="0 2 * * * cd $SCRIPT_DIR && $PYTHON_PATH $CLEANUP_SCRIPT --days 7 >> $SCRIPT_DIR/logs/cleanup.log 2>&1"

echo "📅 将添加以下cron任务:"
echo "   $CRON_JOB"
echo ""

# 检查是否已存在相同的cron任务
if crontab -l 2>/dev/null | grep -q "cleanup_logs.py"; then
    echo "⚠️  检测到已存在日志清理任务，是否要替换？(y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        # 删除现有的清理任务
        crontab -l 2>/dev/null | grep -v "cleanup_logs.py" | crontab -
        echo "🗑️  已删除现有任务"
    else
        echo "❌ 取消设置"
        exit 0
    fi
fi

# 添加新的cron任务
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ 日志清理定时任务设置成功！"
    echo ""
    echo "📋 任务详情:"
    echo "   - 执行时间: 每天凌晨2点"
    echo "   - 保留天数: 7天"
    echo "   - 日志目录: $SCRIPT_DIR/logs"
    echo ""
    echo "🔍 查看当前cron任务:"
    echo "   crontab -l"
    echo ""
    echo "🗑️  删除定时任务:"
    echo "   crontab -e  # 然后删除相关行"
    echo ""
    echo "🧪 手动测试清理:"
    echo "   $PYTHON_PATH $CLEANUP_SCRIPT --dry-run"
else
    echo "❌ 设置定时任务失败"
    exit 1
fi

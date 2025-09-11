#!/usr/bin/env python3
"""
日志清理脚本
自动清理指定天数前的日志文件
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
import glob
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.logger import log_manager, cleanup_logs


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='清理过期日志文件')
    parser.add_argument(
        '--days', 
        type=int, 
        default=7, 
        help='保留日志的天数 (默认: 7天)'
    )
    parser.add_argument(
        '--log-dir', 
        type=str, 
        default='logs', 
        help='日志目录路径 (默认: logs)'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true', 
        help='预览模式，不实际删除文件'
    )
    
    args = parser.parse_args()
    
    print(f"🧹 开始清理 {args.log_dir} 目录中 {args.days} 天前的日志文件...")
    
    if args.dry_run:
        print("🔍 预览模式 - 不会实际删除文件")
    
    # 设置日志目录
    log_manager.log_dir = Path(args.log_dir)
    
    if not log_manager.log_dir.exists():
        print(f"❌ 日志目录不存在: {args.log_dir}")
        return 1
    
    # 计算截止日期
    cutoff_date = datetime.now() - timedelta(days=args.days)
    deleted_count = 0
    
    # 查找所有日志文件
    log_patterns = [
        str(log_manager.log_dir / "*.log.*"),  # 轮转的日志文件
        str(log_manager.log_dir / "*.log")     # 当前日志文件
    ]
    
    print(f"📅 将删除 {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')} 之前的日志文件")
    print("-" * 60)
    
    for pattern in log_patterns:
        for log_file in glob.glob(pattern):
            try:
                # 获取文件修改时间
                file_mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                file_size = os.path.getsize(log_file)
                
                # 如果文件超过指定天数，则删除
                if file_mtime < cutoff_date:
                    if args.dry_run:
                        print(f"🔍 [预览] 将删除: {log_file} (修改时间: {file_mtime.strftime('%Y-%m-%d %H:%M:%S')}, 大小: {file_size} bytes)")
                    else:
                        os.remove(log_file)
                        print(f"🗑️  已删除: {log_file} (修改时间: {file_mtime.strftime('%Y-%m-%d %H:%M:%S')}, 大小: {file_size} bytes)")
                        deleted_count += 1
                else:
                    print(f"✅ 保留: {log_file} (修改时间: {file_mtime.strftime('%Y-%m-%d %H:%M:%S')}, 大小: {file_size} bytes)")
                        
            except (OSError, ValueError) as e:
                print(f"❌ 处理日志文件失败 {log_file}: {e}")
    
    print("-" * 60)
    
    if args.dry_run:
        print(f"🔍 预览完成，将删除 {deleted_count} 个文件")
    else:
        print(f"✅ 清理完成，共删除 {deleted_count} 个过期日志文件")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

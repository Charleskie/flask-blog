#!/usr/bin/env python3
"""
日志管理模块
提供按日期分区的日志记录和自动清理功能
"""

import os
import logging
import logging.handlers
from datetime import datetime, timedelta
import glob
from pathlib import Path


class DailyRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """按日期轮转的文件处理器"""
    
    def __init__(self, filename, when='midnight', interval=1, backupCount=7, encoding='utf-8'):
        # 确保日志目录存在
        log_dir = os.path.dirname(filename)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        super().__init__(
            filename=filename,
            when=when,
            interval=interval,
            backupCount=backupCount,
            encoding=encoding,
            utc=False
        )
        
        # 设置文件名后缀格式
        self.suffix = "%Y-%m-%d"


class LogManager:
    """日志管理器"""
    
    def __init__(self, log_dir=None, app_name='personal_website'):
        # 如果没有指定日志目录，从配置中获取
        if log_dir is None:
            from config import Config
            log_dir = Config.get_log_dir()
        
        self.log_dir = Path(log_dir)
        self.app_name = app_name
        self.loggers = {}
        
        # 确保日志目录存在
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置日志格式
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def get_logger(self, name=None, level=logging.INFO):
        """获取日志记录器"""
        if name is None:
            name = self.app_name
        
        if name in self.loggers:
            return self.loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
        
        # 创建日志文件路径
        log_file = self.log_dir / f"{name}.log"
        
        # 添加文件处理器（按日期轮转）
        file_handler = DailyRotatingFileHandler(
            filename=str(log_file),
            when='midnight',
            interval=1,
            backupCount=7,  # 保留7天的日志
            encoding='utf-8'
        )
        file_handler.setFormatter(self.formatter)
        logger.addHandler(file_handler)
        
        # 添加控制台处理器（开发环境）
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        logger.addHandler(console_handler)
        
        # 防止日志向上传播
        logger.propagate = False
        
        self.loggers[name] = logger
        return logger
    
    def cleanup_old_logs(self, days=7):
        """清理指定天数前的日志文件"""
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        # 查找所有日志文件
        log_patterns = [
            str(self.log_dir / "*.log.*"),  # 轮转的日志文件
            str(self.log_dir / "*.log")     # 当前日志文件
        ]
        
        for pattern in log_patterns:
            for log_file in glob.glob(pattern):
                try:
                    # 获取文件修改时间
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                    
                    # 如果文件超过指定天数，则删除
                    if file_mtime < cutoff_date:
                        os.remove(log_file)
                        deleted_count += 1
                        print(f"🗑️  已删除过期日志文件: {log_file}")
                        
                except (OSError, ValueError) as e:
                    print(f"❌ 删除日志文件失败 {log_file}: {e}")
        
        return deleted_count
    
    def get_log_files(self):
        """获取所有日志文件信息"""
        log_files = []
        
        for log_file in self.log_dir.glob("*.log*"):
            try:
                stat = log_file.stat()
                log_files.append({
                    'name': log_file.name,
                    'path': str(log_file),
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'created': datetime.fromtimestamp(stat.st_ctime)
                })
            except OSError:
                continue
        
        return sorted(log_files, key=lambda x: x['modified'], reverse=True)
    
    def get_log_content(self, log_file, lines=100):
        """获取日志文件内容（最后N行）"""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        except (OSError, UnicodeDecodeError) as e:
            return f"读取日志文件失败: {e}"


# 全局日志管理器实例
log_manager = LogManager()


def setup_app_logging(app):
    """为Flask应用设置日志"""
    # 设置Flask应用日志
    app.logger.setLevel(logging.INFO)
    
    # 移除默认处理器
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)
    
    # 添加自定义处理器
    from config import Config
    log_file = Path(Config.get_log_dir()) / Config.get_log_file()
    file_handler = DailyRotatingFileHandler(
        filename=str(log_file),
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_manager.formatter)
    app.logger.addHandler(file_handler)
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_manager.formatter)
    app.logger.addHandler(console_handler)
    
    # 设置Werkzeug日志
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)  # 减少Werkzeug的日志输出
    
    return app.logger


def get_logger(name=None):
    """获取日志记录器的便捷函数"""
    return log_manager.get_logger(name)


def cleanup_logs(days=7):
    """清理过期日志的便捷函数"""
    return log_manager.cleanup_old_logs(days)

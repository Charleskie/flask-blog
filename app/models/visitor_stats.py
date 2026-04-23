from .user import db
from datetime import datetime, date

class VisitorStats(db.Model):
    """访问量统计模型"""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)  # 统计日期
    page_views = db.Column(db.Integer, default=0)  # 页面浏览量
    unique_visitors = db.Column(db.Integer, default=0)  # 独立访客数
    total_views = db.Column(db.Integer, default=0)  # 总浏览量
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<VisitorStats {self.date}>'
    
    @staticmethod
    def get_today_stats():
        """获取今日统计数据"""
        today = date.today()
        stats = VisitorStats.query.filter_by(date=today).first()
        if not stats:
            stats = VisitorStats(date=today)
            db.session.add(stats)
            db.session.commit()
        return stats
    
    @staticmethod
    def increment_page_view():
        """增加页面浏览量"""
        stats = VisitorStats.get_today_stats()
        stats.page_views += 1
        stats.total_views += 1
        stats.updated_at = datetime.utcnow()
        db.session.commit()
        return stats
    
    @staticmethod
    def increment_unique_visitor():
        """增加独立访客数"""
        stats = VisitorStats.get_today_stats()
        stats.unique_visitors += 1
        stats.updated_at = datetime.utcnow()
        db.session.commit()
        return stats
    
    @staticmethod
    def get_total_stats():
        """获取总统计数据"""
        total_views = db.session.query(db.func.sum(VisitorStats.total_views)).scalar() or 0
        total_visitors = db.session.query(db.func.sum(VisitorStats.unique_visitors)).scalar() or 0
        return {
            'total_views': total_views,
            'total_visitors': total_visitors
        }
    
    @staticmethod
    def get_recent_stats(days=7):
        """获取最近几天的统计数据"""
        end_date = date.today()
        start_date = date.fromordinal(end_date.toordinal() - days + 1)
        
        stats = VisitorStats.query.filter(
            VisitorStats.date >= start_date,
            VisitorStats.date <= end_date
        ).order_by(VisitorStats.date.desc()).all()
        
        return stats

from datetime import datetime
from zoneinfo import ZoneInfo

import markdown
from markdown.extensions import codehilite, fenced_code, tables, toc


LOCAL_TZ = ZoneInfo('Asia/Shanghai')

def nl2br_filter(text):
    """将换行符转换为HTML的<br>标签"""
    if text is None:
        return ''
    # 处理Windows风格的换行符 \r\n 和 Unix风格的换行符 \n
    text = text.replace('\r\n', '<br>')
    text = text.replace('\n', '<br>')
    return text

def markdown_filter(text):
    """将Markdown文本转换为HTML（保留用于向后兼容）"""
    if text is None:
        return ''
    
    # 配置Markdown扩展
    extensions = [
        'codehilite',  # 代码高亮
        'fenced_code',  # 围栏代码块
        'tables',       # 表格
        'toc',          # 目录
        'nl2br',        # 换行转换
        'attr_list',    # 属性列表
        'def_list',     # 定义列表
        'footnotes',    # 脚注
        'md_in_html',   # HTML中的Markdown
    ]
    
    # 创建Markdown实例
    md = markdown.Markdown(
        extensions=extensions,
        extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': False,
            },
            'toc': {
                'permalink': True,
                'permalink_title': '永久链接',
            }
        }
    )
    
    return md.convert(text)

def html_filter(text):
    """直接返回HTML内容（用于Tiptap编辑器）"""
    if text is None:
        return ''
    return text


def localtime_filter(value, fmt='%Y-%m-%d %H:%M'):
    """将数据库里的 UTC 时间统一转换为本地时间字符串。"""
    if value is None:
        return ''

    if not isinstance(value, datetime):
        return value

    if value.tzinfo is None:
        value = value.replace(tzinfo=ZoneInfo('UTC'))

    return value.astimezone(LOCAL_TZ).strftime(fmt)

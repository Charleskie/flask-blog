import markdown
from markdown.extensions import codehilite, fenced_code, tables, toc

def nl2br_filter(text):
    """将换行符转换为HTML的<br>标签"""
    if text is None:
        return ''
    return text.replace('\n', '<br>')

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
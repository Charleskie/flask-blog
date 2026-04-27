import html
import re

from app.utils.filters import markdown_filter


HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def normalize_plain_text(text):
    """将文本归一成适合摘要展示的一行纯文本。"""
    return WHITESPACE_RE.sub(" ", html.unescape(text or "")).strip()


def render_post_content(content, content_format="html"):
    """根据内容格式渲染文章正文。"""
    raw_content = content or ""
    if (content_format or "html").lower() == "markdown":
        return markdown_filter(raw_content)
    return raw_content


def extract_post_plain_text(content, content_format="html"):
    """从 HTML 或 Markdown 内容中提取纯文本。"""
    rendered_content = render_post_content(content, content_format)
    text_content = HTML_TAG_RE.sub(" ", rendered_content or "")
    return normalize_plain_text(text_content)

"""
PDF生成工具模块
用于将关于页面内容转换为PDF格式
"""

import os
import tempfile
import logging
import re
import html
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib import colors

# 配置日志
logger = logging.getLogger(__name__)


class PDFGenerator:
    """PDF生成器类"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_chinese_fonts()
        self._setup_custom_styles()
    
    def _setup_chinese_fonts(self):
        """设置中文字体支持"""
        try:
            # 注册中文字体
            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
            self.chinese_font = 'STSong-Light'
            self.body_font = 'STSong-Light'  # 正文使用轻量字体
            
            # 尝试注册粗体字体
            try:
                pdfmetrics.registerFont(UnicodeCIDFont('STSong'))
                self.bold_font = 'STSong'  # 标题使用粗体字体
                logger.info("成功注册中文字体: STSong-Light (正文) 和 STSong (标题)")
            except:
                self.bold_font = 'STSong-Light'  # 如果粗体字体不可用，使用轻量字体
                logger.info("成功注册中文字体: STSong-Light")
                
        except Exception as e:
            try:
                # 备选字体
                pdfmetrics.registerFont(UnicodeCIDFont('SimSun'))
                self.chinese_font = 'SimSun'
                self.body_font = 'SimSun'
                self.bold_font = 'SimSun'
                logger.info("成功注册中文字体: SimSun")
            except Exception as e2:
                # 如果都失败，使用默认字体
                self.chinese_font = 'Helvetica-Bold'
                self.body_font = 'Helvetica'
                self.bold_font = 'Helvetica-Bold'
                logger.warning(f"无法注册中文字体，使用默认字体: {str(e2)}")
    
    def _setup_custom_styles(self):
        """设置自定义样式"""
        # 标题样式
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=14,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#667eea'),
            fontName=self.bold_font  # 使用粗体字体
        ))
        
        # 主标题样式
        self.styles.add(ParagraphStyle(
            name='MainHeading',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#333333'),
            fontName=self.bold_font,  # 使用粗体字体
            borderWidth=1,
            # borderColor=HexColor('#667eea'),
            borderPadding=5
        ))
        
        # 二级标题样式
        self.styles.add(ParagraphStyle(
            name='SubHeading',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=16,
            textColor=HexColor('#444444'),
            fontName=self.bold_font  # 使用粗体字体
        ))
        
        # 三级标题样式
        self.styles.add(ParagraphStyle(
            name='SubSubHeading',
            parent=self.styles['Heading3'],
            fontSize=10,
            spaceAfter=6,
            spaceBefore=12,
            textColor=HexColor('#555555'),
            fontName=self.bold_font  # 使用粗体字体
        ))
        
        # 正文样式
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            textColor=HexColor('#333333'),
            fontName=self.body_font,  # 使用专门的正文字体
            leading=6  # 行间距
        ))
        
        # 页脚样式
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=HexColor('#666666'),
            fontName=self.chinese_font
        ))
    
    def _safe_text(self, text):
        """安全地处理文本，确保编码正确"""
        if not text:
            return ""
        
        # 确保是字符串
        if not isinstance(text, str):
            text = str(text)
        
        # 解码HTML实体
        text = html.unescape(text)
        
        # 移除或替换可能导致编码问题的字符
        text = text.replace('\u201c', '"').replace('\u201d', '"')  # 智能引号
        text = text.replace('\u2018', "'").replace('\u2019', "'")  # 智能单引号
        text = text.replace('\u2013', '-').replace('\u2014', '--')  # 破折号
        
        return text
    
    def _clean_html_content(self, html_content):
        """清理HTML内容，提取纯文本"""
        if not html_content:
            return ""
        
        # 确保输入是字符串
        if not isinstance(html_content, str):
            html_content = str(html_content)
        
        # 移除HTML标签
        clean_text = re.sub(r'<[^>]+>', '', html_content)
        
        # 解码HTML实体
        clean_text = html.unescape(clean_text)
        
        # 清理多余的空行
        clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)
        
        return clean_text.strip()
    
    def _parse_content_to_paragraphs(self, content):
        """将内容解析为段落列表"""
        paragraphs = []
        
        if not content:
            return paragraphs
        
        # 按行分割内容
        lines = content.split('\n')
        current_paragraph = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_paragraph:
                    paragraphs.append(self._safe_text(current_paragraph.strip()))
                    current_paragraph = ""
            else:
                # 检查是否是标题（以#开头或短行且包含中文）
                if (line.startswith('#') or 
                    (len(line) < 50 and any('\u4e00' <= char <= '\u9fff' for char in line))):
                    if current_paragraph:
                        paragraphs.append(self._safe_text(current_paragraph.strip()))
                        current_paragraph = ""
                    paragraphs.append(('heading', self._safe_text(line)))
                else:
                    if current_paragraph:
                        current_paragraph += " " + line
                    else:
                        current_paragraph = line
        
        if current_paragraph:
            paragraphs.append(self._safe_text(current_paragraph.strip()))
        
        return paragraphs
    
    def generate_about_pdf(self, page_title, page_content, base_url=None):
        """
        生成关于页面的PDF
        
        Args:
            page_title (str): 页面标题
            page_content (str): 页面内容（HTML格式）
            base_url (str): 基础URL，用于处理相对路径
            
        Returns:
            bytes: PDF文件的二进制数据
            
        Raises:
            Exception: PDF生成失败时抛出异常
        """
        try:
            logger.info(f"开始生成PDF: {page_title}")
            
            # 安全处理标题
            safe_title = self._safe_text(page_title)
            
            # 创建内存中的PDF文档
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # 构建PDF内容
            story = []
            
            # 添加标题
            title = Paragraph(safe_title, self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 20))
            
            # 添加副标题
            subtitle = Paragraph("个人简介文档", self.styles['Footer'])
            story.append(subtitle)
            story.append(Spacer(1, 30))
            
            # 清理HTML内容
            clean_content = self._clean_html_content(page_content)
            
            # 解析内容为段落
            paragraphs = self._parse_content_to_paragraphs(clean_content)
            
            # 添加内容段落
            for para in paragraphs:
                try:
                    if isinstance(para, tuple) and para[0] == 'heading':
                        # 处理标题
                        heading_text = para[1].lstrip('#').strip()
                        if heading_text:
                            if len(heading_text) < 20:
                                story.append(Paragraph(heading_text, self.styles['MainHeading']))
                            elif len(heading_text) < 40:
                                story.append(Paragraph(heading_text, self.styles['SubHeading']))
                            else:
                                story.append(Paragraph(heading_text, self.styles['SubSubHeading']))
                    else:
                        # 处理普通段落
                        if para and para.strip():
                            # 处理列表项
                            if para.strip().startswith('-') or para.strip().startswith('•'):
                                para = "• " + para.strip().lstrip('-•').strip()
                            
                            story.append(Paragraph(para, self.styles['CustomBody']))
                            story.append(Spacer(1, 6))
                except Exception as e:
                    logger.warning(f"处理段落时出错: {str(e)}")
                    # 如果处理失败，跳过这个段落
                    continue
            
            # 添加页脚信息
            story.append(Spacer(1, 30))
            story.append(Paragraph("─" * 30, self.styles['Footer']))
            story.append(Spacer(1, 10))
            
            generation_time = datetime.now().strftime('%Y年%m月%d日 %H:%M')
            footer_text = f"生成时间：{generation_time} | 本文档由个人网站自动生成"
            story.append(Paragraph(footer_text, self.styles['Footer']))
            
            # 构建PDF
            doc.build(story)
            
            # 获取PDF字节数据
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"PDF生成成功，大小: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"PDF生成失败: {str(e)}")
            raise Exception(f"PDF生成失败: {str(e)}")
    
    def save_pdf_to_file(self, pdf_bytes, filename):
        """
        将PDF字节数据保存到文件
        
        Args:
            pdf_bytes (bytes): PDF字节数据
            filename (str): 文件名
            
        Returns:
            str: 保存的文件路径
        """
        # 确保uploads目录存在
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
        pdf_dir = os.path.join(uploads_dir, 'pdfs')
        
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)
        
        # 生成文件路径
        file_path = os.path.join(pdf_dir, filename)
        
        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(pdf_bytes)
        
        return file_path


def generate_about_pdf(page_title, page_content, base_url=None):
    """
    便捷函数：生成关于页面PDF
    
    Args:
        page_title (str): 页面标题
        page_content (str): 页面内容（HTML格式）
        base_url (str): 基础URL
        
    Returns:
        bytes: PDF文件的二进制数据
    """
    generator = PDFGenerator()
    return generator.generate_about_pdf(page_title, page_content, base_url)
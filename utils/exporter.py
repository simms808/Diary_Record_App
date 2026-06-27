from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import csv
import os
from datetime import datetime

class Exporter:
    @staticmethod
    def export_to_pdf(diary_data, filepath):
        """导出单篇日记为PDF"""
        # 注册中文字体支持
        try:
            # 尝试使用系统中文字体
            font_paths = [
                'C:/Windows/Fonts/msyh.ttc',  # Windows 微软雅黑
                'C:/Windows/Fonts/simsun.ttc',  # Windows 宋体
                '/System/Library/Fonts/PingFang.ttc',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
            ]
            font_loaded = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        font_loaded = True
                        break
                    except:
                        continue
            if not font_loaded:
                # 使用默认字体
                font_name = 'Helvetica'
            else:
                font_name = 'ChineseFont'
        except:
            font_name = 'Helvetica'
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # 创建自定义样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        date_style = ParagraphStyle(
            'CustomDate',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=12,
            textColor='gray',
            spaceAfter=20
        )
        
        content_style = ParagraphStyle(
            'CustomContent',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=12,
            leading=18,
            spaceAfter=10
        )
        
        # 构建PDF内容
        story = []
        
        # 标题
        story.append(Paragraph(diary_data['title'], title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # 日期和天气
        date_text = f"日期: {diary_data['date']}"
        if diary_data.get('weather'):
            date_text += f" | 天气: {diary_data['weather']}"
        if diary_data.get('sentiment_score'):
            date_text += f" | 情感分数: {diary_data['sentiment_score']:.2f}"
        story.append(Paragraph(date_text, date_style))
        story.append(Spacer(1, 0.2*inch))
        
        # 标签
        if diary_data.get('tags'):
            tags_text = '标签: ' + ' '.join([f'#{tag}' for tag in diary_data['tags']])
            story.append(Paragraph(tags_text, date_style))
            story.append(Spacer(1, 0.2*inch))
        
        # 内容
        story.append(Paragraph('内容:', content_style))
        story.append(Spacer(1, 0.1*inch))
        # 处理内容中的换行
        content_lines = diary_data['content'].split('\n')
        for line in content_lines:
            story.append(Paragraph(line, content_style))
        
        doc.build(story)
    
    @staticmethod
    def export_to_csv(diaries, filepath):
        """导出日记列表为CSV"""
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', '标题', '日期', '天气', '情感分数', '标签'])
            
            for diary in diaries:
                tags_str = '、'.join(diary.get('tags', [])) if isinstance(diary, dict) else ''
                if not isinstance(diary, dict):
                    diary = diary.to_dict()
                writer.writerow([
                    diary['id'],
                    diary['title'],
                    diary['date'],
                    diary.get('weather', ''),
                    f"{diary.get('sentiment_score', 0):.2f}",
                    tags_str
                ])
import re
from datetime import datetime

def validate_date(date_str):
    """验证日期格式"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def get_current_date():
    """获取当前日期字符串"""
    return datetime.now().strftime('%Y-%m-%d')

def parse_tags(tag_string):
    """解析标签字符串，返回标签列表"""
    if not tag_string:
        return []
    # 按逗号或空格分割
    tags = re.split(r'[,，\s]+', tag_string.strip())
    return [t.strip() for t in tags if t.strip()]
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Diary:
    id: Optional[int] = None
    title: str = ''
    content: str = ''
    date: str = ''
    weather: str = ''
    sentiment_score: float = 0.0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.date:
            self.date = datetime.now().strftime('%Y-%m-%d')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'date': self.date,
            'weather': self.weather,
            'sentiment_score': self.sentiment_score,
            'tags': self.tags
        }
    
    @classmethod
    def from_db_row(cls, row, tags=None):
        """从数据库行创建Diary对象"""
        return cls(
            id=row[0],
            title=row[1],
            content=row[2],
            date=row[3],
            weather=row[4] or '',
            sentiment_score=row[5] or 0.0,
            tags=tags or []
        )
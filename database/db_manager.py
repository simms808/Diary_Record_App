import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='database/diary.db'):
        self.db_path = db_path
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """初始化数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建日记表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                date TEXT NOT NULL,
                weather TEXT,
                sentiment_score REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建标签表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        # 创建日记标签关联表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diary_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                diary_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                FOREIGN KEY (diary_id) REFERENCES diaries (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE,
                UNIQUE(diary_id, tag_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ============ 日记操作 ============
    def add_diary(self, title, content, date, weather='', sentiment_score=0, tags=None):
        """添加日记"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO diaries (title, content, date, weather, sentiment_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content, date, weather, sentiment_score))
        
        diary_id = cursor.lastrowid
        
        # 添加标签
        if tags:
            for tag_name in tags:
                tag_name = tag_name.strip()
                if tag_name:
                    # 获取或创建标签
                    cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag_name,))
                    cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
                    tag_id = cursor.fetchone()[0]
                    cursor.execute('INSERT INTO diary_tags (diary_id, tag_id) VALUES (?, ?)', 
                                 (diary_id, tag_id))
        
        conn.commit()
        conn.close()
        return diary_id
    
    def update_diary(self, diary_id, title, content, date, weather='', sentiment_score=0, tags=None):
        """更新日记"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE diaries 
            SET title = ?, content = ?, date = ?, weather = ?, 
                sentiment_score = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title, content, date, weather, sentiment_score, diary_id))
        
        # 删除旧标签关联
        cursor.execute('DELETE FROM diary_tags WHERE diary_id = ?', (diary_id,))
        
        # 添加新标签
        if tags:
            for tag_name in tags:
                tag_name = tag_name.strip()
                if tag_name:
                    cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag_name,))
                    cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
                    tag_id = cursor.fetchone()[0]
                    cursor.execute('INSERT INTO diary_tags (diary_id, tag_id) VALUES (?, ?)', 
                                 (diary_id, tag_id))
        
        conn.commit()
        conn.close()
    
    def delete_diary(self, diary_id):
        """删除日记"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM diaries WHERE id = ?', (diary_id,))
        conn.commit()
        conn.close()
    
    def get_all_diaries(self, tag_filter=None):
        """获取所有日记，可选按标签筛选"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if tag_filter:
            query = '''
                SELECT DISTINCT d.id, d.title, d.content, d.date, d.weather, d.sentiment_score
                FROM diaries d
                JOIN diary_tags dt ON d.id = dt.diary_id
                JOIN tags t ON dt.tag_id = t.id
                WHERE t.name = ? AND d.date IS NOT NULL AND d.date != ""
                ORDER BY d.date DESC
            '''
            cursor.execute(query, (tag_filter,))
        else:
            cursor.execute('''
                SELECT id, title, content, date, weather, sentiment_score
                FROM diaries
                WHERE date IS NOT NULL AND date != ""
                ORDER BY date DESC
            ''')
        
        diaries = cursor.fetchall()
        conn.close()
        return diaries
    
    def get_diary(self, diary_id):
        """获取单篇日记详情"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, content, date, weather, sentiment_score
            FROM diaries
            WHERE id = ?
        ''', (diary_id,))
        
        diary = cursor.fetchone()
        
        if diary:
            # 获取标签
            cursor.execute('''
                SELECT t.name
                FROM tags t
                JOIN diary_tags dt ON t.id = dt.tag_id
                WHERE dt.diary_id = ?
            ''', (diary_id,))
            tags = [row[0] for row in cursor.fetchall()]
            conn.close()
            return {'id': diary[0], 'title': diary[1], 'content': diary[2],
                    'date': diary[3], 'weather': diary[4], 'sentiment_score': diary[5],
                    'tags': tags}
        conn.close()
        return None
    
    # ============ 标签操作 ============
    def get_all_tags(self):
        """获取所有标签"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM tags ORDER BY name')
        tags = cursor.fetchall()
        conn.close()
        return tags
    
    def delete_tag(self, tag_id):
        """删除标签"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tags WHERE id = ?', (tag_id,))
        conn.commit()
        conn.close()
    
    # ============ 统计和趋势 ============
    def get_monthly_sentiment(self, year):
        """获取每月平均情感分数"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT strftime('%m', date) as month, AVG(sentiment_score) as avg_score
            FROM diaries
            WHERE strftime('%Y', date) = ? AND date IS NOT NULL AND date != ""
            GROUP BY month
            ORDER BY month
        ''', (str(year),))
        
        results = cursor.fetchall()
        conn.close()
        
        # 转换为完整月份列表
        monthly_data = {f'{i:02d}': None for i in range(1, 13)}
        for row in results:
            if row[0] is not None:  # 确保月份不为空
                monthly_data[row[0]] = row[1]
        
        return monthly_data
    
    def get_available_years(self):
        """获取有日记的年份列表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        # 过滤掉 date 为 NULL 或空字符串的记录
        cursor.execute('''
            SELECT DISTINCT strftime("%Y", date) as year 
            FROM diaries 
            WHERE date IS NOT NULL AND date != "" 
            ORDER BY year
        ''')
        years = []
        for row in cursor.fetchall():
            if row[0] is not None and row[0] != '':
                try:
                    years.append(int(row[0]))
                except (ValueError, TypeError):
                    continue
        conn.close()
        return years
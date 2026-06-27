"""
生成示例日记数据（精简版）
"""
import sqlite3
from utils.sentiment import SentimentAnalyzer

# 6条不同情绪的日记
sample_diaries = [
    {
        'title': '心情特别好！',
        'content': '今天天气晴朗，阳光明媚。出门散步时遇到一只可爱的小猫，感觉整个世界都美好了起来！',
        'date': '2026-01-15',
        'weather': '☀️ 晴'
    },
    {
        'title': '有点郁闷的一天',
        'content': '今天工作不太顺利，被领导批评了。心情有点低落，希望明天会更好。',
        'date': '2026-02-10',
        'weather': '🌧️ 雨'
    },
    {
        'title': '平淡的一天',
        'content': '今天没什么特别的事情发生，就是普通的上班、下班、吃饭、睡觉。',
        'date': '2026-03-05',
        'weather': '⛅ 多云'
    },
    {
        'title': '超级开心！',
        'content': '今天和朋友聚会玩了一整天，吃了美食，看了电影，聊了很多有趣的话题！',
        'date': '2026-04-12',
        'weather': '☀️ 晴'
    },
    {
        'title': '心情不好',
        'content': '今天生病了，发烧感冒浑身难受。一个人在家躺着，感觉特别孤独。',
        'date': '2026-05-08',
        'weather': '🌧️ 雨'
    },
    {
        'title': '很有成就感！',
        'content': '终于完成了期末大作业！感觉这几个月的努力没有白费，很有成就感！',
        'date': '2026-06-22',
        'weather': '☀️ 晴'
    }
]

def generate_data():
    conn = sqlite3.connect('database/diary.db')
    cursor = conn.cursor()
    analyzer = SentimentAnalyzer()
    
    for diary in sample_diaries:
        # 分析情感
        score = analyzer.analyze(diary['content'])
        
        # 插入数据
        cursor.execute('''
            INSERT INTO diaries (title, content, date, weather, sentiment_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (diary['title'], diary['content'], diary['date'], diary['weather'], score))
        
        print(f"✅ 添加: {diary['title']} (情感分数: {score:.2f})")
    
    conn.commit()
    conn.close()
    print("\n🎉 示例数据添加完成！运行程序查看情绪趋势图吧！")

if __name__ == '__main__':
    generate_data()
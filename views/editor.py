import tkinter as tk
from tkinter import ttk, scrolledtext
from utils.sentiment import SentimentAnalyzer

class DiaryEditor(ttk.Frame):
    def __init__(self, parent, on_save_callback, on_delete_callback):
        super().__init__(parent)
        self.on_save_callback = on_save_callback
        self.on_delete_callback = on_delete_callback
        self.sentiment_analyzer = SentimentAnalyzer()
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建编辑区组件"""
        # 标题
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(title_frame, text='标题:').pack(side=tk.LEFT, padx=5)
        self.title_var = tk.StringVar()
        ttk.Entry(title_frame, textvariable=self.title_var, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 日期
        ttk.Label(title_frame, text='日期:').pack(side=tk.LEFT, padx=5)
        self.date_var = tk.StringVar()
        ttk.Entry(title_frame, textvariable=self.date_var, width=12).pack(side=tk.LEFT, padx=5)
        
        # 天气
        ttk.Label(title_frame, text='天气:').pack(side=tk.LEFT, padx=5)
        self.weather_var = tk.StringVar()
        ttk.Combobox(title_frame, textvariable=self.weather_var, width=10,
                    values=['', '☀️ 晴', '⛅ 多云', '🌧️ 雨', '❄️ 雪', '🌤️ 阴']).pack(side=tk.LEFT, padx=5)
        
        # 标签
        tag_frame = ttk.Frame(self)
        tag_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(tag_frame, text='标签:').pack(side=tk.LEFT, padx=5)
        self.tags_var = tk.StringVar()
        ttk.Entry(tag_frame, textvariable=self.tags_var, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Label(tag_frame, text='(用逗号分隔)').pack(side=tk.LEFT, padx=5)
        
        # 情感显示
        sentiment_frame = ttk.Frame(self)
        sentiment_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.sentiment_label = ttk.Label(sentiment_frame, text='情感: 未分析')
        self.sentiment_label.pack(side=tk.LEFT, padx=5)
        
        self.sentiment_score_label = ttk.Label(sentiment_frame, text='分数: 0.00')
        self.sentiment_score_label.pack(side=tk.LEFT, padx=5)
        
        # 内容编辑器（富文本支持）
        content_frame = ttk.LabelFrame(self, text='内容')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, 
                                                      font=('Microsoft YaHei', 11))
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 绑定内容变化事件，实时分析情感
        self.content_text.bind('<KeyRelease>', self.on_content_changed)
        
        # 底部按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text='💾 保存', command=self.on_save_callback).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='🗑️ 删除', command=self.on_delete_callback).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='🔍 分析情感', command=self.analyze_sentiment).pack(side=tk.LEFT, padx=5)
    
    def load_diary(self, diary):
        """加载日记到编辑器"""
        self.title_var.set(diary['title'])
        self.content_text.delete('1.0', tk.END)
        self.content_text.insert('1.0', diary['content'])
        self.date_var.set(diary['date'])
        self.weather_var.set(diary['weather'] or '')
        self.tags_var.set(', '.join(diary['tags']))
        
        # 显示情感分析
        self.update_sentiment_display(diary['sentiment_score'])
    
    def clear(self):
        """清空编辑器"""
        self.title_var.set('')
        self.content_text.delete('1.0', tk.END)
        self.date_var.set('')
        self.weather_var.set('')
        self.tags_var.set('')
        self.sentiment_label.config(text='情感: 未分析')
        self.sentiment_score_label.config(text='分数: 0.00')
    
    def analyze_sentiment(self):
        """手动分析情感"""
        content = self.content_text.get('1.0', tk.END).strip()
        if content:
            score = self.sentiment_analyzer.analyze(content)
            self.update_sentiment_display(score)
        else:
            self.sentiment_label.config(text='情感: 无内容')
            self.sentiment_score_label.config(text='分数: 0.00')
    
    def on_content_changed(self, event):
        """内容变化时自动分析情感"""
        # 使用 after 延迟执行，避免频繁分析
        if hasattr(self, '_sentiment_after_id'):
            self.after_cancel(self._sentiment_after_id)
        self._sentiment_after_id = self.after(500, self.analyze_sentiment)
    
    def update_sentiment_display(self, score):
        """更新情感显示"""
        emoji = self.sentiment_analyzer.get_sentiment_emoji(score)
        label = self.sentiment_analyzer.get_sentiment_label(score)
        
        self.sentiment_label.config(text=f'情感: {emoji} {label}')
        self.sentiment_score_label.config(text=f'分数: {score:.2f}')
        
        # 根据情感分数改变颜色
        if score > 0.3:
            color = 'green'
        elif score > 0.1:
            color = 'lightgreen'
        elif score > -0.1:
            color = 'orange'
        elif score > -0.3:
            color = 'coral'
        else:
            color = 'red'
        
        self.sentiment_label.config(foreground=color)
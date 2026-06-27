import tkinter as tk
from tkinter import ttk
from utils.sentiment import SentimentAnalyzer

class DiaryList(ttk.Frame):
    def __init__(self, parent, on_select_callback):
        super().__init__(parent)
        self.on_select_callback = on_select_callback
        self.sentiment_analyzer = SentimentAnalyzer()
        self.diary_items = {}
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建列表组件"""
        # 列表框架
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 使用Text作为列表（支持颜色和表情）
        self.list_text = tk.Text(list_frame, yscrollcommand=scrollbar.set, 
                                 font=('Microsoft YaHei', 10), 
                                 wrap=tk.WORD, height=20)
        self.list_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.list_text.yview)
        
        # 绑定点击事件
        self.list_text.tag_bind('item', '<Button-1>', self.on_item_click)
        self.list_text.tag_bind('item', '<Enter>', self.on_item_enter)
        self.list_text.tag_bind('item', '<Leave>', self.on_item_leave)
        
        # 配置标签样式
        self.list_text.tag_configure('title', font=('Microsoft YaHei', 11, 'bold'))
        self.list_text.tag_configure('date', foreground='gray', font=('Microsoft YaHei', 9))
        self.list_text.tag_configure('tags', foreground='blue', font=('Microsoft YaHei', 9))
        self.list_text.tag_configure('selected', background='lightblue')
        self.list_text.tag_configure('normal', background='white')
    
    def load_diaries(self, diaries):
        """加载日记列表"""
        self.list_text.delete('1.0', tk.END)
        self.diary_items = {}
        
        for i, diary in enumerate(diaries):
            # 获取情感表情
            emoji = self.sentiment_analyzer.get_sentiment_emoji(diary['sentiment_score'])
            
            # 插入位置
            start_pos = self.list_text.index(tk.END)
            
            # 标题和表情
            title_text = f"{emoji} {diary['title']}"
            self.list_text.insert(tk.END, title_text + '\n', ('item', f'diary_{diary["id"]}'))
            self.list_text.insert(tk.END, '  ', ('item', f'diary_{diary["id"]}'))
            
            # 日期
            self.list_text.insert(tk.END, f"{diary['date']}", ('date', f'diary_{diary["id"]}'))
            
            # 标签
            if diary.get('tags'):
                tags_text = '  ' + ' '.join([f'#{tag}' for tag in diary['tags']])
                self.list_text.insert(tk.END, tags_text, ('tags', f'diary_{diary["id"]}'))
            
            # 内容预览
            content_preview = diary.get('content', '')[:50]
            if content_preview:
                self.list_text.insert(tk.END, f'\n  {content_preview}...', ('item', f'diary_{diary["id"]}'))
            
            self.list_text.insert(tk.END, '\n' + '-'*50 + '\n', ('item', f'diary_{diary["id"]}'))
            
            end_pos = self.list_text.index(tk.END)
            self.diary_items[diary['id']] = (start_pos, end_pos)
        
        # 配置标签
        for diary_id, (start, end) in self.diary_items.items():
            self.list_text.tag_add(f'diary_{diary_id}', start, end)
            self.list_text.tag_config(f'diary_{diary_id}', background='white')
    
    def on_item_click(self, event):
        """点击日记项"""
        # 获取点击位置
        index = self.list_text.index(f"@{event.x},{event.y}")
        # 检查点击位置的标签
        tags = self.list_text.tag_names(index)
        
        for tag in tags:
            if tag.startswith('diary_'):
                diary_id = int(tag.split('_')[1])
                self.select_diary(diary_id)
                self.on_select_callback(diary_id)
                break
    
    def on_item_enter(self, event):
        """鼠标悬停"""
        index = self.list_text.index(f"@{event.x},{event.y}")
        tags = self.list_text.tag_names(index)
        for tag in tags:
            if tag.startswith('diary_'):
                self.list_text.tag_config(tag, background='#e8f0fe')
                break
    
    def on_item_leave(self, event):
        """鼠标离开"""
        for diary_id in self.diary_items:
            self.list_text.tag_config(f'diary_{diary_id}', background='white')
    
    def select_diary(self, diary_id):
        """选中日记"""
        # 清除所有选中状态
        for item_id in self.diary_items:
            self.list_text.tag_config(f'diary_{item_id}', background='white')
        
        # 高亮选中的日记
        if diary_id in self.diary_items:
            self.list_text.tag_config(f'diary_{diary_id}', background='lightblue')
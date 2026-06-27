import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')

from database.db_manager import DatabaseManager
from utils.sentiment import SentimentAnalyzer
from utils.exporter import Exporter
from utils.helpers import get_current_date, parse_tags
from views.diary_list import DiaryList
from views.editor import DiaryEditor
from views.charts import ChartWindow

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('个人日记本与情绪分析系统')
        self.root.geometry('1200x700')
        
        # 初始化数据库和情感分析器
        self.db = DatabaseManager()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # 当前选中的日记ID
        self.current_diary_id = None
        self.current_tag_filter = None
        
        # 创建界面
        self.create_widgets()
        self.load_diaries()
    
    def create_widgets(self):
        """创建界面组件"""
        # 顶部工具栏
        self.create_toolbar()
        
        # 主内容区域（左右分栏）
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧 - 日记列表
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # 标签筛选栏
        self.create_tag_filter(left_frame)
        
        # 日记列表
        self.diary_list = DiaryList(left_frame, self.on_diary_selected)
        self.diary_list.pack(fill=tk.BOTH, expand=True)
        
        # 右侧 - 编辑区域
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        self.editor = DiaryEditor(right_frame, self.on_save_diary, self.on_delete_diary)
        self.editor.pack(fill=tk.BOTH, expand=True)
    
    def create_toolbar(self):
        """创建顶部工具栏"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # 添加日记按钮
        ttk.Button(toolbar, text='📝 新建日记', command=self.new_diary).pack(side=tk.LEFT, padx=5)
        
        # 导出按钮
        ttk.Button(toolbar, text='📄 导出PDF', command=self.export_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text='📊 导出CSV', command=self.export_csv).pack(side=tk.LEFT, padx=5)
        
        # 统计图表按钮
        ttk.Button(toolbar, text='📈 情绪趋势', command=self.show_charts).pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        ttk.Button(toolbar, text='🔄 刷新', command=self.load_diaries).pack(side=tk.LEFT, padx=5)
        
        # 分隔线
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # 标签管理
        ttk.Button(toolbar, text='🏷️ 标签管理', command=self.manage_tags).pack(side=tk.LEFT, padx=5)
    
    def create_tag_filter(self, parent):
        """创建标签筛选栏"""
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(filter_frame, text='标签筛选:').pack(side=tk.LEFT, padx=5)
        
        self.tag_filter_var = tk.StringVar(value='全部')
        self.tag_filter_combo = ttk.Combobox(filter_frame, textvariable=self.tag_filter_var, 
                                             state='readonly', width=15)
        self.tag_filter_combo.bind('<<ComboboxSelected>>', self.on_tag_filter_changed)
        self.tag_filter_combo.pack(side=tk.LEFT, padx=5)
        
        # 更新标签列表
        self.update_tag_filter_list()
    
    def update_tag_filter_list(self):
        """更新标签筛选下拉列表"""
        tags = self.db.get_all_tags()
        tag_names = ['全部'] + [tag[1] for tag in tags]
        self.tag_filter_combo['values'] = tag_names
        if self.tag_filter_var.get() not in tag_names:
            self.tag_filter_var.set('全部')
    
    def on_tag_filter_changed(self, event):
        """标签筛选变化"""
        selected = self.tag_filter_var.get()
        self.current_tag_filter = None if selected == '全部' else selected
        self.load_diaries()
    
    def load_diaries(self):
        """加载日记列表"""
        diaries = self.db.get_all_diaries(self.current_tag_filter)
        
        # 获取每篇日记的标签
        diary_data = []
        for row in diaries:
            tags = []
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.name FROM tags t
                JOIN diary_tags dt ON t.id = dt.tag_id
                WHERE dt.diary_id = ?
            ''', (row[0],))
            tags = [r[0] for r in cursor.fetchall()]
            conn.close()
            
            diary_data.append({
                'id': row[0],
                'title': row[1],
                'content': row[2][:100],
                'date': row[3],
                'weather': row[4],
                'sentiment_score': row[5] or 0,
                'tags': tags
            })
        
        self.diary_list.load_diaries(diary_data)
        self.update_tag_filter_list()
    
    def on_diary_selected(self, diary_id):
        """日记被选中"""
        self.current_diary_id = diary_id
        diary = self.db.get_diary(diary_id)
        if diary:
            self.editor.load_diary(diary)
    
    def new_diary(self):
        """新建日记"""
        self.current_diary_id = None
        self.editor.clear()
        # 设置默认日期
        self.editor.date_var.set(get_current_date())
    
    def on_save_diary(self):
        """保存日记"""
        title = self.editor.title_var.get().strip()
        content = self.editor.content_text.get('1.0', tk.END).strip()
        date = self.editor.date_var.get()
        weather = self.editor.weather_var.get().strip()
        tag_string = self.editor.tags_var.get().strip()
        
        if not title:
            messagebox.showwarning('警告', '请输入日记标题')
            return
        
        if not content:
            messagebox.showwarning('警告', '请输入日记内容')
            return
        
        # 情感分析
        sentiment_score = self.sentiment_analyzer.analyze(content)
        
        # 解析标签
        tags = parse_tags(tag_string)
        
        if self.current_diary_id:
            # 更新日记
            self.db.update_diary(self.current_diary_id, title, content, date, weather, 
                                sentiment_score, tags)
        else:
            # 添加日记
            self.current_diary_id = self.db.add_diary(title, content, date, weather, 
                                                     sentiment_score, tags)
        
        # 更新情感显示
        self.editor.update_sentiment_display(sentiment_score)
        
        # 刷新列表
        self.load_diaries()
        
        # 选中当前日记
        self.diary_list.select_diary(self.current_diary_id)
        
        messagebox.showinfo('成功', '日记已保存')
    
    def on_delete_diary(self):
        """删除日记"""
        if not self.current_diary_id:
            return
        
        if messagebox.askyesno('确认删除', '确定要删除这篇日记吗？'):
            self.db.delete_diary(self.current_diary_id)
            self.current_diary_id = None
            self.editor.clear()
            self.load_diaries()
            messagebox.showinfo('成功', '日记已删除')
    
    def export_pdf(self):
        """导出当前日记为PDF"""
        if not self.current_diary_id:
            messagebox.showwarning('警告', '请先选择一篇日记')
            return
        
        diary = self.db.get_diary(self.current_diary_id)
        if not diary:
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension='.pdf',
            filetypes=[('PDF文件', '*.pdf')],
            title='导出PDF'
        )
        
        if filepath:
            try:
                Exporter.export_to_pdf(diary, filepath)
                messagebox.showinfo('成功', f'PDF已导出到: {filepath}')
            except Exception as e:
                messagebox.showerror('错误', f'导出失败: {str(e)}')
    
    def export_csv(self):
        """导出所有日记为CSV"""
        diaries = self.db.get_all_diaries()
        diary_data = []
        for row in diaries:
            diary = self.db.get_diary(row[0])
            if diary:
                diary_data.append(diary)
        
        if not diary_data:
            messagebox.showwarning('警告', '没有日记可导出')
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV文件', '*.csv')],
            title='导出CSV'
        )
        
        if filepath:
            try:
                Exporter.export_to_csv(diary_data, filepath)
                messagebox.showinfo('成功', f'CSV已导出到: {filepath}')
            except Exception as e:
                messagebox.showerror('错误', f'导出失败: {str(e)}')
    
    def show_charts(self):
        """显示情绪趋势图"""
        years = self.db.get_available_years()
        if not years:
            messagebox.showwarning('警告', '没有日记数据，无法显示图表')
            return
        
        chart_window = tk.Toplevel(self.root)
        chart_window.title('情绪趋势分析')
        chart_window.geometry('800x600')
        
        ChartWindow(chart_window, self.db, years)
    
    def manage_tags(self):
        """标签管理窗口"""
        tag_window = tk.Toplevel(self.root)
        tag_window.title('标签管理')
        tag_window.geometry('400x400')
        
        # 标签列表
        list_frame = ttk.Frame(tag_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tag_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        tag_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=tag_listbox.yview)
        
        # 加载标签
        tags = self.db.get_all_tags()
        for tag in tags:
            tag_listbox.insert(tk.END, f"{tag[1]} (ID: {tag[0]})")
        
        # 删除按钮
        def delete_selected_tag():
            selection = tag_listbox.curselection()
            if not selection:
                return
            tag_text = tag_listbox.get(selection[0])
            tag_id = int(tag_text.split('ID: ')[1].rstrip(')'))
            
            if messagebox.askyesno('确认删除', f'确定要删除标签 "{tag_text.split(" (")[0]}" 吗？'):
                self.db.delete_tag(tag_id)
                tag_window.destroy()
                self.manage_tags()
                self.update_tag_filter_list()
                self.load_diaries()
        
        ttk.Button(tag_window, text='删除选中标签', command=delete_selected_tag).pack(pady=10)
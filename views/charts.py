import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class ChartWindow:
    def __init__(self, parent, db, years):
        self.parent = parent
        self.db = db
        self.years = years
        
        self.create_widgets()
        self.update_chart(years[0] if years else None)
    
    def create_widgets(self):
        """创建图表窗口组件"""
        # 年份选择
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(control_frame, text='选择年份:').pack(side=tk.LEFT, padx=5)
        
        self.year_var = tk.StringVar()
        year_combo = ttk.Combobox(control_frame, textvariable=self.year_var, 
                                  values=self.years, state='readonly', width=10)
        year_combo.pack(side=tk.LEFT, padx=5)
        if self.years:
            year_combo.set(self.years[0])
        year_combo.bind('<<ComboboxSelected>>', lambda e: self.update_chart(int(self.year_var.get())))
        
        # 图表区域
        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self.parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def update_chart(self, year):
        """更新图表"""
        if not year:
            return
        
        # 清空图表
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # 获取数据
        monthly_data = self.db.get_monthly_sentiment(year)
        
        months = ['1月', '2月', '3月', '4月', '5月', '6月', 
                 '7月', '8月', '9月', '10月', '11月', '12月']
        scores = [monthly_data[f'{i+1:02d}'] for i in range(12)]
        
        # 检查是否有数据
        if all(score is None for score in scores):
            ax.text(0.5, 0.5, f'{year}年没有日记数据', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
        else:
            # 替换None为0并标记
            plot_scores = [s if s is not None else 0 for s in scores]
            plot_months = [m for m, s in zip(months, scores) if s is not None]
            plot_scores_filtered = [s for s in scores if s is not None]
            
            if plot_scores_filtered:
                # 绘制折线图
                ax.plot(plot_months, plot_scores_filtered, marker='o', linewidth=2, 
                        markersize=8, color='#2196F3')
                
                # 添加水平参考线
                ax.axhline(y=0, color='gray', linestyle='--', alpha=0.3)
                
                # 添加数据标签
                for i, (month, score) in enumerate(zip(plot_months, plot_scores_filtered)):
                    ax.annotate(f'{score:.2f}', (month, score), 
                               textcoords="offset points", xytext=(0, 10), 
                               ha='center', fontsize=9)
                
                # 设置Y轴范围
                max_score = max(plot_scores_filtered) if plot_scores_filtered else 0.5
                min_score = min(plot_scores_filtered) if plot_scores_filtered else -0.5
                y_max = max(1.0, max_score + 0.2)
                y_min = min(-1.0, min_score - 0.2)
                ax.set_ylim(y_min, y_max)
                
                # 颜色区域
                ax.fill_between(plot_months, 0, plot_scores_filtered, 
                               where=[s > 0 for s in plot_scores_filtered],
                               color='green', alpha=0.2, interpolate=True)
                ax.fill_between(plot_months, 0, plot_scores_filtered,
                               where=[s < 0 for s in plot_scores_filtered],
                               color='red', alpha=0.2, interpolate=True)
        
        # 设置标题和标签
        ax.set_title(f'{year}年 情绪变化趋势', fontsize=14, fontweight='bold')
        ax.set_xlabel('月份', fontsize=12)
        ax.set_ylabel('情感分数', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # 设置刻度
        ax.set_xticklabels(months, rotation=0)
        
        # 调整布局
        self.figure.tight_layout()
        self.canvas.draw()
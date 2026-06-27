from textblob import TextBlob
import re

class SentimentAnalyzer:
    def __init__(self):
        # 尝试使用SnowNLP，如果不可用则使用TextBlob
        try:
            from snownlp import SnowNLP
            self.use_snownlp = True
            self.SnowNLP = SnowNLP
        except ImportError:
            self.use_snownlp = False
    
    def analyze(self, text):
        """
        分析文本情感，返回分数 (-1 到 1)
        负数表示消极，正数表示积极
        """
        if not text or not text.strip():
            return 0.0
        
        # 清理文本
        text = text.strip()
        
        try:
            if self.use_snownlp:
                # 使用SnowNLP
                s = self.SnowNLP(text)
                # SnowNLP返回0-1，转换为-1到1
                score = (s.sentiments - 0.5) * 2
                return round(score, 3)
            else:
                # 使用TextBlob
                blob = TextBlob(text)
                # TextBlob返回-1到1
                return round(blob.sentiment.polarity, 3)
        except:
            return 0.0
    
    def get_sentiment_emoji(self, score):
        """根据情感分数返回表情"""
        if score > 0.3:
            return '😊'  # 非常积极
        elif score > 0.1:
            return '🙂'  # 积极
        elif score > -0.1:
            return '😐'  # 中性
        elif score > -0.3:
            return '🙁'  # 消极
        else:
            return '😢'  # 非常消极
    
    def get_sentiment_label(self, score):
        """根据情感分数返回标签"""
        if score > 0.3:
            return '非常积极'
        elif score > 0.1:
            return '积极'
        elif score > -0.1:
            return '中性'
        elif score > -0.3:
            return '消极'
        else:
            return '非常消极'
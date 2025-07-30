import requests
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime, timedelta
import os

class WakaTimeProcessor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://wakatime.com/api/v1"
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def get_stats(self, range_type="last_7_days"):
        """获取统计数据"""
        url = f"{self.base_url}/users/current/stats/{range_type}"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_languages_data(self):
        """获取编程语言数据"""
        stats = self.get_stats()
        languages = stats['data']['languages']
        
        # 只保留使用时间超过30分钟的语言
        filtered_languages = [
            lang for lang in languages 
            if lang['total_seconds'] > 1800
        ]
        
        return filtered_languages[:5]  # 只要前5种语言
    
    def generate_clean_chart(self):
        """生成图表"""
        languages = self.get_languages_data()
        
        colors = ['#DD5500', '#00DD55', '#5500DD', '#DDDD00', '#DD0055']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('white')
        
        names = [lang['name'] for lang in languages]
        hours = [lang['total_seconds'] / 3600 for lang in languages]
        
        bars = ax.barh(names, hours, color=colors[:len(names)])
        
        ax.set_xlabel('Hours', fontsize=12, fontweight='bold')
        ax.set_title('Weekly Coding Activity', fontsize=16, fontweight='bold', pad=20)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        for i, (bar, hour) in enumerate(zip(bars, hours)):
            ax.text(hour + 0.1, i, f'{hour:.1f}h', 
                   va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('wakatime_stats.png', dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    api_key = os.environ.get('WAKATIME_API_KEY')
    processor = WakaTimeProcessor(api_key)
    processor.generate_clean_chart()
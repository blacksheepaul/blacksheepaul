import requests
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime, timedelta
import os
import base64
import argparse

# Set matplotlib backend for SVG output
plt.switch_backend('svg')

class WakaTimeProcessor:
    def __init__(self, api_key=None, test_mode=False):
        self.test_mode = test_mode
        if not test_mode:
            self.api_key = api_key
            self.base_url = "https://wakatime.com/api/v1"
            # Encode API key using base64 for HTTP Basic Auth
            encoded_key = base64.b64encode(api_key.encode()).decode()
            self.headers = {"Authorization": f"Basic {encoded_key}"}
    
    def get_mock_data(self):
        """返回模拟测试数据"""
        return {
            'data': {
                'languages': [
                    {'name': 'Python', 'total_seconds': 25200, 'percent': 45.2},
                    {'name': 'JavaScript', 'total_seconds': 14400, 'percent': 25.8},
                    {'name': 'TypeScript', 'total_seconds': 7200, 'percent': 12.9},
                    {'name': 'HTML', 'total_seconds': 5400, 'percent': 9.7},
                    {'name': 'CSS', 'total_seconds': 3600, 'percent': 6.4},
                    {'name': 'JSON', 'total_seconds': 1200, 'percent': 2.1}
                ]
            }
        }
    
    def get_stats(self, range_type="last_7_days"):
        """获取统计数据"""
        if self.test_mode:
            return self.get_mock_data()
        
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
        
        # 按使用时间降序排列，时间最长的在前
        filtered_languages.sort(key=lambda x: x['total_seconds'], reverse=True)
        
        return filtered_languages[:5]  # 只要前5种语言
    
    def generate_clean_chart(self):
        """生成图表"""
        languages = self.get_languages_data()
        
        colors = ['#DD5500', '#00DD55', '#5500DD', '#DDDD00', '#DD0055']
        
        # 减少高度以缩短柱形宽度
        fig, ax = plt.subplots(figsize=(10, 3))
        fig.patch.set_facecolor('white')
        
        # 反转顺序，使时长最长的在顶部
        names = [lang['name'] for lang in reversed(languages)]
        hours = [lang['total_seconds'] / 3600 for lang in reversed(languages)]
        
        bars = ax.barh(names, hours, color=colors[:len(names)])
        
        ax.get_xaxis().set_visible(False)
        ax.set_title('Weekly Coding Activity', fontsize=16, fontweight='bold', pad=20)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        
        for i, (bar, hour) in enumerate(zip(bars, hours)):
            ax.text(hour + 0.1, i, f'{hour:.1f}h', 
                   va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('wakatime_stats.svg', format='svg', bbox_inches='tight')
        plt.close()
        print("Chart saved as wakatime_stats.svg")

def main():
    parser = argparse.ArgumentParser(description='Generate WakaTime coding activity chart')
    parser.add_argument('--test', action='store_true', help='Run in test mode with mock data')
    args = parser.parse_args()
    
    if args.test:
        print("Running in test mode with mock data...")
        processor = WakaTimeProcessor(test_mode=True)
    else:
        api_key = os.environ.get('WAKATIME_API_KEY')
        if not api_key:
            print("Error: WAKATIME_API_KEY environment variable not set")
            return
        processor = WakaTimeProcessor(api_key)
    
    processor.generate_clean_chart()

if __name__ == "__main__":
    main()
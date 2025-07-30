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

class SteamProcessor:
    def __init__(self, steam_api_key=None, steam_id=None, test_mode=False):
        self.test_mode = test_mode
        if not test_mode:
            self.steam_api_key = steam_api_key
            self.steam_id = steam_id
    
    def get_mock_steam_data(self):
        """返回模拟Steam数据"""
        return [
            {'name': 'Baldur\'s Gate 3', 'playtime_2weeks': 28800},  # 8 hours in seconds
            {'name': 'Cyberpunk 2077', 'playtime_2weeks': 21600},   # 6 hours in seconds
            {'name': 'Elden Ring', 'playtime_2weeks': 14400},       # 4 hours in seconds
        ]
    
    def get_steam_owned_games(self):
        """获取Steam拥有的所有游戏"""
        if self.test_mode:
            return [
                {'name': 'The Witcher 3: Wild Hunt', 'playtime_forever': 3600000},  # 1000 hours
                {'name': 'Counter-Strike: Global Offensive', 'playtime_forever': 2160000},  # 600 hours
                {'name': 'Dota 2', 'playtime_forever': 1800000},  # 500 hours
                {'name': 'Cyberpunk 2077', 'playtime_forever': 720000},  # 200 hours
                {'name': 'Baldur\'s Gate 3', 'playtime_forever': 540000},  # 150 hours
            ]
        
        if not self.steam_api_key or not self.steam_id:
            return []
        
        url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        params = {
            'key': self.steam_api_key,
            'steamid': self.steam_id,
            'format': 'json',
            'include_appinfo': True,
            'include_played_free_games': True
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if 'response' in data and 'games' in data['response']:
                games = data['response']['games']
                # 获取有游玩时间的游戏，按总游玩时间排序
                owned_games = [
                    {'name': game.get('name', 'Unknown Game'), 'playtime_forever': game.get('playtime_forever', 0) * 60}  # 转换为秒
                    for game in games 
                    if game.get('playtime_forever', 0) > 0
                ]
                owned_games.sort(key=lambda x: x['playtime_forever'], reverse=True)
                return owned_games[:5]  # 最多5个游戏
        except Exception as e:
            print(f"Error fetching Steam owned games: {e}")
        
        return []

    def get_steam_recent_games(self):
        """获取Steam最近游玩的游戏"""
        if self.test_mode:
            return self.get_mock_steam_data()
        
        if not self.steam_api_key or not self.steam_id:
            return []
        
        url = f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/"
        params = {
            'key': self.steam_api_key,
            'steamid': self.steam_id,
            'format': 'json'
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if 'response' in data and 'games' in data['response']:
                games = data['response']['games']
                # 过滤最近2周有游玩记录的游戏，按游玩时间排序
                recent_games = [
                    {'name': game['name'], 'playtime_2weeks': game.get('playtime_2weeks', 0) * 60}  # 转换为秒
                    for game in games 
                    if game.get('playtime_2weeks', 0) > 0
                ]
                recent_games.sort(key=lambda x: x['playtime_2weeks'], reverse=True)
                return recent_games[:5]  # 最多5个游戏
        except Exception as e:
            print(f"Error fetching Steam data: {e}")
        
        return []
    
    def format_time(self, total_seconds):
        """格式化时间显示"""
        total_hours = total_seconds / 3600
        
        # 对于超过1000小时的，显示为简化格式
        if total_hours >= 1000:
            return f"{total_hours:.0f} hrs"
        elif total_hours >= 100:
            return f"{total_hours:.0f} hrs"
        elif total_hours >= 10:
            return f"{total_hours:.1f} hrs"
        else:
            hours = int(total_hours)
            minutes = int((total_hours - hours) * 60)
            
            if hours == 0:
                return f"{minutes} mins"
            elif minutes == 0:
                hour_text = "hr" if hours == 1 else "hrs"
                return f"{hours} {hour_text}"
            else:
                hour_text = "hr" if hours == 1 else "hrs"
                return f"{hours} {hour_text} {minutes} mins"
    
    def generate_steam_chart(self):
        """生成Steam游戏时间图表"""
        games = self.get_steam_recent_games()
        chart_title = 'Weekly Gaming Activity'
        time_key = 'playtime_2weeks'
        
        # 如果没有最近游戏活动，使用总游戏时长
        if not games:
            print("No recent gaming activity, showing top games by total playtime")
            games = self.get_steam_owned_games()
            chart_title = 'Top Games by Total Playtime'
            time_key = 'playtime_forever'
        
        if not games:
            print("No gaming activity to display")
            return
        
        # 游戏活动颜色（蓝绿色系）
        colors = ['#0066CC', '#3388DD', '#55AAEE', '#77BBFF', '#99CCFF']
        
        fig, ax = plt.subplots(figsize=(7.62, 2.56))
        fig.patch.set_facecolor('white')
        
        # 反转顺序，使时长最长的在顶部
        games_reversed = list(reversed(games))
        hours = [game[time_key] / 3600 for game in games_reversed]
        y_positions = range(len(games_reversed))
        
        # 绘制柱状图
        bars = ax.barh(y_positions, hours, left=0, color=colors[:len(games_reversed)], height=0.6)
        
        ax.get_xaxis().set_visible(False)
        ax.set_title(chart_title, fontsize=16, fontweight='bold', pad=20)
        
        # 完全隐藏Y轴
        ax.set_yticks([])
        ax.set_yticklabels([])
        ax.tick_params(left=False)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        
        max_hour = max(hours) if hours else 1
        
        # 显示游戏名称和时间
        for i, game in enumerate(games_reversed):
            ax.text(-max_hour * 0.95, i, game['name'], 
                   va='center', ha='left', fontweight='bold')
            time_text = self.format_time(game[time_key])
            ax.text(-max_hour * 0.5, i, time_text, 
                   va='center', ha='left', fontweight='bold')
        
        ax.set_xlim(-max_hour, max_hour * 1.1)
        
        plt.tight_layout()
        plt.savefig('steam_stats.svg', format='svg', bbox_inches='tight')
        plt.close()
        print("Steam chart saved as steam_stats.svg")

    def generate_steam_dark_chart(self):
        """生成Steam黑暗主题图表"""
        games = self.get_steam_recent_games()
        chart_title = 'Weekly Gaming Activity'
        time_key = 'playtime_2weeks'
        
        # 如果没有最近游戏活动，使用总游戏时长
        if not games:
            print("No recent gaming activity, showing top games by total playtime")
            games = self.get_steam_owned_games()
            chart_title = 'Top Games by Total Playtime'
            time_key = 'playtime_forever'
        
        if not games:
            print("No gaming activity to display")
            return
        
        # 黑暗主题颜色
        colors = ['#4ECDC4', '#6EDDD4', '#8EEEE4', '#AEFFF4', '#CEFFFF']
        
        fig, ax = plt.subplots(figsize=(7.62, 2.56))
        fig.patch.set_facecolor('#1e1e1e')
        
        games_reversed = list(reversed(games))
        hours = [game[time_key] / 3600 for game in games_reversed]
        y_positions = range(len(games_reversed))
        
        bars = ax.barh(y_positions, hours, left=0, color=colors[:len(games_reversed)], height=0.6)
        
        ax.get_xaxis().set_visible(False)
        ax.set_title(chart_title, fontsize=16, fontweight='bold', pad=20, color='white')
        ax.set_facecolor('#1e1e1e')
        
        ax.set_yticks([])
        ax.set_yticklabels([])
        ax.tick_params(left=False)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        
        max_hour = max(hours) if hours else 1
        
        for i, game in enumerate(games_reversed):
            ax.text(-max_hour * 0.95, i, game['name'], 
                   va='center', ha='left', fontweight='bold', color='white')
            time_text = self.format_time(game[time_key])
            ax.text(-max_hour * 0.5, i, time_text, 
                   va='center', ha='left', fontweight='bold', color='#cccccc')
        
        ax.set_xlim(-max_hour, max_hour * 1.1)
        
        plt.tight_layout()
        plt.savefig('steam_stats_dark.svg', format='svg', bbox_inches='tight')
        plt.close()
        print("Steam dark theme chart saved as steam_stats_dark.svg")

def main():
    parser = argparse.ArgumentParser(description='Generate Steam gaming activity chart')
    parser.add_argument('--test', action='store_true', help='Run in test mode with mock data')
    args = parser.parse_args()
    
    if args.test:
        print("Running in test mode with mock data...")
        processor = SteamProcessor(test_mode=True)
    else:
        steam_api_key = os.environ.get('STEAM_API_KEY')
        steam_id = os.environ.get('STEAM_ID')
        
        if not steam_api_key or not steam_id:
            print("Error: STEAM_API_KEY and STEAM_ID environment variables must be set")
            return
        
        processor = SteamProcessor(steam_api_key, steam_id)
    
    # 生成Steam图表
    processor.generate_steam_chart()
    processor.generate_steam_dark_chart()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
AI龙虾群聊 - Web版
Flask Web服务器，端口3000
支持多API: xAI (Grok) / Deepseek
支持Polymarket每日热门市场推荐
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API配置
API_PROVIDER = os.getenv("API_PROVIDER", "deepseek").lower()

if API_PROVIDER == "xai":
    API_KEY = os.getenv("XAI_API_KEY")
    BASE_URL = "https://api.x.ai/v1"
    MODEL = "grok-2-latest"
elif API_PROVIDER == "deepseek":
    API_KEY = os.getenv("DEEPSEEK_API_KEY")
    BASE_URL = "https://api.deepseek.com"
    MODEL = "deepseek-chat"
else:
    API_KEY = None
    BASE_URL = None
    MODEL = None

# Polymarket数据路径
HOT_MARKETS_FILE = 'data/hot_markets.json'

# 配置日志 - 同时输出到文件和内存
class LogBuffer:
    """内存日志缓冲区，用于在网页显示"""
    def __init__(self, max_lines=100):
        self.lines = []
        self.max_lines = max_lines
    
    def write(self, line):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.lines.append(f"[{timestamp}] {line}")
        if len(self.lines) > self.max_lines:
            self.lines.pop(0)
    
    def get_logs(self):
        return self.lines
    
    def clear(self):
        self.lines = []

log_buffer = LogBuffer()

# 配置Flask
app = Flask(__name__)
app.config['PORT'] = 3000
app.config['JSON_AS_ASCII'] = False

# 存储当前聊天状态
chat_state = {
    'is_running': False,
    'topic': None,
    'messages': [],
    'current_round': 0,
    'total_rounds': 0,
    'error': None
}

def get_hot_markets():
    """获取热门市场数据"""
    try:
        with open(HOT_MARKETS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        markets = data.get('markets', [])
        updated_at = data.get('updated_at', '')
        
        # 格式化市场数据
        formatted = []
        for m in markets:
            outcomes_str = ' / '.join([
                f"{o['label']}({o['probability']:.0f}%)"
                for o in m.get('outcomes', [])[:2]
            ])
            formatted.append({
                'id': m.get('id', ''),
                'question': m.get('question', ''),
                'outcomes': outcomes_str,
                'volume': m.get('volume', 0),
                'url': m.get('url', ''),
                'updated_at': updated_at
            })
        
        return formatted
    except Exception as e:
        print(f"读取市场数据失败: {e}")
        return []

@app.route('/')
def index():
    """主页"""
    return render_template('index.html', api_provider=API_PROVIDER.upper())

@app.route('/api/config')
def get_config():
    """获取API配置"""
    return jsonify({
        'api_provider': API_PROVIDER,
        'model': MODEL,
        'api_key_configured': bool(API_KEY)
    })

@app.route('/api/hot-markets')
def get_hot_markets_api():
    """获取Polymarket热门市场"""
    markets = get_hot_markets()
    
    # 检查数据是否过期
    data_age = "未知"
    try:
        with open(HOT_MARKETS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            updated_at = datetime.fromisoformat(data.get('updated_at', '2000-01-01'))
            age = datetime.now() - updated_at
            if age < timedelta(hours=1):
                data_age = f"{age.seconds // 60}分钟前"
            else:
                data_age = f"{age.seconds // 3600}小时前"
    except:
        pass
    
    return jsonify({
        'markets': markets,
        'count': len(markets),
        'data_age': data_age
    })

@app.route('/api/start', methods=['POST'])
def start_chat():
    """开始新的群聊"""
    global chat_state
    
    # 检查API Key
    if not API_KEY:
        error_msg = f"未配置 {API_PROVIDER.upper()}_API_KEY"
        log_buffer.write(f"错误: {error_msg}")
        return jsonify({'status': 'error', 'error': error_msg}), 400
    
    data = request.json
    topic = data.get('topic', 'AI人工智能')
    rounds = data.get('rounds', 6)
    market_data = data.get('market_data', None)  # 可选的市场数据
    
    log_buffer.clear()
    log_buffer.write(f"使用 {API_PROVIDER.upper()} API")
    log_buffer.write(f"开始新的群聊: {topic}, {rounds}轮")
    
    chat_state = {
        'is_running': True,
        'topic': topic,
        'messages': [],
        'current_round': 0,
        'total_rounds': rounds,
        'error': None
    }
    
    # 在后台线程运行聊天
    import threading
    thread = threading.Thread(target=run_chat_thread, args=(topic, rounds, market_data))
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started', 'topic': topic, 'rounds': rounds})

@app.route('/api/status')
def get_status():
    """获取当前状态"""
    return jsonify(chat_state)

@app.route('/api/logs')
def get_logs():
    """获取日志"""
    return jsonify({'logs': log_buffer.get_logs()})

@app.route('/api/clear', methods=['POST'])
def clear_chat():
    """清除聊天"""
    global chat_state
    chat_state = {
        'is_running': False,
        'topic': None,
        'messages': [],
        'current_round': 0,
        'total_rounds': 0,
        'error': None
    }
    log_buffer.clear()
    return jsonify({'status': 'cleared'})

@app.route('/api/update-markets', methods=['POST'])
def update_markets():
    """手动触发更新市场数据"""
    try:
        from polymarket import update_hot_markets
        success = update_hot_markets()
        if success:
            return jsonify({'status': 'success', 'message': '市场数据已更新'})
        else:
            return jsonify({'status': 'error', 'message': '更新失败'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def run_chat_thread(topic, rounds, market_data=None):
    """在后台线程运行聊天"""
    global chat_state
    
    try:
        # 导入必要的模块
        sys.path.insert(0, '/root/.openclaw/workspace/lobster-ai')
        from main import LobsterChat
        
        log_buffer.write("初始化龙虾群聊...")
        chat = LobsterChat()
        
        # 设置回调函数来更新消息
        chat.message_callback = add_message_callback
        chat.round_callback = update_round_callback
        chat.log_callback = log_callback
        
        # 如果有市场数据，添加到话题中
        if market_data:
            full_topic = f"""{topic}

【Polymarket市场数据】
问题: {market_data.get('question', '')}
当前赔率: {market_data.get('outcomes', '')}
交易量: ${market_data.get('volume', 0):,.0f}
"""
        else:
            full_topic = topic
        
        # 运行辩论
        chat.run_debate(full_topic, rounds=rounds)
        
        chat_state['is_running'] = False
        log_buffer.write("群聊结束！")
        
    except Exception as e:
        error_msg = str(e)
        chat_state['error'] = error_msg
        chat_state['is_running'] = False
        log_buffer.write(f"错误: {error_msg}")
        import traceback
        log_buffer.write(traceback.format_exc())

def add_message_callback(lobster_name, message, emoji):
    """添加消息的回调"""
    chat_state['messages'].append({
        'name': lobster_name,
        'message': message,
        'emoji': emoji,
        'time': datetime.now().strftime("%H:%M:%S")
    })

def update_round_callback(current, total):
    """更新轮次的回调"""
    chat_state['current_round'] = current
    chat_state['total_rounds'] = total
    log_buffer.write(f"第 {current}/{total} 轮")

def log_callback(msg):
    """日志回调"""
    log_buffer.write(msg)

if __name__ == '__main__':
    print("🦞 AI龙虾群聊 Web服务器启动中...")
    print(f"API提供商: {API_PROVIDER.upper()}")
    print(f"模型: {MODEL}")
    print(f"访问地址: http://localhost:3000")
    print("按 Ctrl+C 停止服务器\n")
    
    app.run(host='0.0.0.0', port=3000, debug=False)

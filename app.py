#!/usr/bin/env python3
"""
AI龙虾群聊 - Web版
Flask Web服务器，端口3000
支持多API: xAI (Grok) / Deepseek
"""

import os
import sys
import json
import logging
from datetime import datetime
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

@app.route('/api/topics')
def get_topics():
    """获取可选话题列表"""
    from lobsters import HOT_TOPICS
    return jsonify({
        'topics': [
            {'id': i, 'text': t}
            for i, t in enumerate(HOT_TOPICS)
        ]
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
    thread = threading.Thread(target=run_chat_thread, args=(topic, rounds))
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

def run_chat_thread(topic, rounds):
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
        
        # 运行辩论
        chat.run_debate(topic, rounds=rounds)
        
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

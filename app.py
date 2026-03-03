#!/usr/bin/env python3
"""
AI龙虾群聊 - Web版
Flask Web服务器，端口3000
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
    'stock': None,
    'messages': [],
    'current_round': 0,
    'total_rounds': 0,
    'error': None
}

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/stocks')
def get_stocks():
    """获取可选股票列表"""
    from lobsters import CONTROVERSIAL_STOCKS
    return jsonify({
        'stocks': [
            {'symbol': s.split(' - ')[0], 'name': s.split(' - ')[1] if ' - ' in s else s}
            for s in CONTROVERSIAL_STOCKS
        ]
    })

@app.route('/api/start', methods=['POST'])
def start_chat():
    """开始新的群聊"""
    global chat_state
    
    data = request.json
    stock = data.get('stock', 'TSLA')
    rounds = data.get('rounds', 6)
    
    log_buffer.clear()
    log_buffer.write(f"开始新的群聊: {stock}, {rounds}轮")
    
    chat_state = {
        'is_running': True,
        'stock': stock,
        'messages': [],
        'current_round': 0,
        'total_rounds': rounds,
        'error': None
    }
    
    # 在后台线程运行聊天
    import threading
    thread = threading.Thread(target=run_chat_thread, args=(stock, rounds))
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started', 'stock': stock, 'rounds': rounds})

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
        'stock': None,
        'messages': [],
        'current_round': 0,
        'total_rounds': 0,
        'error': None
    }
    log_buffer.clear()
    return jsonify({'status': 'cleared'})

def run_chat_thread(stock, rounds):
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
        chat.run_debate(stock, rounds=rounds)
        
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
    print(f"访问地址: http://localhost:3000")
    print("按 Ctrl+C 停止服务器\n")
    
    app.run(host='0.0.0.0', port=3000, debug=False)

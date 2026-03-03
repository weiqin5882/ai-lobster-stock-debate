#!/usr/bin/env python3
"""
AI龙虾群聊 - CEO全权负责版 Web服务器
端口3000 | 立场明确 + 多数据源 + 质量监控
"""

import os
import sys
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入CEO数据模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_provider import data_provider, save_markets_data

# Polymarket数据路径
HOT_MARKETS_FILE = 'data/hot_markets.json'

# 配置日志
class LogBuffer:
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

# 聊天状态
chat_state = {
    'is_running': False,
    'topic': None,
    'messages': [],
    'current_round': 0,
    'total_rounds': 0,
    'stance_stats': {},  # CEO新增：立场统计
    'error': None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/hot-markets')
def get_hot_markets():
    """获取热门市场"""
    try:
        with open(HOT_MARKETS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        markets = data.get('markets', [])
        updated_at = data.get('updated_at', '')
        
        # 计算数据年龄
        data_age = "未知"
        try:
            updated = datetime.fromisoformat(updated_at)
            age = datetime.now() - updated
            if age < timedelta(hours=1):
                data_age = f"{age.seconds // 60}分钟前"
            else:
                data_age = f"{age.seconds // 3600}小时前"
        except:
            pass
        
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
            })
        
        return jsonify({'markets': formatted, 'count': len(formatted), 'data_age': data_age})
    except Exception as e:
        return jsonify({'markets': [], 'error': str(e)})

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    """获取股票数据"""
    try:
        data = data_provider.get_stock_data(symbol.upper())
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/start', methods=['POST'])
def start_chat():
    """开始投研"""
    global chat_state
    
    API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("XAI_API_KEY")
    if not API_KEY:
        return jsonify({'status': 'error', 'error': 'API Key未配置'}), 400
    
    data = request.json
    topic = data.get('topic', 'TSLA')
    rounds = data.get('rounds', 6)
    market_data = data.get('market_data')
    
    # 尝试获取股票数据
    stock_data = None
    for symbol in ['TSLA', 'NVDA', 'AAPL', 'BTC']:
        if symbol in topic.upper():
            stock_data = data_provider.get_stock_data(symbol)
            break
    
    log_buffer.clear()
    log_buffer.write(f"CEO启动投研: {topic}")
    
    chat_state = {
        'is_running': True,
        'topic': topic,
        'messages': [],
        'current_round': 0,
        'total_rounds': rounds,
        'stance_stats': {},
        'error': None
    }
    
    import threading
    thread = threading.Thread(target=run_chat_thread, args=(topic, rounds, market_data, stock_data))
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started', 'topic': topic, 'rounds': rounds})

@app.route('/api/status')
def get_status():
    return jsonify(chat_state)

@app.route('/api/logs')
def get_logs():
    return jsonify({'logs': log_buffer.get_logs()})

@app.route('/api/clear', methods=['POST'])
def clear_chat():
    global chat_state
    chat_state = {
        'is_running': False,
        'topic': None,
        'messages': [],
        'current_round': 0,
        'total_rounds': 0,
        'stance_stats': {},
        'error': None
    }
    log_buffer.clear()
    return jsonify({'status': 'cleared'})

@app.route('/api/update-markets', methods=['POST'])
def update_markets():
    """CEO手动更新市场数据"""
    try:
        log_buffer.write("CEO手动更新市场数据...")
        markets = data_provider.get_polymarket_hot(20)
        if markets:
            save_markets_data(markets)
            log_buffer.write(f"✅ 更新成功，获取{len(markets)}个市场")
            return jsonify({'status': 'success', 'count': len(markets)})
        else:
            return jsonify({'status': 'error', 'message': '获取失败'}), 500
    except Exception as e:
        log_buffer.write(f"❌ 更新失败: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def run_chat_thread(topic, rounds, market_data=None, stock_data=None):
    """CEO监督下的投研线程"""
    global chat_state
    
    try:
        from main import LobsterChat
        
        log_buffer.write("CEO初始化龙虾群聊...")
        chat = LobsterChat()
        chat.set_market_data(market_data, stock_data)
        
        chat.message_callback = add_message_callback
        chat.round_callback = update_round_callback
        chat.log_callback = log_callback
        
        log_buffer.write("开始立场明确投研对决...")
        chat.run_debate(topic, rounds=rounds)
        
        # 保存立场统计
        chat_state['stance_stats'] = chat.stance_stats
        chat_state['is_running'] = False
        
        log_buffer.write("✅ CEO投研结束")
        
    except Exception as e:
        error_msg = str(e)
        chat_state['error'] = error_msg
        chat_state['is_running'] = False
        log_buffer.write(f"❌ CEO错误: {error_msg}")
        import traceback
        log_buffer.write(traceback.format_exc())

def add_message_callback(lobster_name, message, emoji):
    chat_state['messages'].append({
        'name': lobster_name,
        'message': message,
        'emoji': emoji,
        'time': datetime.now().strftime("%H:%M:%S")
    })

def update_round_callback(current, total):
    chat_state['current_round'] = current
    chat_state['total_rounds'] = total
    log_buffer.write(f"第 {current}/{total} 轮")

def log_callback(msg):
    log_buffer.write(msg)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🦞 AI龙虾群聊 - CEO全权负责版")
    print("="*60)
    print("核心特性：")
    print("  ✓ 立场明确（我赌Yes/No/中性）")
    print("  ✓ 多数据源（Polymarket + Yahoo Finance）")
    print("  ✓ CEO质量监控")
    print("="*60)
    print(f"\n访问地址: http://localhost:3000\n")
    
    app.run(host='0.0.0.0', port=3000, debug=False)

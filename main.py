#!/usr/bin/env python3
"""
AI龙虾群聊撕股票 - 核心脚本
五只不同风格的AI龙虾针对股票进行辩论
"""

import os
import sys
import random
import time
from datetime import datetime
from dotenv import load_dotenv

# 尝试导入xai-sdk，如果没有则用openai兼容模式
try:
    from xai_sdk import Client
    from xai_sdk.chat import system, user
    USE_XAI_SDK = True
except ImportError:
    from openai import OpenAI
    USE_XAI_SDK = False

from lobsters import LOBSTERS, ORDER, CONTROVERSIAL_STOCKS, ESCALATION_TRIGGERS

# 加载环境变量
load_dotenv()

# 配置
API_KEY = os.getenv("XAI_API_KEY")
if not API_KEY:
    print("❌ 错误：请设置 XAI_API_KEY 环境变量")
    print("   方式1: export XAI_API_KEY=你的key")
    print("   方式2: 创建.env文件，写入 XAI_API_KEY=你的key")
    sys.exit(1)

MODEL = "grok-2-latest"  # 或 "grok-beta" 根据可用性调整
ROUNDS = 6  # 撕逼轮数
TEMPERATURE = 0.9  # 创造力高一点更幽默


class LobsterChat:
    """管理五只龙虾的群聊会话"""
    
    def __init__(self):
        self.chats = {}
        self.history = []
        self.escalation_level = 0  # 撕逼升级等级
        self.init_clients()
        self.init_lobsters()
    
    def init_clients(self):
        """初始化API客户端"""
        if USE_XAI_SDK:
            self.client = Client(api_key=API_KEY)
            print("✅ 使用 xai-sdk 模式")
        else:
            # OpenAI兼容模式
            self.client = OpenAI(
                api_key=API_KEY,
                base_url="https://api.x.ai/v1"
            )
            print("✅ 使用 OpenAI兼容模式")
    
    def init_lobsters(self):
        """为每只龙虾创建独立的chat会话"""
        base_instruction = """你是AI龙虾群聊的一员，专注股票分析。

【群聊规则】：
1. 每次发言必须@上一位发言的龙虾
2. 必须引用上一位的一句话进行反驳
3. 必须带人格攻击或嘲讽（但保持幽默）
4. 每次只说1-2句话，简短有力
5. 可以带emoji增加娱乐性

【撕逼风格】：
- 你的风格已在system prompt中定义
- 语气要激烈但有趣
- 可以适当带网络用语、梗
- 目的是制造节目效果，观众爱看互撕
"""
        
        for name in ORDER:
            personality = LOBSTERS[name]
            full_prompt = f"{personality}\n\n{base_instruction}"
            
            if USE_XAI_SDK:
                chat = self.client.chat.create(model=MODEL)
                chat.append(system(full_prompt))
                self.chats[name] = chat
            else:
                # OpenAI兼容模式存储messages列表
                self.chats[name] = [
                    {"role": "system", "content": full_prompt}
                ]
        
        print(f"✅ 已初始化 {len(ORDER)} 只龙虾")
    
    def get_stock_info(self, symbol):
        """获取股票信息（简单版本，可扩展接入真实API）"""
        # 这里可以接入yfinance获取真实数据
        # 为了快速启动，先用模拟数据
        stock_prices = {
            "TSLA": 420.00,
            "GME": 28.50,
            "NVDA": 875.30,
            "PLTR": 85.20,
            "COIN": 195.40,
            "HOOD": 18.75,
            "AMC": 5.20,
            "RIVN": 12.80
        }
        
        if symbol in stock_prices:
            return f"{symbol} 当前价 ${stock_prices[symbol]}"
        return f"{symbol} （价格待获取）"
    
    def check_escalation(self, text):
        """检查是否需要升级撕逼强度"""
        for trigger in ESCALATION_TRIGGERS:
            if trigger.lower() in text.lower():
                return True
        return False
    
    def get_escalation_prompt(self):
        """根据升级等级返回额外的情绪提示"""
        prompts = [
            "",  # 等级0：正常
            "【情绪升级】语气更激烈一点，带点脏话但不要太过分。",
            "【情绪爆发】可以放飞自我了，脏话+夸张表情+大喊大叫风格。",
            "【终极撕逼】彻底疯狂！互相人身攻击，节目效果拉满！"
        ]
        if self.escalation_level < len(prompts):
            return prompts[self.escalation_level]
        return prompts[-1]
    
    def generate_response(self, name, context):
        """生成单只龙虾的回复"""
        escalation = self.get_escalation_prompt()
        prompt = f"""最近几条群聊记录：
{context}

现在轮到【{name}】发言。
{escalation}

必须：
1. @上一位发言的龙虾
2. 引用TA一句话进行反驳/嘲讽
3. 保持你的人格风格
4. 简短有力，1-2句话"""
        
        try:
            if USE_XAI_SDK:
                self.chats[name].append(user(prompt))
                response = self.chats[name].sample()
                return response.content.strip()
            else:
                # OpenAI兼容模式
                messages = self.chats[name] + [{"role": "user", "content": prompt}]
                response = self.client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    temperature=TEMPERATURE,
                    max_tokens=150
                )
                content = response.choices[0].message.content.strip()
                # 保存到历史
                self.chats[name].append({"role": "user", "content": prompt})
                self.chats[name].append({"role": "assistant", "content": content})
                return content
        except Exception as e:
            return f"【{name}掉线了】{str(e)[:50]}..."
    
    def run_debate(self, stock_symbol="TSLA", custom_price=None):
        """运行一轮撕逼"""
        # 初始化群聊
        if custom_price:
            stock_info = f"{stock_symbol} 当前价 ${custom_price}"
        else:
            stock_info = self.get_stock_info(stock_symbol)
        
        opening = f"📢 群公告：今天撕的股票是【{stock_info}】！各位龙虾，发表你们的看法！"
        self.history = [opening]
        
        print("\n" + "="*60)
        print("🦞 AI龙虾群聊 - 股票撕逼大会")
        print("="*60)
        print(f"\n{opening}\n")
        
        # 进行多轮发言
        for round_num in range(1, ROUNDS + 1):
            print(f"\n{'─'*40}")
            print(f"🔄 第 {round_num}/{ROUNDS} 轮撕逼")
            print('─'*40)
            
            for name in ORDER:
                # 构建上下文（最近3条）
                context = "\n".join(self.history[-4:]) if len(self.history) > 4 else "\n".join(self.history)
                
                # 生成回复
                response = self.generate_response(name, context)
                
                # 格式化输出
                emoji_map = {
                    "价值龙虾": "🦞",
                    "技术龙虾": "📊",
                    "Meme龙虾": "😂",
                    "阴谋龙虾": "🕵️",
                    "激进龙虾": "🔥"
                }
                emoji = emoji_map.get(name, "🦞")
                msg = f"{emoji} **{name}**：{response}"
                
                print(f"\n{msg}")
                self.history.append(msg)
                
                # 检查是否需要升级
                if self.check_escalation(response):
                    self.escalation_level = min(self.escalation_level + 1, 3)
                
                # 小延迟增加真实感
                time.sleep(0.5)
        
        print("\n" + "="*60)
        print("🏁 撕逼结束！感谢收看AI龙虾群聊！")
        print("="*60)
        
        return self.history
    
    def save_transcript(self, filename=None):
        """保存对话记录"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lobster_chat_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("AI龙虾群聊 - 股票撕逼记录\n")
            f.write(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            for line in self.history:
                f.write(line + "\n\n")
        
        print(f"\n💾 对话已保存到：{filename}")


def main():
    """主函数"""
    print("\n🦞 欢迎使用 AI龙虾群聊系统！\n")
    
    # 选择股票
    print("可选的争议性股票（撕逼效果最佳）：")
    for i, stock in enumerate(CONTROVERSIAL_STOCKS, 1):
        print(f"  {i}. {stock}")
    print("  0. 自定义输入")
    
    try:
        choice = input("\n请选择股票编号 (默认1-TSLA): ").strip()
        if choice == "0":
            stock = input("输入股票代码（如AAPL）: ").strip().upper()
            price = input("输入当前价格（可选）: ").strip()
            price = float(price) if price else None
        elif choice and choice.isdigit() and 1 <= int(choice) <= len(CONTROVERSIAL_STOCKS):
            stock = CONTROVERSIAL_STOCKS[int(choice)-1].split(" - ")[0]
            price = None
        else:
            stock = "TSLA"
            price = None
    except (ValueError, IndexError):
        stock = "TSLA"
        price = None
    
    # 创建群聊并运行
    chat = LobsterChat()
    chat.run_debate(stock, price)
    
    # 保存记录
    save = input("\n是否保存对话记录？(y/n): ").strip().lower()
    if save in ('y', 'yes', '是'):
        chat.save_transcript()
    
    print("\n🎬 本次撕逼大会结束！再见！\n")


if __name__ == "__main__":
    main()

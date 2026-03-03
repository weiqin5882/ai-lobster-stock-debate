#!/usr/bin/env python3
"""
AI龙虾群聊 - 实盘投研版
五只龙虾基于前一日真实股价、新闻、数据互撕
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

from lobsters import LOBSTERS, ORDER, ESCALATION_TRIGGERS

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
    API_KEY = os.getenv("DEEPSEEK_API_KEY")
    BASE_URL = "https://api.deepseek.com"
    MODEL = "deepseek-chat"

if not API_KEY:
    print(f"❌ 错误：请设置 API Key")
    sys.exit(1)

ROUNDS = 6
TEMPERATURE = 0.9
MAX_TOKENS = 150


class LobsterChat:
    """管理五只龙虾的群聊会话"""
    
    def __init__(self):
        self.chats = {}
        self.history = []
        self.escalation_level = 0
        self.message_callback = None
        self.round_callback = None
        self.log_callback = None
        self.market_data = None  # 存储市场数据
        self.init_client()
        self.init_lobsters()
    
    def init_client(self):
        """初始化API客户端"""
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        print(f"✅ 使用 {API_PROVIDER.upper()} API")
    
    def init_lobsters(self):
        """为每只龙虾创建独立的chat会话"""
        # 基础指令 - 强制格式
        base_instruction = """
【强制输出格式 - 必须遵循】：
1. 先引用1个真实数据/事实（股价、财报、指标、新闻等）
2. 再融入你的领域认知（护城河/MACD/FOMO/内幕/IV等）
3. 最后@上一位龙虾，引用其一句话，脏话+表情猛怼
4. 总长度控制在40-60字，1-2句话

【示例】：
"Q3自由现金流暴跌28%，你DCF算个屁价值！@技术龙虾 你那MACD能当现金流用？书呆子🖕"

【禁止】：
- 长篇大论解释概念
- 没有脏话的温和发言
- 不@人不引用
- 不带真实数据空对空"""
        
        for name in ORDER:
            personality = LOBSTERS[name]
            full_prompt = f"{personality}\n\n{base_instruction}"
            
            self.chats[name] = [{"role": "system", "content": full_prompt}]
        
        print(f"✅ 已初始化 {len(ORDER)} 只龙虾")
    
    def set_market_data(self, data):
        """设置市场数据"""
        self.market_data = data
    
    def check_escalation(self, text):
        """检查是否需要升级撕逼强度"""
        for trigger in ESCALATION_TRIGGERS:
            if trigger.lower() in text.lower():
                return True
        return False
    
    def get_escalation_prompt(self):
        """根据升级等级返回额外的情绪提示"""
        prompts = [
            "",
            "【情绪升级】语气更冲，多带1个脏话",
            "【情绪爆发】彻底放飞，连续2个脏话+夸张比喻",
            "【终极撕逼】人身攻击模式，怎么难听怎么骂"
        ]
        return prompts[min(self.escalation_level, 3)]
    
    def get_market_context(self, topic):
        """获取市场数据上下文"""
        context = f"【讨论话题】：{topic}\n\n"
        
        if self.market_data:
            context += "【Polymarket/市场数据】：\n"
            context += f"- 问题：{self.market_data.get('question', 'N/A')}\n"
            context += f"- 当前赔率：{self.market_data.get('outcomes', 'N/A')}\n"
            context += f"- 交易量：${self.market_data.get('volume', 0):,.0f}\n\n"
        
        # 这里可以扩展接入真实股票API
        context += "【要求】：\n"
        context += "1. 引用上述真实数据中的一个数字\n"
        context += "2. 结合你的专业领域（价值/技术/Meme/阴谋/激进）\n"
        context += "3. @上一位龙虾，引用一句话，脏话+表情猛怼\n"
        context += "4. 控制在1-2句话，40-60字\n"
        
        return context
    
    def generate_response(self, name, context, topic):
        """生成单只龙虾的回复"""
        escalation = self.get_escalation_prompt()
        market_context = self.get_market_context(topic)
        
        prompt = f"""{market_context}

【最近群聊记录】：
{context}

【现在轮到{name}发言】
{escalation}

必须做到：
1. 引用真实数据（赔率/交易量/价格等）
2. 展现你的专业认知
3. @上一位发言者，引用其一句原话
4. 脏话+表情嘲讽
5. 1-2句话，40-60字

直接输出你的发言："""
        
        try:
            messages = self.chats[name] + [{"role": "user", "content": prompt}]
            
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            content = response.choices[0].message.content.strip()
            
            # 保存到历史
            self.chats[name].append({"role": "user", "content": prompt})
            self.chats[name].append({"role": "assistant", "content": content})
            
            return content
            
        except Exception as e:
            return f"【{name}掉线】{str(e)[:30]}..."
    
    def run_debate(self, topic="TSLA", rounds=None):
        """运行一轮撕逼"""
        total_rounds = rounds if rounds else ROUNDS
        
        # 初始化群聊
        if self.market_data:
            market_info = f"{self.market_data.get('question', topic)} | {self.market_data.get('outcomes', '')}"
        else:
            market_info = topic
        
        opening = f"📢 群公告：今日实盘【{market_info}】！各投研员发表观点，必须带真实数据！"
        self.history = [opening]
        
        if self.log_callback:
            self.log_callback(f"开始实盘投研: {topic}")
        
        print("\n" + "="*60)
        print("🦞 AI龙虾群聊 - 实盘投研")
        print("="*60)
        print(f"\n{opening}\n")
        
        emoji_map = {
            "价值龙虾": "🦞",
            "技术龙虾": "📊",
            "Meme龙虾": "😂",
            "阴谋龙虾": "🕵️",
            "激进龙虾": "🔥"
        }
        
        for round_num in range(1, total_rounds + 1):
            print(f"\n{'─'*40}")
            print(f"🔄 第 {round_num}/{total_rounds} 轮")
            print('─'*40)
            
            if self.round_callback:
                self.round_callback(round_num, total_rounds)
            
            for name in ORDER:
                context = "\n".join(self.history[-4:]) if len(self.history) > 4 else "\n".join(self.history)
                response = self.generate_response(name, context, topic)
                
                emoji = emoji_map.get(name, "🦞")
                msg = f"{emoji} **{name}**：{response}"
                
                print(f"\n{msg}")
                self.history.append(msg)
                
                if self.message_callback:
                    self.message_callback(name, response, emoji)
                
                if self.check_escalation(response):
                    self.escalation_level = min(self.escalation_level + 1, 3)
                
                time.sleep(0.3)
        
        print("\n" + "="*60)
        print("🏁 投研结束！")
        print("="*60)
        
        if self.log_callback:
            self.log_callback("投研结束！")
        
        return self.history
    
    def save_transcript(self, filename=None):
        """保存对话记录"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lobster_chat_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("AI龙虾群聊 - 实盘投研记录\n")
            f.write(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            for line in self.history:
                f.write(line + "\n\n")
        
        print(f"\n💾 已保存：{filename}")


def main():
    """主函数"""
    print(f"\n🦞 AI龙虾实盘投研系统\n")
    
    topic = input("输入话题/股票（默认TSLA）: ").strip() or "TSLA"
    
    chat = LobsterChat()
    chat.run_debate(topic)
    
    if input("\n保存记录？(y/n): ").strip().lower() in ('y', 'yes'):
        chat.save_transcript()
    
    print("\n🎬 结束！\n")


if __name__ == "__main__":
    main()

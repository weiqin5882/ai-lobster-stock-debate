#!/usr/bin/env python3
"""
AI龙虾群聊 - CEO全权负责版
立场明确 + 多数据源 + 质量监控
"""

import os
import sys
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

from lobsters import LOBSTERS, ORDER, ESCALATION_TRIGGERS
from data_provider import data_provider

# 加载环境变量
load_dotenv()

# API配置
API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("XAI_API_KEY")
BASE_URL = "https://api.deepseek.com" if os.getenv("API_PROVIDER") != "xai" else "https://api.x.ai/v1"
MODEL = "deepseek-chat" if os.getenv("API_PROVIDER") != "xai" else "grok-2-latest"

if not API_KEY:
    print("❌ CEO错误：API Key未配置")
    sys.exit(1)

ROUNDS = 6
TEMPERATURE = 0.85  # 稍降一点，保证立场明确
MAX_TOKENS = 120  # 限制长度，强制短句


class LobsterChat:
    """CEO优化版龙虾群聊"""
    
    def __init__(self):
        self.chats = {}
        self.history = []
        self.escalation_level = 0
        self.stance_stats = {name: [] for name in ORDER}  # 记录每只龙虾的立场
        self.message_callback = None
        self.round_callback = None
        self.log_callback = None
        self.market_data = None
        self.stock_data = None
        self.init_client()
        self.init_lobsters()
    
    def init_client(self):
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        print(f"✅ CEO模式启动 | API: {MODEL}")
    
    def init_lobsters(self):
        """初始化龙虾人格"""
        base_instruction = """
【CEO强制命令 - 违反者开除】：

1. 首句必须亮明立场：
   "我赌Yes，[概率]%" / "我看No" / "中性，[概率]%概率发生"
   ❌ 错误："我认为..." / "可能..." / "也许..."
   ✅ 正确："我赌Yes，60%" / "我看No，被高估"

2. 必须引用真实数据（Polymarket概率/股价/成交量/IV）：
   ❌ 错误："价格很高" / "很多人讨论"
   ✅ 正确："Polymarket概率55%" / "股价$220，PE 45倍"

3. 必须融入领域认知：
   价值：DCF/护城河/现金流/ROIC
   技术：MACD/均线/VWAP/成交量
   Meme：FOMO/热搜/情绪周期/反身性
   阴谋：暗池/内幕/机构对冲/历史操控
   激进：IV/Gamma/Straddle/杠杆回报

4. 必须@上一位并引用原话+脏话+表情

5. 总长度≤60字，1-2句话

【CEO检查清单】：
□ 首句有"我赌/我看/中性"
□ 有具体数字（概率/价格/成交量）
□ 有专业术语（DCF/MACD/FOMO等）
□ @了人并引用了话
□ 有脏话和表情"""
        
        for name in ORDER:
            full_prompt = f"{LOBSTERS[name]}\n\n{based_instruction}"
            self.chats[name] = [{"role": "system", "content": full_prompt}]
        
        print(f"✅ 五只龙虾已激活，立场明确模式")
    
    def set_market_data(self, market_data, stock_data=None):
        self.market_data = market_data
        self.stock_data = stock_data
    
    def check_stance_valid(self, text: str) -> tuple:
        """CEO质检：检查立场是否明确"""
        # 检查首句立场
        stance_patterns = [
            r'我赌\s*(Yes|No|YES|NO|yes|no)',
            r'我看\s*(Yes|No|YES|NO|yes|no)',
            r'中性',
            r'(\d+)%\s*(概率|概率|chance)'
        ]
        
        has_stance = any(re.search(p, text) for p in stance_patterns)
        
        # 检查是否有数字
        has_number = bool(re.search(r'\d+\.?\d*%?|\$\d+', text))
        
        # 检查是否@人
        has_mention = '@' in text
        
        # 检查长度
        length_ok = len(text) <= 80
        
        return has_stance, has_number, has_mention, length_ok
    
    def generate_response(self, name: str, context: str, topic: str) -> str:
        """生成回复（CEO质量把控）"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 构建Prompt
                market_info = self._build_market_info()
                
                prompt = f"""【CEO监督下的实盘投研】

{market_info}

【话题】{topic}

【最近发言】
{context}

【轮到{name}发言】

CEO命令：首句亮立场+真实数据+专业认知+@怼人+脏话表情

{name}发言："""
                
                messages = self.chats[name] + [{"role": "user", "content": prompt}]
                
                response = self.client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS
                )
                
                content = response.choices[0].message.content.strip()
                
                # CEO质检
                has_stance, has_number, has_mention, length_ok = self.check_stance_valid(content)
                
                if all([has_stance, has_number, has_mention, length_ok]):
                    # 通过质检
                    self.chats[name].append({"role": "user", "content": prompt})
                    self.chats[name].append({"role": "assistant", "content": content})
                    
                    # 记录立场
                    self._record_stance(name, content)
                    
                    return content
                else:
                    # 未通过，记录问题
                    issues = []
                    if not has_stance: issues.append("缺立场")
                    if not has_number: issues.append("缺数据")
                    if not has_mention: issues.append("缺@人")
                    if not length_ok: issues.append("太长")
                    
                    if self.log_callback:
                        self.log_callback(f"⚠️ {name}未通过CEO质检: {', '.join(issues)}，重试({attempt+1}/3)")
                    
                    if attempt == max_retries - 1:
                        # 最后一次仍失败，强制修正
                        return self._force_correct(content, name)
                        
            except Exception as e:
                if attempt == max_retries - 1:
                    return f"【{name}掉线】{str(e)[:20]}..."
        
        return f"【{name}发言失败】"
    
    def _build_market_info(self) -> str:
        """构建市场信息"""
        lines = ["【CEO提供的市场数据】"]
        
        if self.market_data:
            lines.append(f"Polymarket: {self.market_data.get('question', '')}")
            outcomes = ' / '.join([f"{o['label']}{o['probability']:.0f}%" for o in self.market_data.get('outcomes', [])])
            lines.append(f"赔率: {outcomes}")
            lines.append(f"交易量: ${self.market_data.get('volume', 0):,.0f}")
        
        if self.stock_data and 'error' not in self.stock_data:
            lines.append(f"股价: ${self.stock_data['price']:.2f} ({self.stock_data['change_pct']:+.2f}%)")
            lines.append(f"量能: {self.stock_data['volume_ratio']:.1f}倍")
            if self.stock_data.get('pe') and self.stock_data['pe'] != 'N/A':
                lines.append(f"PE: {self.stock_data['pe']:.1f}")
        
        return '\n'.join(lines)
    
    def _record_stance(self, name: str, content: str):
        """记录龙虾立场"""
        # 提取Yes/No/中性
        if re.search(r'我赌\s*Yes|我看\s*Yes', content, re.IGNORECASE):
            self.stance_stats[name].append('Yes')
        elif re.search(r'我赌\s*No|我看\s*No', content, re.IGNORECASE):
            self.stance_stats[name].append('No')
        else:
            self.stance_stats[name].append('Neutral')
    
    def _force_correct(self, content: str, name: str) -> str:
        """强制修正不符合规范的输出"""
        # 简单修正：添加立场前缀
        if not re.search(r'我赌|我看|中性', content):
            content = f"我看No，{content}"
        
        if '@' not in content:
            content += " @其他人 傻X"
        
        if len(content) > 80:
            content = content[:77] + "..."
        
        return content
    
    def run_debate(self, topic: str = "TSLA", rounds: int = None) -> list:
        """运行投研对决"""
        total_rounds = rounds or ROUNDS
        
        # 开场
        market_info = ""
        if self.market_data:
            market_info = f" | {self.market_data.get('question', '')}"
        
        opening = f"📢 CEO开盘：今日实盘【{topic}{market_info}】！五只龙虾亮明立场，必须带真实数据！"
        self.history = [opening]
        
        if self.log_callback:
            self.log_callback(f"CEO启动投研: {topic}")
        
        print("\n" + "="*60)
        print("🦞 AI龙虾群聊 - CEO全权负责版")
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
            print(f"\n{'─'*50}")
            print(f"🔄 CEO监督 - 第 {round_num}/{total_rounds} 轮")
            print('─'*50)
            
            if self.round_callback:
                self.round_callback(round_num, total_rounds)
            
            for name in ORDER:
                context = "\n".join(self.history[-3:]) if len(self.history) > 3 else "\n".join(self.history)
                response = self.generate_response(name, context, topic)
                
                emoji = emoji_map.get(name, "🦞")
                msg = f"{emoji} **{name}**：{response}"
                
                print(f"\n{msg}")
                self.history.append(msg)
                
                if self.message_callback:
                    self.message_callback(name, response, emoji)
                
                # 检查升级
                if any(t in response.lower() for t in ESCALATION_TRIGGERS):
                    self.escalation_level = min(self.escalation_level + 1, 3)
                
                time.sleep(0.5)
        
        # 总结立场分布
        print("\n" + "="*60)
        print("📊 CEO立场统计")
        print("="*60)
        for name, stances in self.stance_stats.items():
            yes_count = stances.count('Yes')
            no_count = stances.count('No')
            neutral_count = stances.count('Neutral')
            print(f"{name}: Yes({yes_count}) No({no_count}) 中性({neutral_count})")
        
        print("\n🏁 CEO宣布：投研结束！")
        print("="*60)
        
        if self.log_callback:
            self.log_callback("投研结束")
        
        return self.history


def main():
    print("\n🦞 AI龙虾 - CEO全权负责版\n")
    
    topic = input("输入话题: ").strip() or "TSLA"
    
    chat = LobsterChat()
    chat.run_debate(topic)
    
    if input("\n保存? (y/n): ").lower() in ('y', 'yes'):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"lobster_ceo_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write("\n\n".join(chat.history))
        print(f"✅ CEO已保存")
    
    print("\n🎬 CEO结束\n")


if __name__ == "__main__":
    main()

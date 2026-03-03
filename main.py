#!/usr/bin/env python3
"""
AI龙虾群聊 - 核心脚本
五只不同风格的AI龙虾针对任何话题进行激烈辩论
"""

import os
import sys
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

from lobsters import LOBSTERS, ORDER, HOT_TOPICS, ESCALATION_TRIGGERS

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
        # Web回调函数
        self.message_callback = None
        self.round_callback = None
        self.log_callback = None
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
        base_instruction = """你是AI龙虾群聊的一员，专业辩手。

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
- 针对话题发表你的观点，用你的风格猛烈输出
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
    
    def run_debate(self, topic="AI人工智能", rounds=None):
        """运行一轮撕逼
        
        Args:
            topic: 辩论话题，可以是任何主题
            rounds: 轮数，默认6轮
        """
        # 使用传入的轮数或默认轮数
        total_rounds = rounds if rounds else ROUNDS
        
        # 初始化群聊
        opening = f"📢 群公告：今天撕的话题是【{topic}】！各位龙虾，发表你们的看法！"
        self.history = [opening]
        
        # Web回调
        if self.log_callback:
            self.log_callback(f"开始撕逼话题: {topic}")
        
        print("\n" + "="*60)
        print("🦞 AI龙虾群聊 - 话题撕逼大会")
        print("="*60)
        print(f"\n{opening}\n")
        
        emoji_map = {
            "价值龙虾": "🦞",
            "技术龙虾": "📊",
            "Meme龙虾": "😂",
            "阴谋龙虾": "🕵️",
            "激进龙虾": "🔥"
        }
        
        # 进行多轮发言
        for round_num in range(1, total_rounds + 1):
            print(f"\n{'─'*40}")
            print(f"🔄 第 {round_num}/{total_rounds} 轮撕逼")
            print('─'*40)
            
            # 轮次回调
            if self.round_callback:
                self.round_callback(round_num, total_rounds)
            
            for name in ORDER:
                # 构建上下文（最近3条）
                context = "\n".join(self.history[-4:]) if len(self.history) > 4 else "\n".join(self.history)
                
                # 生成回复
                response = self.generate_response(name, context)
                
                # 格式化输出
                emoji = emoji_map.get(name, "🦞")
                msg = f"{emoji} **{name}**：{response}"
                
                print(f"\n{msg}")
                self.history.append(msg)
                
                # 消息回调（用于Web实时显示）
                if self.message_callback:
                    self.message_callback(name, response, emoji)
                
                # 检查是否需要升级
                if self.check_escalation(response):
                    self.escalation_level = min(self.escalation_level + 1, 3)
                
                # 小延迟增加真实感
                time.sleep(0.3)
        
        print("\n" + "="*60)
        print("🏁 撕逼结束！感谢收看AI龙虾群聊！")
        print("="*60)
        
        if self.log_callback:
            self.log_callback("撕逼结束！")
        
        return self.history
    
    def save_transcript(self, filename=None):
        """保存对话记录"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lobster_chat_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("AI龙虾群聊 - 话题撕逼记录\n")
            f.write(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            for line in self.history:
                f.write(line + "\n\n")
        
        print(f"\n💾 对话已保存到：{filename}")


def main():
    """主函数"""
    print("\n🦞 欢迎使用 AI龙虾群聊系统！\n")
    
    # 选择话题
    print("可选的热门话题（撕逼效果最佳）：")
    for i, topic in enumerate(HOT_TOPICS, 1):
        print(f"  {i}. {topic}")
    print("  0. 自定义输入")
    
    try:
        choice = input("\n请选择话题编号 (默认1): ").strip()
        if choice == "0":
            topic = input("输入自定义话题: ").strip()
        elif choice and choice.isdigit() and 1 <= int(choice) <= len(HOT_TOPICS):
            topic = HOT_TOPICS[int(choice)-1].split(" - ")[0]
        else:
            topic = HOT_TOPICS[0].split(" - ")[0]
    except (ValueError, IndexError):
        topic = HOT_TOPICS[0].split(" - ")[0]
    
    # 创建群聊并运行
    chat = LobsterChat()
    chat.run_debate(topic)
    
    # 保存记录
    save = input("\n是否保存对话记录？(y/n): ").strip().lower()
    if save in ('y', 'yes', '是'):
        chat.save_transcript()
    
    print("\n🎬 本次撕逼大会结束！再见！\n")


if __name__ == "__main__":
    main()

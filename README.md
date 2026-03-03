# 🦞 AI龙虾群聊 - 话题撕逼大会

五只不同风格的AI龙虾（价值理性、数据驱动、情绪热度、阴谋怀疑、激进冒险）在一个群里针对任何热门话题展开激烈辩论，制造娱乐性极强的内容。

![Web UI Preview](https://img.shields.io/badge/Web-UI-ff4757?style=for-the-badge)
![Port 3000](https://img.shields.io/badge/Port-3000-2ed573?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge)
![Deepseek](https://img.shields.io/badge/API-Deepseek-4f46e5?style=for-the-badge)

## 🎯 核心看点

- **AI互撕/互怼** - 冲突制造笑点和高能时刻
- **不同人格碰撞** - 价值派 vs 技术派 vs Meme派 vs 阴谋论派 vs 激进派
- **任何话题都能撕** - 股票、科技、社会热点、lifestyle
- **娱乐性 > 专业性** - 观众看热闹为主
- **短视频剪辑潜力极高** - 金句、名场面频出
- **低成本可复制** - 换话题继续产出

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API Key

**Deepseek API（推荐，性价比高）：**

1. 前往 [Deepseek开放平台](https://platform.deepseek.com/) 注册并创建API Key
2. 配置环境变量：

```bash
# 方式1 - 环境变量（临时）
export DEEPSEEK_API_KEY="你的Deepseek_API_Key"
export API_PROVIDER="deepseek"

# 方式2 - .env文件（推荐）
cp .env.example .env
# 编辑.env文件，填入你的API Key
```

**可选：xAI (Grok) API**

```bash
export XAI_API_KEY="你的xAI_API_Key"
export API_PROVIDER="xai"
```

### 3. 运行方式（二选一）

#### 🌐 方式A - Web界面（推荐）
```bash
python app.py
```
然后访问：**http://localhost:3000**

#### 💻 方式B - 命令行
```bash
python main.py
```

## 🌐 Web界面功能

- ✅ **可视化聊天** - 五只龙虾以不同颜色气泡显示
- ✅ **话题选择** - 15个热门话题 + 自定义输入
- ✅ **自定义话题** - 输入任何想撕的话题
- ✅ **轮数控制** - 可设置1-10轮撕逼
- ✅ **实时状态** - 显示当前轮次和进度
- ✅ **日志面板** - 页面底部显示系统日志和报错信息
- ✅ **响应式设计** - 支持手机和桌面

### 热门话题池

| 类型 | 话题 |
|------|------|
| 💰 投资 | TSLA股票、比特币、房地产 |
| 🤖 科技 | AI人工智能、元宇宙、电动车 |
| 💼 职场 | 996工作制、躺平文化、内卷 |
| 🎭 生活 | 追星、游戏、素食主义 |
| 自定义 | 输入任何话题！ |

## 🤖 API配置

### Deepseek（默认，推荐）

- **价格**: 输入¥2/百万token，输出¥8/百万token
- **模型**: `deepseek-chat` (V3) 或 `deepseek-reasoner` (R1)
- **特点**: 中文效果好，价格便宜，响应快
- **注册**: https://platform.deepseek.com/

```bash
export DEEPSEEK_API_KEY="sk-..."
export API_PROVIDER="deepseek"
```

### xAI (Grok)

- **价格**: 按需付费
- **模型**: `grok-2-latest`
- **特点**: 英文效果好，实时信息
- **注册**: https://console.x.ai

```bash
export XAI_API_KEY="..."
export API_PROVIDER="xai"
```

## 🦞 五只龙虾人格

| 龙虾 | emoji | 风格 | 核心武器 |
|------|-------|------|----------|
| 价值龙虾 | 🦞 | 长期价值 | 本质、根基、长期主义 |
| 技术龙虾 | 📊 | 数据驱动 | 逻辑、分析、客观指标 |
| Meme龙虾 | 😂 | 情绪热度 | 流量、热点、FOMO |
| 阴谋龙虾 | 🕵️ | 阴谋怀疑 | 套路、内幕、假象 |
| 激进龙虾 | 🔥 | 激进冒险 | 梭哈、All in、暴富 |

## 📁 文件结构

```
lobster-ai/
├── app.py              # 🌐 Flask Web服务器 (端口3000)
├── main.py             # 💻 命令行版本
├── lobsters.py         # 五只龙虾人格定义 + 话题池
├── requirements.txt    # 依赖列表
├── .env.example        # 环境变量示例 (Deepseek + xAI)
├── .gitignore          # Git忽略规则
├── templates/
│   └── index.html      # Web前端页面
└── README.md           # 本文件
```

## 💰 成本估算

使用 **Deepseek API**：
- 每次撕逼（6轮 × 5只龙虾 = 30次API调用）
- 预估消耗：约 3000-5000 tokens
- 成本：约 ¥0.02-0.05/次

**超级便宜！放心撕！**

## 🎬 使用场景

1. **内容创作** - 生成有趣的AI对话，剪辑成短视频
2. **直播** - 实时生成辩论内容，配TTS语音直播
3. **测试** - 测试不同AI人格的prompt工程效果
4. **娱乐** - 看AI互相撕逼，纯粹好玩
5. **自媒体** - B站/YouTube视频素材生成
6. **话题探索** - 看AI从不同角度分析同一话题

## 🔧 进阶配置

### 添加新话题
在 `lobsters.py` 的 `HOT_TOPICS` 列表中添加

### 修改龙虾人格
编辑 `lobsters.py` 中的 `LOBSTERS` 字典

### 切换API
修改 `.env` 文件中的 `API_PROVIDER`：
```bash
API_PROVIDER=deepseek  # 或 xai
```

### 添加语音输出 (Web版)
在 `app.py` 中集成gTTS，给每只龙虾添加语音播报

## 📝 示例输出

```
🦞 AI龙虾群聊 - 话题撕逼大会

📢 群公告：今天撕的话题是【AI人工智能会取代人类工作吗？】！各位龙虾，发表你们的看法！

───────────────
🔄 第 1/6 轮撕逼
───────────────

🦞 **价值龙虾**：AI就是泡沫！人类的核心价值是创造力和情感，你们这帮技术宅在给算法数钱呢？

📊 **技术龙虾**：@价值龙虾 老古董闭嘴！数据不会骗人，AI效率提升300%，你继续抱着人类优越性哭去吧！

😂 **Meme龙虾**：哈哈哈你们好土鳖😂 AI就是新的互联网泡沫！谁抓到风口谁暴富，情绪王道！

🕵️ **阴谋龙虾**：@Meme龙虾 你就是被资本洗脑最惨的那只韭菜！AI威胁论就是科技公司的营销剧本！

🔥 **激进龙虾**：@价值龙虾 胆小如鼠的废物！老子已经All in AI概念股，你们还在讨论？loser！
```

## 🎥 直播扩展思路

1. **TTS语音** - 用gTTS或pyttsx3给每只龙虾配音
2. **视觉形象** - OBS捕获Web界面 + 龙虾头像动画
3. **弹幕互动** - 让观众投票决定下一话题
4. **实时话题** - 监听Twitter/微博热搜自动抓取话题
5. **推流** - OBS推流到B站/YouTube/Twitch

## ⚠️ 注意事项

1. 需要 Deepseek 或 xAI 的 API Key
   - Deepseek: https://platform.deepseek.com/
   - xAI: https://console.x.ai
2. API调用会产生费用，Deepseek价格很便宜
3. 生成的内容仅供娱乐，**不构成任何建议**
4. 撕逼内容可能包含讽刺和夸张表达

## 📄 License

MIT License - 自由使用和修改

---

🦞 **让AI撕起来！** 访问 http://localhost:3000 开始体验

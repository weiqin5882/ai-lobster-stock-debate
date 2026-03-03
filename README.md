# 🦞 AI龙虾群聊 - 股票撕逼大会

五只不同风格的AI龙虾（价值投资、技术分析、Meme投机、阴谋论、激进杠杆）在一个群里针对热门股票展开激烈辩论，制造娱乐性极强的内容。

![Web UI Preview](https://img.shields.io/badge/Web-UI-ff4757?style=for-the-badge)
![Port 3000](https://img.shields.io/badge/Port-3000-2ed573?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge)

## 🎯 核心看点

- **AI互撕/互怼** - 冲突制造笑点和高能时刻
- **不同人格碰撞** - 价值派 vs 技术派 vs Meme派 vs 阴谋论派 vs 激进派
- **实时热点股票** + 意外神预测/翻车
- **娱乐性 > 专业性** - 观众看热闹为主
- **短视频剪辑潜力极高** - 金句、名场面频出
- **低成本可复制** - 换股票继续产出

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API Key

**方式1 - 环境变量（临时）：**
```bash
export XAI_API_KEY="你的xAI_API_Key"
```

**方式2 - .env文件（推荐）：**
```bash
cp .env.example .env
# 编辑.env文件，填入你的API Key
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

![Web UI](https://via.placeholder.com/800x400/1a1a2e/ffffff?text=Web+UI+Preview)

- ✅ **可视化聊天** - 五只龙虾以不同颜色气泡显示
- ✅ **股票选择** - 下拉菜单选择争议股票
- ✅ **轮数控制** - 可设置1-10轮撕逼
- ✅ **实时状态** - 显示当前轮次和进度
- ✅ **日志面板** - 页面底部显示系统日志和报错信息
- ✅ **响应式设计** - 支持手机和桌面

## 🦞 五只龙虾人格

| 龙虾 | emoji | 风格 | 核心武器 |
|------|-------|------|----------|
| 价值龙虾 | 🦞 | 保守理性 | PE、ROE、基本面 |
| 技术龙虾 | 📊 | 图表狂热 | MACD、K线、趋势 |
| Meme龙虾 | 😂 | 娱乐投机 | 推特热点、表情包 |
| 阴谋龙虾 | 🕵️ | 怀疑论 | 操控论、内幕说 |
| 激进龙虾 | 🔥 | 杠杆狂魔 | 0DTE、All in |

## 📁 文件结构

```
lobster-ai/
├── app.py              # 🌐 Flask Web服务器 (端口3000)
├── main.py             # 💻 命令行版本
├── lobsters.py         # 五只龙虾人格定义
├── requirements.txt    # 依赖列表
├── .env.example        # 环境变量示例
├── .gitignore          # Git忽略规则
├── templates/
│   └── index.html      # Web前端页面
└── README.md           # 本文件
```

## 🎬 使用场景

1. **内容创作** - 生成有趣的AI对话，剪辑成短视频
2. **直播** - 实时生成辩论内容，配TTS语音直播
3. **测试** - 测试不同AI人格的prompt工程效果
4. **娱乐** - 看AI互相撕逼，纯粹好玩
5. **自媒体** - B站/YouTube视频素材生成

## 🔧 进阶配置

### 修改撕逼轮数
- Web版：页面直接选择
- 命令行版：编辑 `main.py` 中的 `ROUNDS` 变量

### 添加新股票
在 `lobsters.py` 的 `CONTROVERSIAL_STOCKS` 列表中添加

### 接入真实股价
取消 `main.py` 中的 `get_stock_info` 方法的注释，接入yfinance获取实时数据

### 添加语音输出 (Web版)
在 `app.py` 中集成gTTS，给每只龙虾添加语音播报

## 📝 示例输出

```
🦞 AI龙虾群聊 - 股票撕逼大会

📢 群公告：今天撕的股票是【TSLA 当前价 $420】！各位龙虾，发表你们的看法！

───────────────
🔄 第 1/6 轮撕逼
───────────────

🦞 **价值龙虾**：TSLA这PE都破百了，基本面跟筛子一样漏风！你们这些赌狗在给马斯克数钱呢？

📊 **技术龙虾**：@价值龙虾 老古董闭嘴！MACD金叉+放量突破，趋势已经反转了！你继续抱着财报哭去吧！

😂 **Meme龙虾**：哈哈哈你们好土鳖😂 TSLA就是马斯克的表情包发射器！他发个💩都能拉20%！

🕵️ **阴谋龙虾**：@Meme龙虾 你就是被操控最惨的那只韭菜！FSD永远明年量产，全是剧本！

🔥 **激进龙虾**：@价值龙虾 胆小如鼠的废物！老子昨天all in 0DTE call，今天已经吃香喝辣！
```

## 🎥 直播扩展思路

1. **TTS语音** - 用gTTS或pyttsx3给每只龙虾配音
2. **视觉形象** - OBS捕获Web界面 + 龙虾头像动画
3. **实时数据** - 接入股票API获取实时价格
4. **弹幕互动** - 让观众投票决定下一支股票
5. **推流** - OBS推流到B站/YouTube/Twitch

## ⚠️ 注意事项

1. 需要 xAI (Grok) 的 API Key - [获取地址](https://console.x.ai)
2. API调用会产生费用，请留意用量
3. 生成的内容仅供娱乐，**不构成投资建议**
4. 撕逼内容可能包含讽刺和夸张表达

## 📄 License

MIT License - 自由使用和修改

---

🦞 **让AI撕起来！** 访问 http://localhost:3000 开始体验

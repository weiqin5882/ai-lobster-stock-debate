#!/usr/bin/env python3
"""
Polymarket 数据获取模块
获取每日热门市场数据
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class PolymarketClient:
    """Polymarket API 客户端"""
    
    BASE_URL = "https://gamma-api.polymarket.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_hot_markets(self, limit: int = 20) -> List[Dict]:
        """
        获取热门市场（按交易量和参与度排序）
        
        Returns:
            List[Dict]: 热门市场列表，每个市场包含：
                - question: 市场问题
                - slug: 市场标识
                - volume: 交易量
                - liquidity: 流动性
                - outcomes: 结果选项及概率
                - endDate: 结束日期
                - description: 描述
        """
        try:
            # 获取活跃市场，按交易量排序
            params = {
                'active': 'true',
                'closed': 'false',
                'archived': 'false',
                'order': 'volume',  # 按交易量排序
                'ascending': 'false',
                'limit': limit * 2,  # 多获取一些，过滤后保留20个
                'offset': 0
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/markets",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            markets = response.json()
            
            # 处理数据
            hot_markets = []
            for market in markets[:limit]:
                processed = self._process_market(market)
                if processed:
                    hot_markets.append(processed)
            
            return hot_markets[:limit]
            
        except Exception as e:
            print(f"❌ 获取Polymarket数据失败: {e}")
            return []
    
    def _process_market(self, market: Dict) -> Optional[Dict]:
        """处理单个市场数据"""
        try:
            question = market.get('question', '')
            if not question:
                return None
            
            # 获取结果和概率
            outcomes = []
            outcome_prices = market.get('outcomePrices', [])
            outcome_labels = market.get('outcomes', [])
            
            if outcome_prices and outcome_labels:
                for i, (label, price) in enumerate(zip(outcome_labels, outcome_prices)):
                    try:
                        # price是字符串形式的价格，需要转换
                        prob = float(price) * 100 if isinstance(price, (int, float, str)) else 50
                        outcomes.append({
                            'label': label,
                            'probability': round(prob, 1)
                        })
                    except:
                        outcomes.append({
                            'label': label,
                            'probability': 50
                        })
            
            # 获取交易量
            volume = market.get('volume', 0)
            if isinstance(volume, str):
                try:
                    volume = float(volume)
                except:
                    volume = 0
            
            # 获取流动性
            liquidity = market.get('liquidity', 0)
            if isinstance(liquidity, str):
                try:
                    liquidity = float(liquidity)
                except:
                    liquidity = 0
            
            return {
                'id': market.get('id', ''),
                'slug': market.get('slug', ''),
                'question': question,
                'description': market.get('description', '')[:200] + '...' if market.get('description') else '',
                'volume': round(volume, 2),
                'liquidity': round(liquidity, 2),
                'outcomes': outcomes,
                'end_date': market.get('endDate', ''),
                'created_at': market.get('createdAt', ''),
                'category': market.get('category', 'General'),
                'icon': market.get('icon', ''),
                'url': f"https://polymarket.com/event/{market.get('slug', '')}"
            }
            
        except Exception as e:
            print(f"处理市场数据失败: {e}")
            return None
    
    def format_market_for_lobsters(self, market: Dict) -> str:
        """将市场格式化为适合龙虾讨论的文本"""
        question = market['question']
        outcomes_text = ' / '.join([
            f"{o['label']}({o['probability']}%)")
            for o in market['outcomes']
        ])
        
        return f"""
【Polymarket预测市场】
问题: {question}
当前赔率: {outcomes_text}
交易量: ${market['volume']:,.0f}
流动性: ${market['liquidity']:,.0f}
截止日期: {market['end_date'][:10] if market['end_date'] else 'TBD'}
"""
    
    def save_hot_markets(self, markets: List[Dict], filepath: str = 'data/hot_markets.json'):
        """保存热门市场到文件"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        data = {
            'updated_at': datetime.now().isoformat(),
            'count': len(markets),
            'markets': markets
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存 {len(markets)} 个热门市场到 {filepath}")
    
    def load_hot_markets(self, filepath: str = 'data/hot_markets.json') -> List[Dict]:
        """从文件加载热门市场"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查数据是否过期（超过24小时）
            updated_at = datetime.fromisoformat(data.get('updated_at', '2000-01-01'))
            if datetime.now() - updated_at > timedelta(hours=24):
                print("⚠️ 市场数据已过期，需要更新")
            
            return data.get('markets', [])
            
        except FileNotFoundError:
            print(f"❌ 市场数据文件不存在: {filepath}")
            return []
        except Exception as e:
            print(f"❌ 加载市场数据失败: {e}")
            return []


def update_hot_markets():
    """更新热门市场数据（用于定时任务）"""
    print(f"\n🔄 更新Polymarket热门市场数据...")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    client = PolymarketClient()
    markets = client.get_hot_markets(limit=20)
    
    if markets:
        client.save_hot_markets(markets)
        
        print("\n📊 今日热门市场Top 5:")
        for i, m in enumerate(markets[:5], 1):
            outcomes = ' / '.join([f"{o['label']}({o['probability']:.0f}%)" for o in m['outcomes'][:2]])
            print(f"  {i}. {m['question'][:50]}... | {outcomes}")
        
        return True
    else:
        print("❌ 未能获取市场数据")
        return False


if __name__ == '__main__':
    # 测试运行
    update_hot_markets()

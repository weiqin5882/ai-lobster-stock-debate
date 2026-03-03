#!/usr/bin/env python3
"""
数据获取模块 - CEO全权负责版
整合多数据源：Polymarket + Yahoo Finance + Twitter/X
"""

import os
import json
import requests
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class DataProvider:
    """统一数据提供者"""
    
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 300  # 5分钟缓存
    
    def get_polymarket_hot(self, limit: int = 20) -> List[Dict]:
        """获取Polymarket热门市场"""
        try:
            url = "https://gamma-api.polymarket.com/markets"
            params = {
                'active': 'true',
                'closed': 'false',
                'archived': 'false',
                'order': 'volume',
                'ascending': 'false',
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            markets = []
            for m in response.json()[:limit]:
                outcomes = []
                prices = m.get('outcomePrices', [])
                labels = m.get('outcomes', [])
                for label, price in zip(labels, prices):
                    try:
                        prob = float(price) * 100
                        outcomes.append({'label': label, 'probability': round(prob, 1)})
                    except:
                        outcomes.append({'label': label, 'probability': 50})
                
                markets.append({
                    'id': m.get('id'),
                    'question': m.get('question'),
                    'outcomes': outcomes,
                    'volume': float(m.get('volume', 0)),
                    'liquidity': float(m.get('liquidity', 0)),
                    'end_date': m.get('endDate', '')[:10] if m.get('endDate') else 'TBD',
                    'url': f"https://polymarket.com/event/{m.get('slug', '')}"
                })
            
            return markets
            
        except Exception as e:
            print(f"❌ Polymarket数据获取失败: {e}")
            return []
    
    def get_stock_data(self, symbol: str) -> Dict:
        """获取股票数据（Yahoo Finance）"""
        cache_key = f"stock_{symbol}"
        
        # 检查缓存
        if cache_key in self.cache:
            if datetime.now() - self.cache_time[cache_key] < timedelta(seconds=self.cache_duration):
                return self.cache[cache_key]
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            info = ticker.info
            
            if hist.empty:
                return {'error': '无数据'}
            
            # 计算技术指标
            current_price = hist['Close'][-1]
            prev_close = hist['Close'][-2] if len(hist) > 1 else current_price
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            # 均线
            ma5 = hist['Close'].rolling(5).mean().iloc[-1] if len(hist) >= 5 else current_price
            ma20 = hist['Close'].rolling(20).mean().iloc[-1] if len(hist) >= 20 else current_price
            
            # 成交量
            volume = hist['Volume'][-1]
            avg_volume = hist['Volume'].mean()
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1
            
            data = {
                'symbol': symbol,
                'price': round(current_price, 2),
                'change_pct': round(change_pct, 2),
                'volume': int(volume),
                'volume_ratio': round(volume_ratio, 2),
                'ma5': round(ma5, 2),
                'ma20': round(ma20, 2),
                'pe': info.get('trailingPE', info.get('forwardPE', 'N/A')),
                'market_cap': info.get('marketCap', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            # 缓存
            self.cache[cache_key] = data
            self.cache_time[cache_key] = datetime.now()
            
            return data
            
        except Exception as e:
            print(f"❌ 股票数据获取失败 {symbol}: {e}")
            return {'error': str(e), 'symbol': symbol}
    
    def get_options_data(self, symbol: str) -> Dict:
        """获取期权数据（IV、Call/Put比等）"""
        try:
            ticker = yf.Ticker(symbol)
            
            # 获取期权链（最近到期日）
            expirations = ticker.options
            if not expirations:
                return {'error': '无期权数据'}
            
            # 取最近到期日
            nearest_exp = expirations[0]
            opt_chain = ticker.option_chain(nearest_exp)
            
            calls = opt_chain.calls
            puts = opt_chain.puts
            
            # 计算IV中位数
            call_iv = calls['impliedVolatility'].median() * 100 if not calls.empty else 0
            put_iv = puts['impliedVolatility'].median() * 100 if not puts.empty else 0
            avg_iv = (call_iv + put_iv) / 2
            
            # Call/Put成交量比
            call_volume = calls['volume'].sum() if not calls.empty else 0
            put_volume = puts['volume'].sum() if not puts.empty else 0
            cp_ratio = call_volume / put_volume if put_volume > 0 else 1
            
            return {
                'symbol': symbol,
                'expiration': nearest_exp,
                'call_iv': round(call_iv, 1),
                'put_iv': round(put_iv, 1),
                'avg_iv': round(avg_iv, 1),
                'cp_ratio': round(cp_ratio, 2),
                'call_volume': int(call_volume),
                'put_volume': int(put_volume)
            }
            
        except Exception as e:
            print(f"❌ 期权数据获取失败 {symbol}: {e}")
            return {'error': str(e)}
    
    def format_for_lobster(self, market_data: Dict, stock_data: Optional[Dict] = None) -> str:
        """格式化为龙虾可用的文本"""
        lines = []
        
        # Polymarket数据
        if 'question' in market_data:
            lines.append(f"【Polymarket】{market_data['question']}")
            outcomes_str = ' / '.join([f"{o['label']}{o['probability']:.0f}%" for o in market_data.get('outcomes', [])])
            lines.append(f"当前赔率：{outcomes_str}")
            lines.append(f"交易量：${market_data.get('volume', 0):,.0f}")
        
        # 股票数据
        if stock_data and 'error' not in stock_data:
            lines.append(f"【股价】${stock_data['price']:.2f} ({stock_data['change_pct']:+.2f}%)")
            lines.append(f"【量能】{stock_data['volume_ratio']:.1f}倍均量")
            if stock_data.get('pe') and stock_data['pe'] != 'N/A':
                lines.append(f"【估值】PE {stock_data['pe']:.1f}")
        
        return '\n'.join(lines)


# 全局数据提供者实例
data_provider = DataProvider()


def save_markets_data(markets: List[Dict], filepath: str = 'data/hot_markets.json'):
    """保存市场数据"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({
            'updated_at': datetime.now().isoformat(),
            'count': len(markets),
            'markets': markets
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存 {len(markets)} 个市场到 {filepath}")


def update_all_data():
    """更新所有数据（定时任务用）"""
    print(f"\n{'='*60}")
    print(f"🔄 CEO数据更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    provider = DataProvider()
    
    # 1. 更新Polymarket
    print("📊 获取Polymarket热门市场...")
    markets = provider.get_polymarket_hot(20)
    if markets:
        save_markets_data(markets)
        print(f"   ✓ 获取 {len(markets)} 个市场")
    
    # 2. 更新热门股票（示例）
    print("\n📈 获取股票数据...")
    for symbol in ['TSLA', 'NVDA', 'AAPL']:
        data = provider.get_stock_data(symbol)
        if 'error' not in data:
            print(f"   ✓ {symbol}: ${data['price']:.2f} ({data['change_pct']:+.2f}%)")
    
    print("\n✅ CEO数据更新完成\n")


if __name__ == '__main__':
    update_all_data()

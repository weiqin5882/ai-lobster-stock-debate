#!/usr/bin/env python3
"""
定时任务脚本 - 每天上午9点更新Polymarket热门市场数据
"""

import os
import sys
import schedule
import time
from datetime import datetime
from pathlib import Path

# 添加项目目录到路径
project_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_dir))

def update_job():
    """更新任务"""
    print(f"\n{'='*60}")
    print(f"🕘 定时任务执行: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    try:
        from polymarket import update_hot_markets
        success = update_hot_markets()
        if success:
            print("\n✅ 定时任务完成\n")
        else:
            print("\n❌ 定时任务失败\n")
    except Exception as e:
        print(f"\n❌ 定时任务异常: {e}\n")

def run_scheduler():
    """运行调度器"""
    print("\n" + "="*60)
    print("🦞 AI龙虾 - Polymarket数据定时更新服务")
    print("="*60)
    print("\n📅 定时任务:")
    print("   每天上午 09:00 自动更新Polymarket热门市场数据")
    print("\n📝 手动更新:")
    print("   访问 http://localhost:3000 点击刷新按钮")
    print("   或直接运行: python polymarket.py")
    print("\n⏳ 等待定时任务...\n")
    
    # 设置每天9点执行任务
    schedule.every().day.at("09:00").do(update_job)
    
    # 立即执行一次（启动时）
    print("🚀 启动时立即执行一次更新...")
    update_job()
    
    # 持续运行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

if __name__ == '__main__':
    run_scheduler()

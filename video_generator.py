#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频生成脚本 - Python版本
每日定时运行，为不同类别生成视频并同步文件
"""

import requests
import subprocess
import logging
from datetime import datetime
import sys
import os
import time
import schedule
from threading import Thread

# 创建日志目录
os.makedirs('logs', exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/video_generator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 配置参数
API_URL = os.getenv('API_URL', 'http://localhost:3100/api/generate-video')
RSYNC_SOURCE = os.getenv('RSYNC_SOURCE', './data/output')
RSYNC_DEST = os.getenv('RSYNC_DEST', 'root@112.126.78.105:~/web/x')
SSH_KEY_PATH = os.getenv('SSH_KEY_PATH', '~/.ssh/id_rsa')
SCHEDULE_TIME = os.getenv('SCHEDULE_TIME', '14:00')  # 2PM CST

def generate_video_for_category(category: str, today: str) -> bool:
    """
    为指定类别生成视频
    
    Args:
        category: 商品类别
        today: 日期字符串 (YYYY-MM-DD)
    
    Returns:
        bool: 是否成功
    """
    title = f"北方地区今日{category}价格({today})"
    
    payload = {
        'title': title,
        'category': category,
        'targetDate': today
    }
    
    try:
        logger.info(f"正在为类别 '{category}' 生成视频...")
        logger.info(f"请求URL: {API_URL}")
        logger.info(f"请求参数: {payload}")
        
        response = requests.post(API_URL, json=payload, timeout=300)
        
        if response.status_code == 200:
            logger.info(f"类别 '{category}' 视频生成成功")
            return True
        else:
            logger.error(f"类别 '{category}' 视频生成失败: HTTP {response.status_code}")
            logger.error(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"类别 '{category}' 请求失败: {str(e)}")
        return False

def sync_files() -> bool:
    """
    使用rsync同步文件到远程服务器
    
    Returns:
        bool: 是否成功
    """
    try:
        logger.info("开始同步文件...")
        
        # 展开SSH密钥路径
        ssh_key_path = os.path.expanduser(SSH_KEY_PATH)
        
        # 构建rsync命令
        cmd = [
            'rsync',
            '-avz',
            '-e', f'ssh -i {ssh_key_path} -o StrictHostKeyChecking=no',
            RSYNC_SOURCE,
            RSYNC_DEST
        ]
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )
        
        if result.returncode == 0:
            logger.info("文件同步成功")
            logger.info(f"rsync输出: {result.stdout}")
            return True
        else:
            logger.error(f"文件同步失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("文件同步超时")
        return False
    except Exception as e:
        logger.error(f"文件同步异常: {str(e)}")
        return False

def run_video_generation():
    """
    执行视频生成任务
    """
    logger.info("=== 视频生成任务开始 ===")
    
    # 商品类别数组
    categories = ["蔬菜", "水果", "水产", "肉禽蛋"]
    
    # 获取今天的日期
    today = datetime.now().strftime('%Y-%m-%d')
    logger.info(f"处理日期: {today}")
    
    # 记录成功和失败的统计
    success_count = 0
    failed_categories = []
    
    # 为每个类别生成视频
    for category in categories:
        if generate_video_for_category(category, today):
            success_count += 1
        else:
            failed_categories.append(category)
    
    # 输出统计信息
    logger.info(f"视频生成完成: 成功 {success_count}/{len(categories)}")
    if failed_categories:
        logger.warning(f"失败的类别: {', '.join(failed_categories)}")
    
    # 同步文件
    sync_success = sync_files()
    if sync_success:
        logger.info("所有任务完成")
    else:
        logger.error("文件同步失败，但视频生成任务已完成")
    
    logger.info("=== 视频生成任务结束 ===")
    return len(failed_categories) == 0 and sync_success

def run_scheduler():
    """
    运行调度器
    """
    logger.info(f"启动调度器，每日 {SCHEDULE_TIME} 执行视频生成任务")
    
    # 设置定时任务
    schedule.every().day.at(SCHEDULE_TIME).do(run_video_generation)
    
    logger.info("调度器已启动，等待执行时间...")
    logger.info("按 Ctrl+C 停止程序")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在退出...")
        sys.exit(0)

def main():
    """
    主函数
    """
    if len(sys.argv) > 1:
        if sys.argv[1] == '--run-once':
            # 立即执行一次
            logger.info("立即执行模式")
            success = run_video_generation()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == '--help':
            print("使用方法:")
            print("  python video_generator.py           # 启动定时调度器")
            print("  python video_generator.py --run-once # 立即执行一次")
            print("  python video_generator.py --help     # 显示帮助信息")
            print("")
            print("环境变量:")
            print(f"  API_URL={API_URL}")
            print(f"  RSYNC_SOURCE={RSYNC_SOURCE}")
            print(f"  RSYNC_DEST={RSYNC_DEST}")
            print(f"  SSH_KEY_PATH={SSH_KEY_PATH}")
            print(f"  SCHEDULE_TIME={SCHEDULE_TIME}")
            sys.exit(0)
    
    # 默认启动调度器
    run_scheduler()

if __name__ == '__main__':
    main()
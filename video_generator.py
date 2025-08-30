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

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/video_generator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 配置参数
API_URL = os.getenv('API_URL', 'http://localhost:3100/api/generate-video')
RSYNC_SOURCE = os.getenv('RSYNC_SOURCE', '/root/code/price-data/data/output')
RSYNC_DEST = os.getenv('RSYNC_DEST', 'root@112.126.78.105:~/web/x')
SSH_KEY_PATH = os.getenv('SSH_KEY_PATH', '/root/.ssh/id_rsa')

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
        
        # 构建rsync命令
        cmd = [
            'rsync',
            '-avz',
            '-e', f'ssh -i {SSH_KEY_PATH} -o StrictHostKeyChecking=no',
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

def main():
    """
    主函数
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
    if sync_files():
        logger.info("所有任务完成")
    else:
        logger.error("文件同步失败，但视频生成任务已完成")
    
    logger.info("=== 视频生成任务结束 ===")
    
    # 如果有失败的任务，返回非零退出码
    if failed_categories or not sync_files():
        sys.exit(1)

if __name__ == '__main__':
    main()
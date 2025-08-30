#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置脚本 - 快速配置视频生成器
"""

import os
import subprocess
import sys

def create_directories():
    """创建必要的目录"""
    directories = ['logs', 'data', 'data/output']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ 创建目录: {directory}")

def install_dependencies():
    """安装Python依赖"""
    print("正在安装Python依赖...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ 依赖安装完成")
    except subprocess.CalledProcessError:
        print("✗ 依赖安装失败")
        return False
    return True

def create_env_file():
    """创建环境变量配置文件"""
    if not os.path.exists('.env'):
        with open('.env', 'w', encoding='utf-8') as f:
            f.write("# 视频生成器配置\n")
            f.write("API_URL=http://localhost:3100/api/generate-video\n")
            f.write("RSYNC_SOURCE=./data/output\n")
            f.write("RSYNC_DEST=root@112.126.78.105:~/web/x\n")
            f.write("SSH_KEY_PATH=~/.ssh/id_rsa\n")
            f.write("SCHEDULE_TIME=14:00\n")
        print("✓ 创建 .env 配置文件")
    else:
        print("✓ .env 文件已存在")

def main():
    print("=== 视频生成器设置 ===")
    print()
    
    # 创建目录
    create_directories()
    print()
    
    # 安装依赖
    if not install_dependencies():
        sys.exit(1)
    print()
    
    # 创建配置文件
    create_env_file()
    print()
    
    print("=== 设置完成 ===")
    print()
    print("下一步:")
    print("1. 编辑 .env 文件，配置你的API地址和服务器信息")
    print("2. 确保SSH密钥已配置")
    print("3. 运行测试: python video_generator.py --run-once")
    print("4. 启动调度器: python video_generator.py")
    print()

if __name__ == '__main__':
    main()
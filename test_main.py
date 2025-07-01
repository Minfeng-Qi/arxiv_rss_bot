#!/usr/bin/env python3
"""
arXiv RSS Filter Bot - 主程序测试脚本
用于测试 main.py 的功能是否正常
"""

import logging
import os
import sys
import time
import argparse
import subprocess
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_main')

def check_directory_structure():
    """检查目录结构是否正确"""
    logger.info("检查目录结构")
    
    required_dirs = ['logs', 'output']
    missing_dirs = []
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
    
    if missing_dirs:
        logger.warning(f"缺少以下目录: {', '.join(missing_dirs)}")
        return False
    else:
        logger.info("所有必要的目录都存在")
        return True

def check_output_files():
    """检查输出文件是否生成"""
    logger.info("检查输出文件")
    
    # 检查日志文件
    log_files = [f for f in os.listdir('logs') if f.startswith('arxiv_rss_bot_')]
    if not log_files:
        logger.warning("未找到日志文件")
        return False
    
    # 检查RSS文件
    rss_files = [f for f in os.listdir('output') if f.endswith('.xml')]
    if not rss_files:
        logger.warning("未找到RSS文件")
        return False
    
    logger.info(f"找到 {len(log_files)} 个日志文件和 {len(rss_files)} 个RSS文件")
    
    # 获取最新的日志文件和RSS文件
    latest_log = max(log_files, key=lambda x: os.path.getmtime(os.path.join('logs', x)))
    latest_rss = max(rss_files, key=lambda x: os.path.getmtime(os.path.join('output', x)))
    
    logger.info(f"最新的日志文件: {latest_log}")
    logger.info(f"最新的RSS文件: {latest_rss}")
    
    return True

def run_main_program():
    """运行主程序"""
    logger.info("开始运行主程序")
    
    try:
        # 运行主程序
        process = subprocess.run(['python', 'main.py'], 
                                capture_output=True, 
                                text=True, 
                                check=False)
        
        # 检查返回码
        if process.returncode == 0:
            logger.info("主程序成功运行，返回码: 0")
        else:
            logger.error(f"主程序运行失败，返回码: {process.returncode}")
            
        # 输出程序输出
        logger.info("程序标准输出:")
        for line in process.stdout.splitlines():
            logger.info(f"  {line}")
            
        if process.stderr:
            logger.warning("程序错误输出:")
            for line in process.stderr.splitlines():
                logger.warning(f"  {line}")
        
        return process.returncode == 0
    
    except Exception as e:
        logger.error(f"运行主程序时出错: {str(e)}", exc_info=True)
        return False

def test_main():
    """测试主程序功能"""
    logger.info("开始测试主程序")
    
    # 检查目录结构
    if not check_directory_structure():
        logger.info("创建必要的目录")
        os.makedirs("logs", exist_ok=True)
        os.makedirs("output", exist_ok=True)
    
    # 运行主程序
    success = run_main_program()
    
    if success:
        # 检查输出文件
        files_ok = check_output_files()
        if files_ok:
            logger.info("主程序测试成功完成")
            return True
        else:
            logger.error("未能生成预期的输出文件")
            return False
    else:
        logger.error("主程序运行失败")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='测试arXiv RSS Filter Bot主程序')
    parser.add_argument('--check-only', action='store_true', 
                        help='只检查目录和文件，不运行主程序')
    args = parser.parse_args()
    
    if args.check_only:
        # 只检查目录和文件
        check_directory_structure()
        check_output_files()
    else:
        # 完整测试
        success = test_main()
        sys.exit(0 if success else 1)
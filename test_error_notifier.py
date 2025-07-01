#!/usr/bin/env python3
"""
arXiv RSS Filter Bot - 错误通知测试脚本
用于测试 error_notifier.py 的错误通知功能
"""

import logging
import os
import sys
import yaml
import time
from datetime import datetime
import argparse

# 导入需要测试的模块
import smtplib
from error_notifier import send_error_notification

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_error_notifier')

def load_test_config(config_file='test_config.yaml'):
    """加载测试配置"""
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as file:
                config = yaml.safe_load(file)
            logger.info(f"从 {config_file} 加载了配置")
            return config
        else:
            logger.warning(f"配置文件 {config_file} 不存在，尝试加载默认配置")
            with open('config.yaml', 'r') as file:
                config = yaml.safe_load(file)
            return config
    except Exception as e:
        logger.error(f"加载配置文件出错: {str(e)}")
        return {}

def create_sample_error():
    """创建一个示例错误"""
    try:
        # 故意引发一个除零错误作为测试
        result = 1 / 0
    except Exception as e:
        return str(e)

def test_with_mock(config):
    """使用模拟方式测试错误通知功能"""
    logger.info("使用模拟方式测试错误通知功能")
    
    # 创建临时的日志处理器来捕获日志输出
    class LogCatcher(logging.Handler):
        def __init__(self):
            super().__init__()
            self.log_records = []
            
        def emit(self, record):
            self.log_records.append(record.getMessage())
    
    # 添加日志捕获器
    log_catcher = LogCatcher()
    error_logger = logging.getLogger('error_notifier')
    error_logger.addHandler(log_catcher)
    
    # 获取原始级别并临时设置为INFO
    original_level = error_logger.level
    error_logger.setLevel(logging.INFO)
    
    # 创建一个示例错误消息
    error_message = create_sample_error()
    
    # 如果配置中没有邮件设置，创建一个空的配置
    if 'email' not in config:
        email_config = {
            'smtp_server': '',
            'username': '',
            'password': '',
            'recipient': ''
        }
    else:
        email_config = config.get('email', {})
    
    # 创建一个模拟的SMTP类
    original_smtp = smtplib.SMTP
    
    class MockSMTP:
        def __init__(self, host='', port=0, *args, **kwargs):
            self.host = host
            self.port = port
            logger.info(f"模拟连接到SMTP服务器: {host}:{port}")
            
        def starttls(self):
            logger.info("模拟启用TLS加密")
            return (220, "Ready to start TLS")
            
        def login(self, username, password):
            logger.info(f"模拟登录邮箱: {username}")
            return (235, "Authentication successful")
            
        def send_message(self, msg):
            logger.info(f"模拟发送邮件: 从Sender={msg['From']} 到Recipient={msg['To']} 主题={msg['Subject']}")
            return {}
            
        def quit(self):
            logger.info("模拟关闭连接")
            return (221, "Bye")
    
    # 替换SMTP类为模拟类
    try:
        smtplib.SMTP = MockSMTP
        
        # 调用错误通知函数
        send_error_notification(error_message, email_config)
        logger.info("使用模拟方式成功测试了邮件发送功能")
        
    finally:
        # 恢复原始的SMTP类
        smtplib.SMTP = original_smtp
    
    # 恢复原始日志级别
    error_logger.setLevel(original_level)
    error_logger.removeHandler(log_catcher)
    
    # 检查日志输出
    if not log_catcher.log_records:
        logger.warning("未捕获到任何日志记录")
    else:
        logger.info(f"捕获到 {len(log_catcher.log_records)} 条日志记录")
        for record in log_catcher.log_records:
            logger.info(f"日志记录: {record}")
    
    return True

def test_real_email(config):
    """使用真实邮件测试错误通知功能"""
    logger.info("使用真实邮件测试错误通知功能")
    
    # 检查是否有完整的邮件配置
    email_config = config.get('email', {})
    required_fields = ['smtp_server', 'username', 'password', 'recipient']
    
    if not all(field in email_config for field in required_fields):
        logger.warning("邮件配置不完整，无法发送真实邮件测试")
        for field in required_fields:
            if field not in email_config:
                logger.warning(f"缺少配置: {field}")
        return False
    
    # 创建一个示例错误消息
    error_message = f"这是一条测试错误消息，生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    try:
        # 调用错误通知函数
        send_error_notification(error_message, email_config)
        
        logger.info(f"已尝试发送测试邮件至 {email_config.get('recipient')}")
        logger.info("请检查您的收件箱，确认是否收到测试邮件")
        return True
    except Exception as e:
        logger.error(f"发送测试邮件时出错: {str(e)}", exc_info=True)
        return False

def run_test(send_real_email=False, config_file='test_config.yaml'):
    """运行测试"""
    logger.info("开始测试错误通知功能")
    
    try:
        # 加载测试配置
        config = load_test_config(config_file)
        
        # 打印邮件配置信息(不显示密码)
        email_config = config.get('email', {})
        if email_config:
            safe_config = {k: (v if k != 'password' else '********') for k, v in email_config.items()}
            logger.info(f"邮件配置: {safe_config}")
            
        # 根据参数选择测试方式
        if send_real_email:
            return test_real_email(config)
        else:
            return test_with_mock(config)
            
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='测试错误通知功能')
    parser.add_argument('--send-email', action='store_true', 
                        help='发送真实测试邮件 (默认: 仅模拟测试)')
    parser.add_argument('--config', type=str, default='test_config.yaml',
                        help='指定配置文件路径 (默认: test_config.yaml)')
    args = parser.parse_args()
    
    # 运行测试
    success = run_test(send_real_email=args.send_email, config_file=args.config)
    sys.exit(0 if success else 1)
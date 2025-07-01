#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
邮件通知模块
用于在发生错误或运行完成时发送邮件通知
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

def send_notification(subject, message, to_email=None, config=None):
    """
    发送邮件通知
    
    参数:
        subject (str): 邮件主题
        message (str): 邮件内容
        to_email (str): 收件人邮箱，如果为None则使用配置中的邮箱
        config (dict): 配置信息，如果为None则不发送邮件
    
    返回:
        bool: 是否发送成功
    """
    if not config or not config.get('email_on_error'):
        logger.debug("邮件通知已禁用")
        return False
        
    smtp_server = config.get('smtp_server')
    smtp_port = config.get('smtp_port', 587)
    smtp_username = config.get('smtp_username')
    smtp_password = config.get('smtp_password')
    from_email = config.get('from_email', smtp_username)
    to_email = to_email or config.get('to_email')
    
    # 检查必要的配置
    if not all([smtp_server, smtp_username, smtp_password, to_email]):
        logger.error("缺少必要的邮件配置，无法发送通知")
        return False
        
    try:
        # 创建多部分消息
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # 添加正文
        msg.attach(MIMEText(message, 'plain'))
        
        # 连接到SMTP服务器
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # 使用TLS加密连接
            server.starttls()
            # 登录
            server.login(smtp_username, smtp_password)
            # 发送邮件
            server.sendmail(from_email, to_email, msg.as_string())
            
        logger.info(f"成功发送邮件通知到 {to_email}")
        return True
            
    except Exception as e:
        logger.error(f"发送邮件通知失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 测试邮件发送
    logging.basicConfig(level=logging.INFO)
    test_config = {
        'email_on_error': True,
        'smtp_server': 'smtp.example.com',
        'smtp_port': 587,
        'smtp_username': 'your_username',
        'smtp_password': 'your_password',
        'from_email': 'sender@example.com',
        'to_email': 'recipient@example.com'
    }
    send_notification(
        "ArXiv RSS Filter Bot - 测试通知", 
        "这是一封测试邮件，如果您收到此邮件，说明邮件通知功能正常工作。", 
        config=test_config
    )
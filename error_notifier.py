"""
arXiv RSS Filter Bot - Error Notification Module
arXiv RSS 过滤机器人 - 错误通知模块

该模块负责在程序运行出错时发送邮件通知。
当流水线中的任何环节出现异常时，可以通过邮件向管理员发送详细的错误信息。
"""

import logging  # 导入日志模块
import smtplib  # 导入SMTP客户端模块，用于发送邮件
from email.mime.text import MIMEText  # 导入邮件文本内容类
from email.mime.multipart import MIMEMultipart  # 导入邮件多部分内容类
import socket  # 导入套接字模块，用于获取主机名
import traceback  # 导入堆栈跟踪模块，用于获取详细错误信息
from datetime import datetime  # 导入日期时间模块

logger = logging.getLogger(__name__)  # 获取当前模块的日志记录器

def send_error_notification(error_message, email_config):
    """
    当发生错误时发送邮件通知
    
    Args:
        error_message (str): 错误信息
        email_config (dict): 邮件配置参数
        
    注意：该函数不会抛出异常，以避免在错误处理中产生新的错误
    """
    try:
        # 从配置中获取邮件参数
        smtp_server = email_config.get('smtp_server')  # SMTP服务器地址
        port = email_config.get('port', 587)  # SMTP服务器端口，默认587
        username = email_config.get('username')  # 邮箱用户名
        password = email_config.get('password')  # 邮箱密码
        recipient = email_config.get('recipient')  # 收件人地址
        
        # 检查是否所有必要的配置都存在
        if not all([smtp_server, username, password, recipient]):
            logger.error("Incomplete email configuration, cannot send notification")  # 记录错误：邮件配置不完整
            return
            
        # 创建邮件对象
        msg = MIMEMultipart()  # 创建多部分邮件
        msg['From'] = username  # 设置发件人
        msg['To'] = recipient  # 设置收件人
        msg['Subject'] = f"arXiv RSS Bot Error - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"  # 设置邮件主题，包含时间戳
        
        # 创建包含错误详情的邮件正文
        hostname = socket.gethostname()  # 获取主机名
        body = f"""
An error occurred in the arXiv RSS Filter Bot:

Error Message: {error_message}

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Hostname: {hostname}

Stack Trace:
{traceback.format_exc()}
        """
        
        msg.attach(MIMEText(body, 'plain'))  # 将正文添加到邮件中
        
        # 连接到服务器并发送邮件
        server = smtplib.SMTP(smtp_server, port)  # 连接到SMTP服务器
        server.starttls()  # 启用TLS加密
        server.login(username, password)  # 登录邮箱
        server.send_message(msg)  # 发送邮件
        server.quit()  # 关闭连接
        
        logger.info(f"Error notification email sent to {recipient}")  # 记录邮件发送成功
        
    except Exception as e:  # 捕获所有可能的异常
        logger.error(f"Failed to send error notification: {str(e)}", exc_info=True)  # 记录发送邮件时的错误
        # 不再抛出异常，避免级联错误 
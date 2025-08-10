#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
arXiv RSS Filter Bot - Email Subscription Module
arXiv RSS 过滤机器人 - 邮件订阅模块

该模块负责将最新的RSS内容发送到订阅邮箱，避免发送重复的论文。
"""

import os
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from config_loader import load_config
import re
from collections import defaultdict

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 定义目录路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_DIR = os.path.join(SCRIPT_DIR, "history")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
SUBSCRIPTION_HISTORY_FILE = os.path.join(SCRIPT_DIR, "subscription_history.json")

def load_subscription_history():
    """
    加载订阅历史记录，用于避免发送重复的论文
    
    Returns:
        dict: 包含已发送论文ID的字典
    """
    if not os.path.exists(SUBSCRIPTION_HISTORY_FILE):
        return {"sent_papers": [], "last_sent": None}
    
    try:
        with open(SUBSCRIPTION_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载订阅历史记录失败: {str(e)}")
        return {"sent_papers": [], "last_sent": None}

def save_subscription_history(history):
    """
    保存订阅历史记录
    
    Args:
        history (dict): 包含已发送论文ID的字典
    """
    try:
        with open(SUBSCRIPTION_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
        logger.info(f"订阅历史记录已保存到 {SUBSCRIPTION_HISTORY_FILE}")
    except Exception as e:
        logger.error(f"保存订阅历史记录失败: {str(e)}")

def get_latest_rss_file():
    """
    获取最新的RSS文件
    
    Returns:
        str: 最新RSS文件的路径，如果没有找到则返回None
    """
    if not os.path.exists(OUTPUT_DIR):
        logger.error(f"输出目录不存在: {OUTPUT_DIR}")
        return None
        
    rss_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.xml')]
    if not rss_files:
        logger.info("没有找到RSS文件")
        return None
        
    # 按文件修改时间排序（最新在前）
    rss_files.sort(key=lambda f: os.path.getmtime(os.path.join(OUTPUT_DIR, f)), reverse=True)
    return os.path.join(OUTPUT_DIR, rss_files[0])

def parse_rss_file(rss_file):
    """
    解析RSS文件，提取论文信息
    
    Args:
        rss_file (str): RSS文件路径
        
    Returns:
        list: 论文信息列表
    """
    try:
        tree = ET.parse(rss_file)
        root = tree.getroot()
        
        papers = []
        for item in root.findall('./channel/item'):
            paper = {
                'title': item.find('title').text if item.find('title') is not None else 'No Title',
                'link': item.find('link').text if item.find('link') is not None else '',
                'description': item.find('description').text if item.find('description') is not None else '',
                'guid': item.find('guid').text if item.find('guid') is not None else '',
                'pubDate': item.find('pubDate').text if item.find('pubDate') is not None else ''
            }
            papers.append(paper)
            
        return papers
    except Exception as e:
        logger.error(f"解析RSS文件失败: {str(e)}")
        return []

def classify_paper(paper, categories_config):
    """
    根据标题和摘要对论文进行分类
    
    Args:
        paper (dict): 论文信息
        categories_config (dict): 分类配置
        
    Returns:
        str: 分类名称，如果没有匹配则返回'🔧 Other AI/ML'
    """
    title = paper['title'].lower()
    description = paper['description'].lower()
    text_content = f"{title} {description}"
    
    # 遍历所有分类，找到第一个匹配的
    for category_name, keywords in categories_config.items():
        for keyword in keywords:
            if keyword.lower() in text_content:
                return category_name
    
    # 如果没有匹配到任何分类，返回默认分类
    return "🔧 Other AI/ML"

def parse_pub_date(pub_date_str):
    """
    解析发布日期字符串为datetime对象
    
    Args:
        pub_date_str (str): 发布日期字符串
        
    Returns:
        datetime: 解析后的日期对象
    """
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(pub_date_str)
    except:
        # 如果解析失败，返回一个很老的日期，确保排序时排在后面
        return datetime(1900, 1, 1, tzinfo=timezone.utc)

def categorize_and_sort_papers(papers, config):
    """
    对论文进行分类并按时间排序
    
    Args:
        papers (list): 论文列表
        config (dict): 配置信息
        
    Returns:
        dict: 按分类组织的论文字典，每个分类内按时间降序排序
    """
    categories_config = config.get('paper_categories', {})
    if not categories_config:
        # 如果没有配置分类，使用默认分类
        categories_config = {"🔧 All Papers": []}
    
    # 按分类组织论文
    categorized_papers = defaultdict(list)
    
    for paper in papers:
        # 解析发布日期
        paper['parsed_date'] = parse_pub_date(paper.get('pubDate', ''))
        
        # 分类论文
        category = classify_paper(paper, categories_config)
        categorized_papers[category].append(paper)
    
    # 每个分类内按时间降序排序（最新的在前）
    for category in categorized_papers:
        categorized_papers[category].sort(
            key=lambda x: x['parsed_date'], 
            reverse=True
        )
    
    # 按分类名称排序，确保一致的显示顺序
    sorted_categories = dict(sorted(categorized_papers.items()))
    
    return sorted_categories

def send_subscription_email(papers, config):
    """
    发送订阅邮件
    
    Args:
        papers (list): 论文信息列表
        config (dict): 配置信息
        
    Returns:
        bool: 是否发送成功
    """
    if not papers:
        logger.info("没有新论文需要发送")
        return False
        
    # 从配置中获取邮件参数
    email_config = config.get('email', {})
    smtp_server = email_config.get('smtp_server')
    port = email_config.get('port', 587)
    username = email_config.get('username')
    password = email_config.get('password')
    recipient = email_config.get('recipient')
    
    # 检查必要的配置
    if not all([smtp_server, username, password, recipient]):
        logger.error("邮件配置不完整，无法发送订阅邮件")
        return False
        
    try:
        # 对论文进行分类和排序
        categorized_papers = categorize_and_sort_papers(papers, config)
        total_papers = sum(len(papers_in_cat) for papers_in_cat in categorized_papers.values())
        
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = recipient
        msg['Subject'] = f"arXiv RSS Filter Bot - 最新论文更新 ({datetime.now().strftime('%Y-%m-%d')})"
        
        # 构建邮件正文
        body = f"""<html>
<head>
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
    .category {{ margin-bottom: 30px; }}
    .category-title {{ 
      font-size: 20px; 
      font-weight: bold; 
      color: #2c3e50; 
      margin-bottom: 15px;
      padding-bottom: 5px;
      border-bottom: 2px solid #3498db;
    }}
    .paper {{ 
      margin-bottom: 20px; 
      padding: 15px; 
      border: 1px solid #e0e0e0; 
      border-radius: 8px;
      background-color: #f9f9f9;
    }}
    .title {{ font-size: 16px; font-weight: bold; color: #1a0dab; margin-bottom: 5px; }}
    .link {{ color: #1a0dab; text-decoration: none; }}
    .link:hover {{ text-decoration: underline; }}
    .pub-date {{ font-size: 12px; color: #666; margin-bottom: 8px; }}
    .description {{ font-size: 14px; color: #333; }}
    .category-summary {{ font-size: 14px; color: #7f8c8d; margin-bottom: 10px; }}
  </style>
</head>
<body>
  <h2>🎯 arXiv RSS Filter Bot - 最新论文更新</h2>
  <p>共找到 <strong>{total_papers}</strong> 篇符合您兴趣的最新论文，按类别整理如下：</p>
"""
        
        # 按分类添加论文
        for category_name, papers_in_category in categorized_papers.items():
            if not papers_in_category:
                continue
                
            body += f"""
  <div class="category">
    <div class="category-title">{category_name}</div>
    <div class="category-summary">本类别共 {len(papers_in_category)} 篇论文，按发表时间排序：</div>
"""
            
            for paper in papers_in_category:
                title = paper['title']
                link = paper['link']
                pub_date = paper['pubDate']
                
                # 处理摘要内容和作者信息
                description = paper['description'] if paper['description'] else '无摘要'
                authors = '暂无作者信息'
                
                if description != '无摘要':
                    lines = description.split('\n')
                    abstract_lines = []
                    found_authors = False
                    
                    for line in lines:
                        if line.strip().startswith('Authors:'):
                            # 提取作者信息
                            authors = line.strip().replace('Authors:', '').strip()
                            found_authors = True
                            continue
                        if found_authors and line.strip():
                            abstract_lines.append(line.strip())
                    
                    # 将摘要合并为连贯的段落
                    if abstract_lines:
                        description = ' '.join(abstract_lines)
                    else:
                        # 如果没找到Authors:行，使用原始描述但去除多余换行
                        description = ' '.join(line.strip() for line in lines if line.strip())
                
                body += f"""
    <div class="paper">
      <div class="title"><a href="{link}" class="link">{title}</a></div>
      <div class="pub-date">📅 发表日期: {pub_date}</div>
      <div class="pub-date">👥 作者: {authors}</div>
      <div class="description">{description}</div>
    </div>
"""
            
            body += "  </div>"  # 关闭category div
        
        body += """
  <hr style="margin-top: 40px; border: none; border-top: 1px solid #bdc3c7;">
  <p style="text-align: center; color: #7f8c8d; font-size: 12px;">
    由 arXiv RSS Filter Bot 自动生成 | 每日自动推送最新论文
  </p>
</body></html>"""
        
        # 添加HTML正文
        msg.attach(MIMEText(body, 'html'))
        
        # 发送邮件
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            
        logger.info(f"成功发送订阅邮件到 {recipient}")
        return True
            
    except Exception as e:
        logger.error(f"发送订阅邮件失败: {str(e)}")
        return False

def run_subscription():
    """
    运行订阅功能
    """
    logger.info("开始运行订阅功能")
    
    # 加载配置
    config = load_config()
    
    # 检查是否启用邮件订阅
    if not config.get('email_subscription', False):
        logger.info("邮件订阅功能未启用，跳过")
        return False
    
    # 检查邮件配置是否完整
    email_config = config.get('email', {})
    required_fields = ['smtp_server', 'port', 'username', 'password', 'recipient']
    missing_fields = [field for field in required_fields if not email_config.get(field)]
    
    if missing_fields:
        logger.error(f"邮件配置不完整，缺少字段: {', '.join(missing_fields)}")
        return False
    
    # 加载订阅历史记录
    subscription_history = load_subscription_history()
    sent_papers = set(subscription_history.get("sent_papers", []))
    logger.info(f"已加载订阅历史记录，共有 {len(sent_papers)} 篇已发送论文")
    
    # 获取最新的RSS文件
    latest_rss = get_latest_rss_file()
    if not latest_rss:
        logger.info("没有找到RSS文件，无法发送订阅邮件")
        return False
        
    # 解析RSS文件
    all_papers = parse_rss_file(latest_rss)
    logger.info(f"从RSS文件中解析到 {len(all_papers)} 篇论文")
    
    # 过滤出新论文
    new_papers = [p for p in all_papers if p['guid'] not in sent_papers]
    logger.info(f"找到 {len(new_papers)} 篇新论文")
    
    if new_papers:
        # 发送订阅邮件
        success = send_subscription_email(new_papers, config)
        
        if success:
            # 更新订阅历史记录
            for paper in new_papers:
                sent_papers.add(paper['guid'])
            
            subscription_history["sent_papers"] = list(sent_papers)
            subscription_history["last_sent"] = datetime.now().isoformat()
            save_subscription_history(subscription_history)
            
            logger.info(f"成功发送 {len(new_papers)} 篇新论文，并更新了订阅历史记录")
            return True
        else:
            logger.error("发送订阅邮件失败")
    else:
        logger.info("没有新论文需要发送")
        
    return False

if __name__ == "__main__":
    run_subscription() 
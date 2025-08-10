#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Conference Paper Subscription Module
会议论文订阅模块

该模块负责将最新的会议论文发送到订阅邮箱，支持按会议和类别推送
"""

import os
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from collections import defaultdict
from config_loader import load_config
from openreview_fetcher import run_conference_fetch

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 定义目录路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFERENCE_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "conference_output")
CONFERENCE_SUBSCRIPTION_HISTORY_FILE = os.path.join(SCRIPT_DIR, "conference_subscription_history.json")

def load_conference_subscription_history():
    """
    加载会议订阅历史记录，用于避免发送重复的论文
    
    Returns:
        dict: 包含已发送论文ID的字典
    """
    if not os.path.exists(CONFERENCE_SUBSCRIPTION_HISTORY_FILE):
        return {"sent_papers": [], "last_sent": None, "sent_by_conference": {}}
    
    try:
        with open(CONFERENCE_SUBSCRIPTION_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载会议订阅历史记录失败: {str(e)}")
        return {"sent_papers": [], "last_sent": None, "sent_by_conference": {}}

def save_conference_subscription_history(history):
    """
    保存会议订阅历史记录
    
    Args:
        history (dict): 包含已发送论文ID的字典
    """
    try:
        with open(CONFERENCE_SUBSCRIPTION_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        logger.info(f"会议订阅历史记录已保存到 {CONFERENCE_SUBSCRIPTION_HISTORY_FILE}")
    except Exception as e:
        logger.error(f"保存会议订阅历史记录失败: {str(e)}")

def get_latest_conference_files():
    """
    获取最新的会议论文文件
    
    Returns:
        list: 最新会议论文文件的路径列表
    """
    if not os.path.exists(CONFERENCE_OUTPUT_DIR):
        logger.error(f"会议输出目录不存在: {CONFERENCE_OUTPUT_DIR}")
        return []
        
    conference_files = [f for f in os.listdir(CONFERENCE_OUTPUT_DIR) if f.endswith('.json')]
    if not conference_files:
        logger.info("没有找到会议论文文件")
        return []
        
    # 按文件修改时间排序（最新在前）
    conference_files.sort(key=lambda f: os.path.getmtime(os.path.join(CONFERENCE_OUTPUT_DIR, f)), reverse=True)
    return [os.path.join(CONFERENCE_OUTPUT_DIR, f) for f in conference_files]

def parse_conference_file(file_path):
    """
    解析会议论文文件，提取论文信息
    
    Args:
        file_path (str): 会议论文文件路径
        
    Returns:
        dict: 会议论文信息
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"解析会议论文文件失败: {str(e)}")
        return {}

def classify_conference_paper(paper, categories_config):
    """
    根据标题和摘要对会议论文进行分类
    
    Args:
        paper (dict): 论文信息
        categories_config (dict): 分类配置
        
    Returns:
        str: 分类名称，如果没有匹配则返回'🔧 Other'
    """
    title = paper.get('title', '').lower()
    abstract = paper.get('abstract', '').lower()
    text_content = f"{title} {abstract}"
    
    # 检查匹配的关键词
    matched_keywords = paper.get('matched_keywords', [])
    
    # 遍历所有分类，找到第一个匹配的
    for category_name, keywords in categories_config.items():
        for keyword in keywords:
            if keyword.lower() in text_content or keyword.lower() in matched_keywords:
                return category_name
    
    # 如果没有匹配到任何分类，返回默认分类
    return "🔧 Other"

def categorize_and_sort_conference_papers(papers, config):
    """
    对会议论文进行分类并排序
    
    Args:
        papers (list): 论文列表
        config (dict): 配置信息
        
    Returns:
        dict: 按分类组织的论文字典
    """
    categories_config = config.get('conferences', {}).get('conference_paper_categories', {})
    if not categories_config:
        # 如果没有配置分类，使用默认分类
        categories_config = {"🔧 All Papers": []}
    
    # 按分类组织论文
    categorized_papers = defaultdict(list)
    
    for paper in papers:
        # 分类论文
        category = classify_conference_paper(paper, categories_config)
        categorized_papers[category].append(paper)
    
    # 每个分类内按获取时间排序（最新的在前）
    for category in categorized_papers:
        categorized_papers[category].sort(
            key=lambda x: x.get('fetched_at', ''), 
            reverse=True
        )
    
    # 按分类名称排序，确保一致的显示顺序
    sorted_categories = dict(sorted(categorized_papers.items()))
    
    return sorted_categories

def send_conference_subscription_email(conference_data, new_papers, config):
    """
    发送会议订阅邮件
    
    Args:
        conference_data (dict): 会议数据
        new_papers (list): 新论文列表
        config (dict): 配置信息
        
    Returns:
        bool: 是否发送成功
    """
    if not new_papers:
        logger.info("没有新的会议论文需要发送")
        return False
        
    # 从配置中获取邮件参数
    email_config = config.get('email', {})
    conference_email_config = config.get('conferences', {}).get('conference_email', {})
    
    smtp_server = email_config.get('smtp_server')
    port = email_config.get('port', 587)
    username = email_config.get('username')
    password = email_config.get('password')
    recipient = email_config.get('recipient')
    
    # 检查必要的配置
    if not all([smtp_server, username, password, recipient]):
        logger.error("邮件配置不完整，无法发送会议订阅邮件")
        return False
        
    try:
        # 对论文进行分类和排序
        categorized_papers = categorize_and_sort_conference_papers(new_papers, config)
        total_papers = sum(len(papers_in_cat) for papers_in_cat in categorized_papers.values())
        
        conference_name = conference_data.get('conference', 'Unknown Conference')
        subject_prefix = conference_email_config.get('subject_prefix', '[Conference Papers]')
        
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = recipient
        msg['Subject'] = f"{subject_prefix} {conference_name} - 最新论文更新 ({datetime.now().strftime('%Y-%m-%d')})"
        
        # 构建邮件正文
        body = f"""<html>
<head>
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
    .header {{ background-color: #3498db; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
    .conference-info {{ background-color: #ecf0f1; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
    .category {{ margin-bottom: 30px; }}
    .category-title {{ 
      font-size: 18px; 
      font-weight: bold; 
      color: #2c3e50; 
      margin-bottom: 15px;
      padding-bottom: 5px;
      border-bottom: 2px solid #e74c3c;
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
    .authors {{ font-size: 12px; color: #666; margin-bottom: 8px; }}
    .abstract {{ font-size: 14px; color: #333; margin-bottom: 8px; }}
    .keywords {{ font-size: 12px; color: #e74c3c; background-color: #fdf2f2; padding: 4px 8px; border-radius: 4px; }}
    .category-summary {{ font-size: 14px; color: #7f8c8d; margin-bottom: 10px; }}
  </style>
</head>
<body>
  <div class="header">
    <h2>🎓 {conference_name} - 会议论文更新</h2>
  </div>
  
  <div class="conference-info">
    <strong>📊 本次更新摘要:</strong><br>
    • 会议: {conference_name}<br>
    • 新增论文: <strong>{total_papers}</strong> 篇<br>
    • 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  </div>
"""
        
        # 按分类添加论文
        for category_name, papers_in_category in categorized_papers.items():
            if not papers_in_category:
                continue
                
            body += f"""
  <div class="category">
    <div class="category-title">{category_name}</div>
    <div class="category-summary">本类别共 {len(papers_in_category)} 篇论文：</div>
"""
            
            for paper in papers_in_category:
                title = paper.get('title', 'No Title')
                abstract = paper.get('abstract', 'No Abstract')
                authors = paper.get('authors', [])
                url = paper.get('url', '')
                matched_keywords = paper.get('matched_keywords', [])
                
                # 处理作者信息
                authors_str = ', '.join(authors[:5]) if authors else 'No Authors'
                if len(authors) > 5:
                    authors_str += f' (and {len(authors) - 5} more)'
                
                # 截断摘要
                abstract_display = abstract[:500] + '...' if len(abstract) > 500 else abstract
                
                # 匹配关键词显示
                keywords_display = ', '.join(matched_keywords[:5]) if matched_keywords else ''
                
                body += f"""
    <div class="paper">
      <div class="title"><a href="{url}" class="link">{title}</a></div>
      <div class="authors">👥 作者: {authors_str}</div>
      <div class="abstract">📝 摘要: {abstract_display}</div>"""
                
                if keywords_display:
                    body += f"""
      <div class="keywords">🔍 匹配关键词: {keywords_display}</div>"""
                
                body += """
    </div>"""
            
            body += "  </div>"  # 关闭category div
        
        body += """
  <hr style="margin-top: 40px; border: none; border-top: 1px solid #bdc3c7;">
  <p style="text-align: center; color: #7f8c8d; font-size: 12px;">
    🤖 由 arXiv RSS Filter Bot (Conference Extension) 自动生成<br>
    📧 会议论文自动推送服务 - 专注顶级AI与安全会议
  </p>
</body></html>"""
        
        # 添加HTML正文
        msg.attach(MIMEText(body, 'html'))
        
        # 发送邮件
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            
        logger.info(f"成功发送会议订阅邮件到 {recipient} - {conference_name}: {total_papers}篇论文")
        return True
            
    except Exception as e:
        logger.error(f"发送会议订阅邮件失败: {str(e)}")
        return False

def process_conference_subscription():
    """
    处理会议订阅功能
    """
    logger.info("开始处理会议论文订阅")
    
    # 加载配置
    config = load_config()
    
    # 检查是否启用会议论文订阅
    conference_config = config.get('conferences', {})
    if not conference_config.get('enabled', False):
        logger.info("会议论文功能未启用，跳过")
        return False
        
    conference_email_config = conference_config.get('conference_email', {})
    if not conference_email_config.get('enabled', False):
        logger.info("会议论文邮件订阅功能未启用，跳过")
        return False
    
    # 检查邮件配置是否完整
    email_config = config.get('email', {})
    required_fields = ['smtp_server', 'port', 'username', 'password', 'recipient']
    missing_fields = [field for field in required_fields if not email_config.get(field)]
    
    if missing_fields:
        logger.error(f"邮件配置不完整，缺少字段: {', '.join(missing_fields)}")
        return False
    
    # 加载订阅历史记录
    subscription_history = load_conference_subscription_history()
    sent_papers = set(subscription_history.get("sent_papers", []))
    sent_by_conference = subscription_history.get("sent_by_conference", {})
    
    logger.info(f"已加载会议订阅历史记录，共有 {len(sent_papers)} 篇已发送论文")
    
    # 获取最新的会议论文文件
    conference_files = get_latest_conference_files()
    if not conference_files:
        logger.info("没有找到会议论文文件")
        return False
    
    total_new_papers = 0
    successful_sends = 0
    
    # 处理每个会议文件
    for file_path in conference_files:
        try:
            logger.info(f"处理会议文件: {os.path.basename(file_path)}")
            
            # 解析会议文件
            conference_data = parse_conference_file(file_path)
            if not conference_data:
                logger.warning(f"跳过无效的会议文件: {file_path}")
                continue
            
            conference_name = conference_data.get('conference', 'Unknown')
            all_papers = conference_data.get('papers', [])
            
            # 过滤出新论文
            conference_sent_papers = set(sent_by_conference.get(conference_name, []))
            new_papers = [p for p in all_papers if p.get('id') not in sent_papers and p.get('id') not in conference_sent_papers]
            
            logger.info(f"{conference_name}: 总论文{len(all_papers)}篇，新论文{len(new_papers)}篇")
            
            if new_papers:
                # 发送订阅邮件
                success = send_conference_subscription_email(conference_data, new_papers, config)
                
                if success:
                    successful_sends += 1
                    total_new_papers += len(new_papers)
                    
                    # 更新历史记录
                    if conference_name not in sent_by_conference:
                        sent_by_conference[conference_name] = []
                    
                    for paper in new_papers:
                        paper_id = paper.get('id')
                        if paper_id:
                            sent_papers.add(paper_id)
                            sent_by_conference[conference_name].append(paper_id)
                    
                    logger.info(f"成功处理 {conference_name}: 发送{len(new_papers)}篇新论文")
                else:
                    logger.error(f"发送 {conference_name} 的邮件失败")
            else:
                logger.info(f"{conference_name}: 没有新论文需要发送")
                
        except Exception as e:
            logger.error(f"处理会议文件时发生错误 {file_path}: {str(e)}")
    
    # 保存更新的历史记录
    if total_new_papers > 0:
        subscription_history["sent_papers"] = list(sent_papers)
        subscription_history["sent_by_conference"] = sent_by_conference
        subscription_history["last_sent"] = datetime.now().isoformat()
        save_conference_subscription_history(subscription_history)
        
        logger.info(f"会议论文订阅完成: 成功发送{successful_sends}个会议的{total_new_papers}篇论文")
    else:
        logger.info("没有新的会议论文需要发送")
    
    return total_new_papers > 0

def run_conference_pipeline():
    """
    运行完整的会议论文流程：获取 + 订阅推送
    """
    logger.info("开始运行完整会议论文流程")
    
    # 第一步：获取会议论文
    fetch_results = run_conference_fetch()
    
    if not fetch_results:
        logger.info("会议论文获取失败，跳过订阅推送")
        return False
    
    # 第二步：处理订阅推送
    subscription_success = process_conference_subscription()
    
    return {
        'fetch_results': fetch_results,
        'subscription_success': subscription_success
    }

if __name__ == "__main__":
    # 可以选择运行完整流程或仅处理订阅
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--subscription-only':
        process_conference_subscription()
    else:
        run_conference_pipeline()
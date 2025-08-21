"""
arXiv RSS Filter Bot - RSS Feed Generator
arXiv RSS 过滤机器人 - RSS订阅源生成器

该模块负责将过滤后的论文转换为标准的RSS订阅源格式。
生成的RSS文件可以被各种RSS阅读器订阅，方便用户跟踪最新的相关论文。
"""

import logging  # 导入日志模块
import os  # 导入操作系统模块，用于文件和目录操作
from datetime import datetime, timezone  # 导入日期时间模块和时区模块
from feedgen.feed import FeedGenerator  # 导入RSS生成库
from email.utils import format_datetime

logger = logging.getLogger(__name__)  # 获取当前模块的日志记录器

def generate_rss(papers, output_file, title='arXiv RSS Filter Bot - Personalized Papers', description='Automatically filtered arXiv papers based on your research interests'):
    """
    从过滤后的论文生成RSS订阅源
    
    Args:
        papers (list): 处理后的论文字典列表
        output_file (str): 输出的RSS文件路径
        title (str): RSS订阅源的标题
        description (str): RSS订阅源的描述
        
    Returns:
        str: 生成的RSS文件路径
    
    Raises:
        Exception: RSS生成过程中出现的任何异常
    """
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)  # 如果目录不存在则创建
        
        # 创建Feed生成器
        fg = FeedGenerator()  # 初始化Feed生成器
        fg.title(title)  # 设置RSS标题
        fg.description(description)  # 设置RSS描述
        fg.link(href='https://arxiv.org')  # 设置RSS链接
        fg.language('en')  # 设置RSS语言
        
        # 为每篇论文添加条目
        for paper in papers:
            entry = fg.add_entry()  # 添加新条目
            entry.id(paper['entry_id'])  # 设置条目ID
            entry.title(paper['title'])  # 设置条目标题
            
            # 创建带有作者信息的格式化摘要
            authors_info = paper.get('authors_info', [])
            authors_text = ""
            if authors_info:
                authors_text = "Authors: "
                author_names = []
                for author in authors_info:
                    author_name = author.get('name', '')
                    author_names.append(author_name)
                authors_text += ", ".join(author_names) + "."
                
                # 添加机构信息
                institutions = []
                for author in authors_info:
                    if author.get('affiliation') and author.get('affiliation') not in institutions:
                        institutions.append(author.get('affiliation'))
                
                if institutions:
                    authors_text += "\nInstitutions: " + "; ".join(institutions) + "."
                
                authors_text += "\n\n"
            
            # 显示匹配的关键词（如果有）
            keywords_text = ""
            keyword_matches = paper.get('keyword_matches', [])
            if keyword_matches:
                keywords_text = f"Matched keywords: {', '.join(keyword_matches)}.\n\n"
            
            summary = f"""
Categories: {', '.join(paper['categories'])}

{keywords_text}{authors_text}{paper['summary']}
            """
            entry.summary(summary)  # 设置条目摘要
            
            # 添加论文链接
            entry.link(href=paper['entry_id'])  # 添加arXiv页面链接
            
            # 添加PDF链接
            entry.link(href=paper['pdf_url'], rel='alternate', type='application/pdf')  # 添加PDF下载链接
            
            # 添加发布日期（添加时区信息）
            if paper.get('published'):
                # 如果发布日期没有时区信息，添加UTC时区
                if paper['published'].tzinfo is None:
                    published_date = paper['published'].replace(tzinfo=timezone.utc)
                else:
                    published_date = paper['published']
                entry.published(published_date)  # 设置feedgen的published字段
                # 额外设置pubDate字段，确保前端能正确解析
                entry.pubDate(format_datetime(published_date))
                
            # 添加作者
            for author_info in authors_info:
                entry.author(name=author_info.get('name', ''))  # 添加作者信息
                
            # 添加类别作为标签
            for category in paper.get('categories', []):
                entry.category(term=category)  # 添加类别标签
                
        # 生成RSS文件
        fg.rss_file(output_file, pretty=True)  # 生成格式化的RSS XML文件
        logger.info(f"Generated RSS feed with {len(papers)} papers at {output_file}")  # 记录RSS生成成功
        
        return output_file  # 返回生成的RSS文件路径
        
    except Exception as e:  # 捕获所有可能的异常
        logger.error(f"Error generating RSS feed: {str(e)}", exc_info=True)  # 记录错误详情
        raise  # 重新抛出异常，让调用者处理 
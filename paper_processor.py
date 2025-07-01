"""
arXiv RSS Filter Bot - Paper processing module
arXiv RSS 过滤机器人 - 论文处理模块

该模块负责对从arXiv获取的论文进行处理，主要功能：
1. 关键词匹配：标题和摘要中包含关键词的检查
2. 时间过滤：根据论文的发布或更新时间进行过滤
3. 作者和机构信息提取：从论文数据中提取作者信息和所属机构
"""

import logging  # 导入日志模块
from datetime import datetime, timedelta, timezone  # 导入日期时间模块
import re  # 导入正则表达式模块，用于关键词匹配
import nltk
from nltk.stem import PorterStemmer

logger = logging.getLogger(__name__)  # 获取当前模块的日志记录器

# 确保nltk资源可用
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

ps = PorterStemmer()

def stem_text(text):
    # 只保留单词，全部小写，词干化
    return ' '.join([ps.stem(word) for word in re.findall(r'\w+', text.lower())])

def process_papers(papers, config):
    """
    根据关键词和时间过滤论文，并提取作者和机构信息
    
    Args:
        papers (list): 论文字典列表
        config (dict): 配置参数字典
        
    Returns:
        list: 处理后的论文列表，按日期降序排序
    
    Raises:
        Exception: 处理过程中出现的任何异常
    """
    try:
        # 从配置中获取参数
        keywords = config.get('keywords', [])  # 获取关键词列表
        max_days_old = config.get('max_days_old', 30)  # 最大天数，默认30天
        date_range = config.get('date_range', None)  # 日期范围，格式为 {'year': 2025, 'month': 5}
        
        logger.info(f"Processing {len(papers)} papers using {len(keywords)} keywords")  # 记录开始处理的信息
        if date_range:
            logger.info(f"Filtering papers by date range: {date_range}")
        processed_papers = []  # 存储处理后的论文
        
        # 获取当前时间，用于计算论文年龄
        now = datetime.now(timezone.utc)  # 当前时间，带UTC时区
        
        # 遍历每篇论文进行处理
        for paper in papers:
            # 检查论文是否包含关键词
            keyword_matches = check_keywords(paper, keywords)
            
            # 检查论文是否在指定时间范围内
            is_recent = check_recency(paper, now, max_days_old)
            
            # 检查论文是否在指定日期范围内
            is_in_date_range = True
            if date_range:
                is_in_date_range = check_date_range(paper, date_range)
            
            # 提取作者和机构信息
            authors_info = extract_author_info(paper)
            
            # 创建处理后的论文对象
            processed_paper = paper.copy()  # 复制论文字典，避免修改原始数据
            processed_paper['keyword_matches'] = keyword_matches  # 添加关键词匹配结果
            processed_paper['is_recent'] = is_recent  # 添加时间检查结果
            processed_paper['is_in_date_range'] = is_in_date_range  # 添加日期范围检查结果
            processed_paper['authors_info'] = authors_info  # 添加作者和机构信息
            
            # 只有同时满足关键词匹配、时间要求和日期范围要求的论文才被保留
            if (not keywords or keyword_matches) and is_recent and is_in_date_range:
                processed_papers.append(processed_paper)
        
        # 按发布日期降序排序论文（最新的在前）
        processed_papers.sort(key=lambda x: x.get('published', datetime.min), reverse=True)
        
        return processed_papers  # 返回处理后的论文列表
        
    except Exception as e:  # 捕获所有可能的异常
        logger.error(f"Error processing papers: {str(e)}", exc_info=True)  # 记录错误详情
        raise  # 重新抛出异常，让调用者处理

def check_keywords(paper, keywords):
    """
    检查论文是否包含关键词
    
    在标题和摘要中查找关键词，使用正则表达式确保匹配完整的单词。
    
    Args:
        paper (dict): 论文字典
        keywords (list): 关键词列表
        
    Returns:
        list: 匹配到的关键词列表
    """
    if not keywords:
        return []
    matches = []
    title = stem_text(paper['title'])
    summary = stem_text(paper['summary'])
    for keyword in keywords:
        keyword_stem = stem_text(keyword)
        # 只要词干化后短语出现在title或summary中就算匹配
        if keyword_stem in title or keyword_stem in summary:
            matches.append(keyword)
    return matches

def check_recency(paper, now, max_days_old):
    """
    检查论文是否在指定的时间范围内
    
    Args:
        paper (dict): 论文字典
        now (datetime): 当前时间
        max_days_old (int): 最大天数
        
    Returns:
        bool: 如果论文在指定时间范围内，返回True
    """
    # 获取发布日期和更新日期
    pub_date = paper.get('published')  # 获取发布日期
    update_date = paper.get('updated')  # 获取更新日期
    
    # 如果没有发布日期，返回False
    if not pub_date:
        logger.debug(f"Paper '{paper.get('title', '未知标题')}' has no publication date - Excluded")
        return False
    
    # 确保时间对象有时区信息
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    
    if pub_date.tzinfo is None:
        pub_date = pub_date.replace(tzinfo=timezone.utc)
    
    if update_date and update_date.tzinfo is None:
        update_date = update_date.replace(tzinfo=timezone.utc)
        
    # 使用发布日期或更新日期中较新的一个
    paper_date = update_date if update_date and update_date > pub_date else pub_date
    
    # 计算论文发布至今的天数
    days_old = (now - paper_date).days  # 计算天数差
    
    # 如果是未来日期，将天数视为0
    if days_old < 0:
        days_old = 0
    
    # 如果论文天数小于等于最大天数，则认为是最近的论文
    result = days_old <= max_days_old
    
    # 记录详细过滤结果，便于调试
    logger.info(f"Paper '{paper.get('title', '未知标题')}' is {days_old} days old (max: {max_days_old}) - {'Included' if result else 'Excluded'}")
    
    return result

def check_date_range(paper, date_range):
    """
    检查论文是否在指定的年月范围内
    
    Args:
        paper (dict): 论文字典
        date_range (dict): 日期范围，格式为 {'year': 2025, 'month': 5}
        
    Returns:
        bool: 如果论文在指定年月范围内，返回True
    """
    # 如果没有指定日期范围，返回True
    if not date_range:
        return True
    
    # 获取发布日期
    pub_date = paper.get('published')
    
    # 如果没有发布日期，返回False
    if not pub_date:
        logger.debug(f"Paper '{paper.get('title', '未知标题')}' has no publication date for date_range check - Excluded")
        return False
    
    # 提取年份和月份
    year = date_range.get('year')
    month = date_range.get('month')
    
    # 如果没有指定年份和月份，返回True
    if not year and not month:
        return True
    
    # 检查年份
    year_match = True
    if year and pub_date.year != year:
        year_match = False
    
    # 检查月份
    month_match = True
    if month and pub_date.month != month:
        month_match = False
    
    result = year_match and month_match
    
    # 添加详细日志
    if not result:
        logger.info(f"Paper '{paper.get('title', '未知标题')}' ({pub_date.year}-{pub_date.month}) doesn't match date range {date_range} - Excluded")
    else:
        logger.debug(f"Paper '{paper.get('title', '未知标题')}' ({pub_date.year}-{pub_date.month}) matches date range {date_range} - Included")
    
    return result

def extract_author_info(paper):
    """
    从论文中提取作者信息和所属机构
    
    Args:
        paper (dict): 论文字典
        
    Returns:
        list: 包含作者信息的字典列表
    """
    authors = paper.get('authors', [])  # 获取作者列表
    authors_info = []
    
    # 如果没有作者信息，返回空列表
    if not authors:
        return authors_info
    
    # 提取每位作者的信息
    for author in authors:
        # 在arxiv API返回中，作者可能是字符串或包含更多信息的对象
        if isinstance(author, dict):
            author_name = author.get('name', '')
            affiliation = author.get('affiliation', '')
        else:
            author_name = author
            affiliation = ''  # 如果API没有提供机构信息，设为空字符串
        
        # 添加到作者信息列表
        authors_info.append({
            'name': author_name,
            'affiliation': affiliation
        })
    
    return authors_info
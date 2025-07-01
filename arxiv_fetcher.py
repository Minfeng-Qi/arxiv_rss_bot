"""
arXiv RSS Filter Bot - Papers fetcher from arXiv API
arXiv RSS 过滤机器人 - 从arXiv API获取论文

该模块负责通过arXiv API获取最新的学术论文。
可以根据配置获取特定类别的论文，默认获取计算机科学领域的论文。
"""

import arxiv  # 导入arXiv API客户端库
import logging  # 导入日志模块
from datetime import datetime, timedelta  # 导入日期时间模块
import requests  # 导入请求库，用于发送HTTP请求
import feedparser  # 导入Feed解析库，用于解析arXiv API的返回结果
import urllib.parse  # 导入URL解析库，用于构建查询URL
import time  # 导入时间模块

logger = logging.getLogger(__name__)  # 获取当前模块的日志记录器

# 默认的计算机科学类别
DEFAULT_CATEGORY = "cs"  # cs代表计算机科学(Computer Science)

def fetch_latest_papers(config):
    """
    从arXiv获取最新论文
    
    Args:
        config (dict): 包含以下键的配置字典:
            - categories: 要获取的arXiv类别列表
            - max_results: 要获取的最大论文数量
            
    Returns:
        list: 论文字典列表，每个字典包含论文的详细信息
    """
    try:
        # 从配置中提取参数
        categories = config.get('categories', ['cs.AI'])  # 默认为人工智能类别
        max_results = config.get('max_results', 100)  # 默认获取100篇论文
        max_days_old = config.get('max_days_old', 30)  # 默认只获取30天内的论文
        
        logger.info(f"Fetching papers from arXiv for categories: {', '.join(categories)}")
        logger.info(f"Max results: {max_results}, Max days old: {max_days_old}")
        
        # 方法1: 直接使用arxiv库
        try:
            return _fetch_via_arxiv_lib(categories, max_results, max_days_old)
        except Exception as e:
            logger.warning(f"使用arxiv库获取失败，尝试备用方法: {str(e)}")
            # 如果arxiv库失败，使用备用方法
            return _fetch_via_feedparser(categories, max_results, max_days_old)
            
    except Exception as e:  # 捕获所有可能的异常
        logger.error(f"Error fetching papers from arXiv: {str(e)}", exc_info=True)  # 记录错误详情
        raise  # 重新抛出异常，让调用者处理

def _fetch_via_arxiv_lib(categories, max_results, max_days_old=30):
    """使用arxiv库获取论文"""
    # 创建类别查询字符串
    search_query = " OR ".join([f"cat:{cat}" for cat in categories])  # 构建类别查询，例如："cat:cs.AI OR cat:cs.LG"
    
    # 根据max_days_old增加获取数量，确保有足够的论文可以过滤
    # 每个类别每天估计10篇论文，乘以类别数和天数，再加上冗余
    # 增加系数，以获取更多历史论文
    papers_per_day_per_category = 20  # 增加每类别每天的估计论文数
    actual_max_results = min(10000, max(max_results, max_days_old * len(categories) * papers_per_day_per_category))
    logger.info(f"Increasing fetch limit to {actual_max_results} to ensure coverage for {max_days_old} days")
    
    # 设置客户端
    client = arxiv.Client(
        page_size=100,  # 每页100篇论文
        delay_seconds=3.0,  # API请求之间延迟3秒，避免过于频繁请求
        num_retries=5  # 失败时最多重试5次
    )
    
    # 创建搜索对象
    search = arxiv.Search(
        query=search_query,  # 使用构建的类别查询
        max_results=actual_max_results,  # 设置增加后的最大结果数
        sort_by=arxiv.SortCriterion.SubmittedDate,  # 按提交日期排序
        sort_order=arxiv.SortOrder.Descending  # 降序排序，最新的论文排在前面
    )
    
    # 执行查询并获取结果
    results = list(client.results(search))
    logger.info(f"Successfully fetched {len(results)} papers from arXiv using arxiv library")
    
    # 转换为标准格式
    papers = []
    for paper in results:
        papers.append({
            'id': paper.entry_id.split('/')[-1],  # 提取论文ID
            'title': paper.title,  # 论文标题
            'authors': [author.name for author in paper.authors],  # 作者列表
            'summary': paper.summary,  # 论文摘要
            'published': paper.published,  # 发布时间
            'updated': paper.updated,  # 更新时间
            'pdf_url': paper.pdf_url,  # PDF下载链接
            'entry_id': paper.entry_id,  # 完整的条目ID
            'categories': paper.categories,  # 论文所属类别
            'primary_category': paper.primary_category,  # 主要类别
        })
    
    return papers

def _fetch_via_feedparser(categories, max_results, max_days_old=30):
    """使用feedparser直接获取arXiv API结果"""
    # 构建arXiv API URL
    base_url = 'https://export.arxiv.org/api/query?'
    
    # 根据max_days_old增加获取数量
    papers_per_day_per_category = 20  # 增加每类别每天的估计论文数
    actual_max_results = min(10000, max(max_results, max_days_old * len(categories) * papers_per_day_per_category))
    logger.info(f"Increasing fetch limit to {actual_max_results} to ensure coverage for {max_days_old} days")
    
    # 构建查询参数
    search_query = " OR ".join([f"cat:{cat}" for cat in categories])
    
    # 如果max_days_old很大，考虑使用分批查询
    if max_days_old > 90:
        return _fetch_in_batches(categories, actual_max_results, max_days_old)
    
    all_papers = []
    page_size = 100  # arXiv API每次请求最大返回数量
    
    # 分页请求数据，避免单次请求数据过多
    for start in range(0, actual_max_results, page_size):
        try:
            # 如果已经获取足够的论文，停止请求
            if len(all_papers) >= actual_max_results:
                break
                
            # 构建本次请求的参数
            params = {
                'search_query': search_query,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending',
                'start': start,
                'max_results': min(page_size, actual_max_results - start)
            }
            
            # 构建完整的URL
            url = base_url + urllib.parse.urlencode(params)
            logger.info(f"Requesting arXiv API: {url}")
            
            # 发送HTTP请求，带重试机制
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    break
                except (requests.RequestException, requests.Timeout) as e:
                    retry_count += 1
                    wait_time = 2 ** retry_count  # 指数退避
                    logger.warning(f"Request failed (attempt {retry_count}/{max_retries}): {str(e)}. Retrying in {wait_time}s...")
                    if retry_count >= max_retries:
                        logger.error(f"Failed to fetch from arXiv after {max_retries} attempts: {str(e)}")
                        raise
                    time.sleep(wait_time)
            
            # 解析返回的Feed
            feed = feedparser.parse(response.content)
            
            # 检查是否有条目返回
            if not feed.entries:
                logger.warning(f"No entries returned for request starting at {start}")
                # 如果是第一个请求就没有结果，可能是查询有问题
                if start == 0:
                    logger.error("First page returned no results, check query parameters")
                    break
                else:
                    # 可能已经获取完所有可用论文
                    logger.info("No more entries available, stopping pagination")
                    break
            
            # 处理返回的条目
            for entry in feed.entries:
                # 提取作者信息
                authors = [author.get('name', '') for author in entry.get('authors', [])]
                
                # 提取分类信息
                categories = [tag.get('term', '') for tag in entry.get('tags', [])]
                
                # 提取日期
                published = None
                updated = None
                try:
                    if 'published' in entry:
                        published = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ")
                    if 'updated' in entry:
                        updated = datetime.strptime(entry.updated, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError as e:
                    logger.warning(f"Date parsing error for entry {entry.id}: {e}")
                    # 使用当前时间作为后备
                    if not published:
                        published = datetime.now()
                    if not updated:
                        updated = published
                
                # 构建论文对象
                paper = {
                    'id': entry.id.split('/')[-1],
                    'title': entry.title,
                    'authors': authors,
                    'summary': entry.summary if 'summary' in entry else '',
                    'published': published,
                    'updated': updated,
                    'pdf_url': f"https://arxiv.org/pdf/{entry.id.split('/')[-1]}.pdf",
                    'entry_id': entry.id,
                    'categories': categories,
                    'primary_category': categories[0] if categories else None,
                }
                
                all_papers.append(paper)
            
            # API限速，避免请求过快
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"Error fetching papers from arXiv at offset {start}: {str(e)}")
            # 继续尝试下一个分页，而不是完全中断
            time.sleep(5)  # 出错后等待更长时间再重试
    
    logger.info(f"Successfully fetched {len(all_papers)} papers from arXiv using feedparser")
    return all_papers

def _fetch_in_batches(categories, max_results, max_days_old):
    """
    分批获取论文，适用于获取较长时间范围的论文
    
    Args:
        categories (list): 要获取的arXiv类别列表
        max_results (int): 要获取的最大论文数量
        max_days_old (int): 最大天数
        
    Returns:
        list: 论文字典列表
    """
    logger.info(f"Using batch fetching for {max_days_old} days")
    all_papers = []
    
    # 计算每批的天数，避免一次获取太多
    batch_days = 90  # 每批90天
    num_batches = (max_days_old + batch_days - 1) // batch_days  # 向上取整
    
    # 每批获取的论文数量
    batch_max_results = max(100, max_results // num_batches)
    
    # 构建arXiv API URL
    base_url = 'https://export.arxiv.org/api/query?'
    
    # 构建基本查询参数
    search_query_base = " OR ".join([f"cat:{cat}" for cat in categories])
    
    # 分批获取
    now = datetime.now()
    for batch in range(num_batches):
        # 计算当前批次的日期范围
        end_date = now - timedelta(days=batch * batch_days)
        start_date = now - timedelta(days=min(max_days_old, (batch + 1) * batch_days))
        
        logger.info(f"Fetching batch {batch+1}/{num_batches}: {start_date.date()} to {end_date.date()}")
        
        # 构建日期范围查询
        date_query = f" AND submittedDate:[{start_date.strftime('%Y%m%d')}000000 TO {end_date.strftime('%Y%m%d')}235959]"
        search_query = search_query_base + date_query
        
        # 获取当前批次的论文
        batch_papers = []
        page_size = 100
        
        # 分页请求数据
        for start in range(0, batch_max_results, page_size):
            try:
                # 如果已经获取足够的论文，停止请求
                if len(batch_papers) >= batch_max_results:
                    break
                    
                # 构建本次请求的参数
                params = {
                    'search_query': search_query,
                    'sortBy': 'submittedDate',
                    'sortOrder': 'descending',
                    'start': start,
                    'max_results': min(page_size, batch_max_results - start)
                }
                
                # 构建完整的URL
                url = base_url + urllib.parse.urlencode(params)
                logger.info(f"Requesting arXiv API for batch {batch+1}: {url}")
                
                # 发送HTTP请求，带重试机制
                max_retries = 3
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        response = requests.get(url, timeout=30)
                        response.raise_for_status()
                        break
                    except (requests.RequestException, requests.Timeout) as e:
                        retry_count += 1
                        wait_time = 2 ** retry_count  # 指数退避
                        logger.warning(f"Request failed (attempt {retry_count}/{max_retries}): {str(e)}. Retrying in {wait_time}s...")
                        if retry_count >= max_retries:
                            logger.error(f"Failed to fetch from arXiv after {max_retries} attempts: {str(e)}")
                            raise
                        time.sleep(wait_time)
                
                # 解析返回的Feed
                feed = feedparser.parse(response.content)
                
                # 检查是否有条目返回
                if not feed.entries:
                    logger.warning(f"No entries returned for batch {batch+1} request starting at {start}")
                    break
                
                # 处理返回的条目
                for entry in feed.entries:
                    # 提取作者信息
                    authors = [author.get('name', '') for author in entry.get('authors', [])]
                    
                    # 提取分类信息
                    categories = [tag.get('term', '') for tag in entry.get('tags', [])]
                    
                    # 提取日期
                    published = None
                    updated = None
                    try:
                        if 'published' in entry:
                            published = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ")
                        if 'updated' in entry:
                            updated = datetime.strptime(entry.updated, "%Y-%m-%dT%H:%M:%SZ")
                    except ValueError as e:
                        logger.warning(f"Date parsing error for entry {entry.id}: {e}")
                        # 使用当前时间作为后备
                        if not published:
                            published = datetime.now()
                        if not updated:
                            updated = published
                    
                    # 构建论文对象
                    paper = {
                        'id': entry.id.split('/')[-1],
                        'title': entry.title,
                        'authors': authors,
                        'summary': entry.summary if 'summary' in entry else '',
                        'published': published,
                        'updated': updated,
                        'pdf_url': f"https://arxiv.org/pdf/{entry.id.split('/')[-1]}.pdf",
                        'entry_id': entry.id,
                        'categories': categories,
                        'primary_category': categories[0] if categories else None,
                    }
                    
                    batch_papers.append(paper)
                
                # API限速，避免请求过快
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Error fetching papers for batch {batch+1} at offset {start}: {str(e)}")
                time.sleep(5)  # 出错后等待更长时间再重试
        
        logger.info(f"Fetched {len(batch_papers)} papers for batch {batch+1}")
        all_papers.extend(batch_papers)
        
        # 如果已经获取足够的论文，停止请求
        if len(all_papers) >= max_results:
            logger.info(f"Reached maximum results limit ({max_results}), stopping batch fetching")
            break
    
    logger.info(f"Successfully fetched {len(all_papers)} papers from arXiv using batch fetching")
    return all_papers 
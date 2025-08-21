#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OpenReview Conference Paper Fetcher
OpenReview会议论文获取模块

该模块负责从OpenReview获取顶级AI和安全会议的论文信息
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List
from config_loader import load_config

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 定义目录路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFERENCE_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "conference_output")
CONFERENCE_HISTORY_DIR = os.path.join(SCRIPT_DIR, "conference_history")

# 确保目录存在
os.makedirs(CONFERENCE_OUTPUT_DIR, exist_ok=True)
os.makedirs(CONFERENCE_HISTORY_DIR, exist_ok=True)

class OpenReviewClient:
    """OpenReview API 客户端"""
    
    def __init__(self, baseurl: str = "https://api2.openreview.net", username: str = None, password: str = None):
        self.baseurl = baseurl.rstrip('/')
        self.username = username
        self.password = password
        self.token = None
        self.headers = {
            'User-Agent': 'arXiv-RSS-Bot-Conference-Fetcher/1.0',
            'Content-Type': 'application/json'
        }
        
        if username and password:
            self._authenticate()
    
    def _authenticate(self):
        """认证获取token"""
        try:
            auth_data = {
                'id': self.username,
                'password': self.password
            }
            
            response = requests.post(
                f"{self.baseurl}/login",
                json=auth_data,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                self.token = response.json().get('token')
                if self.token:
                    self.headers['Authorization'] = f'Bearer {self.token}'
                    logger.info("OpenReview认证成功")
                else:
                    logger.error("认证响应中未找到token")
            else:
                logger.error(f"认证失败: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"认证过程中发生错误: {str(e)}")
    
    def get_notes(self, venue_id: str, content_filter: Dict = None, limit: int = 1000) -> List[Dict]:
        """获取会议论文"""
        try:
            params = {
                'limit': limit,
                'offset': 0
            }
            
            # 构建查询参数
            if content_filter:
                for key, value in content_filter.items():
                    params[f'content.{key}'] = value
            else:
                # 默认查询被接收的论文
                params['content.venueid'] = venue_id
            
            response = requests.get(
                f"{self.baseurl}/notes",
                params=params,
                headers=self.headers,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get('notes', [])
                logger.info(f"成功获取{len(notes)}篇论文来自{venue_id}")
                return notes
            else:
                logger.error(f"获取论文失败: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"获取论文时发生错误: {str(e)}")
            return []
    
    def get_venue_info(self, venue_id: str) -> Dict:
        """获取会议信息"""
        try:
            response = requests.get(
                f"{self.baseurl}/groups",
                params={'id': venue_id},
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                groups = data.get('groups', [])
                if groups:
                    return groups[0]
            return {}
        except Exception as e:
            logger.error(f"获取会议信息时发生错误: {str(e)}")
            return {}

class ConferencePaperProcessor:
    """会议论文处理器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """初始化OpenReview客户端"""
        openreview_config = self.config.get('openreview', {})
        baseurl = openreview_config.get('baseurl', 'https://api2.openreview.net')
        username = openreview_config.get('username')
        password = openreview_config.get('password')
        
        self.client = OpenReviewClient(baseurl, username, password)
    
    def filter_papers_by_keywords(self, papers: List[Dict], keywords: List[str]) -> List[Dict]:
        """根据关键词过滤论文"""
        if not keywords:
            return papers
        
        filtered_papers = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        for paper in papers:
            content = paper.get('content', {})
            title = content.get('title', {}).get('value', '') if isinstance(content.get('title'), dict) else content.get('title', '')
            abstract = content.get('abstract', {}).get('value', '') if isinstance(content.get('abstract'), dict) else content.get('abstract', '')
            
            # 合并标题和摘要进行匹配
            text_content = f"{title} {abstract}".lower()
            
            # 检查是否匹配任何关键词
            matched_keywords = [kw for kw in keywords_lower if kw in text_content]
            if matched_keywords:
                paper['matched_keywords'] = matched_keywords
                filtered_papers.append(paper)
        
        logger.info(f"关键词过滤后剩余{len(filtered_papers)}篇论文")
        return filtered_papers
    
    def format_paper_data(self, paper: Dict, conference_name: str) -> Dict:
        """格式化论文数据"""
        content = paper.get('content', {})
        
        # 提取基本信息
        title = content.get('title', {}).get('value', '') if isinstance(content.get('title'), dict) else content.get('title', '')
        abstract = content.get('abstract', {}).get('value', '') if isinstance(content.get('abstract'), dict) else content.get('abstract', '')
        authors = content.get('authors', {}).get('value', []) if isinstance(content.get('authors'), dict) else content.get('authors', [])
        
        # 构造OpenReview链接
        paper_id = paper.get('id', '')
        openreview_url = f"https://openreview.net/forum?id={paper_id}" if paper_id else ""
        
        formatted_paper = {
            'id': paper_id,
            'title': title,
            'abstract': abstract,
            'authors': authors if isinstance(authors, list) else [],
            'conference': conference_name,
            'venue_id': content.get('venueid', {}).get('value', '') if isinstance(content.get('venueid'), dict) else content.get('venueid', ''),
            'url': openreview_url,
            'cdate': paper.get('cdate', 0),
            'mdate': paper.get('mdate', 0),
            'matched_keywords': paper.get('matched_keywords', []),
            'fetched_at': datetime.now().isoformat()
        }
        
        return formatted_paper
    
    def save_conference_papers(self, papers: List[Dict], conference_name: str) -> str:
        """保存会议论文到文件"""
        if not papers:
            logger.info("没有论文需要保存")
            return None
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{conference_name.lower().replace(' ', '_')}_papers_{timestamp}.json"
        filepath = os.path.join(CONFERENCE_OUTPUT_DIR, filename)
        
        # 保存数据
        output_data = {
            'conference': conference_name,
            'papers_count': len(papers),
            'timestamp': datetime.now().isoformat(),
            'papers': papers
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"成功保存{len(papers)}篇论文到{filepath}")
            return filepath
        except Exception as e:
            logger.error(f"保存论文文件失败: {str(e)}")
            return None
    
    def fetch_conference_papers(self, conference_config: Dict) -> List[Dict]:
        """获取特定会议的论文"""
        conference_name = conference_config.get('name', '')
        venue_id = conference_config.get('venue_id', '')
        keywords = conference_config.get('keywords', [])
        
        logger.info(f"开始获取{conference_name}的论文")
        
        if not venue_id:
            logger.error(f"{conference_name}缺少venue_id配置")
            return []
        
        # 获取论文
        raw_papers = self.client.get_notes(venue_id)
        if not raw_papers:
            logger.info(f"{conference_name}没有找到论文")
            return []
        
        # 关键词过滤
        if keywords:
            filtered_papers = self.filter_papers_by_keywords(raw_papers, keywords)
        else:
            filtered_papers = raw_papers
        
        # 格式化数据
        formatted_papers = [
            self.format_paper_data(paper, conference_name) 
            for paper in filtered_papers
        ]
        
        return formatted_papers

def load_conference_history(conference_name: str) -> Dict:
    """加载会议历史记录"""
    history_file = os.path.join(CONFERENCE_HISTORY_DIR, f"{conference_name.lower().replace(' ', '_')}_history.json")
    
    if not os.path.exists(history_file):
        return {"fetched_papers": [], "last_fetch": None}
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载会议历史记录失败: {str(e)}")
        return {"fetched_papers": [], "last_fetch": None}

def save_conference_history(conference_name: str, history: Dict):
    """保存会议历史记录"""
    history_file = os.path.join(CONFERENCE_HISTORY_DIR, f"{conference_name.lower().replace(' ', '_')}_history.json")
    
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        logger.info(f"{conference_name}历史记录已保存")
    except Exception as e:
        logger.error(f"保存会议历史记录失败: {str(e)}")

def run_conference_fetch():
    """运行会议论文获取"""
    logger.info("开始运行会议论文获取")
    
    # 加载配置
    config = load_config()
    conferences_config = config.get('conferences', {})
    
    if not conferences_config.get('enabled', False):
        logger.info("会议论文获取功能未启用")
        return False
    
    # 初始化处理器
    processor = ConferencePaperProcessor(config)
    
    # 获取会议列表
    conference_list = conferences_config.get('conference_list', [])
    if not conference_list:
        logger.info("没有配置会议列表")
        return False
    
    results = {}
    
    for conference_config in conference_list:
        conference_name = conference_config.get('name', '')
        
        try:
            # 获取论文
            papers = processor.fetch_conference_papers(conference_config)
            
            if papers:
                # 保存论文文件
                output_file = processor.save_conference_papers(papers, conference_name)
                
                if output_file:
                    # 更新历史记录
                    history = load_conference_history(conference_name)
                    
                    # 添加新的论文ID到历史记录
                    fetched_paper_ids = set(history.get("fetched_papers", []))
                    new_papers = [p for p in papers if p['id'] not in fetched_paper_ids]
                    
                    if new_papers:
                        for paper in new_papers:
                            fetched_paper_ids.add(paper['id'])
                        
                        history["fetched_papers"] = list(fetched_paper_ids)
                        history["last_fetch"] = datetime.now().isoformat()
                        save_conference_history(conference_name, history)
                        
                        logger.info(f"{conference_name}: 发现{len(new_papers)}篇新论文")
                    else:
                        logger.info(f"{conference_name}: 没有新论文")
                    
                    results[conference_name] = {
                        'success': True,
                        'papers_count': len(papers),
                        'new_papers_count': len(new_papers) if 'new_papers' in locals() else 0,
                        'output_file': output_file
                    }
            else:
                results[conference_name] = {
                    'success': False,
                    'error': '没有找到匹配的论文'
                }
        
        except Exception as e:
            logger.error(f"处理{conference_name}时发生错误: {str(e)}")
            results[conference_name] = {
                'success': False,
                'error': str(e)
            }
    
    logger.info("会议论文获取完成")
    return results

if __name__ == "__main__":
    run_conference_fetch()
#!/usr/bin/env python3
"""
测试Google Scholar API集成
"""

import logging
import sys
import json
from datetime import datetime
from scholar_api import get_author_info, get_author_hindex, clean_expired_cache

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def test_known_authors():
    """测试知名作者的h-index获取"""
    logger.info("测试知名作者的h-index获取")
    
    known_authors = [
        "Geoffrey Hinton",
        "Yoshua Bengio",
        "Yann LeCun",
        "Andrew Ng",
        "Ian Goodfellow",
        "Fei-Fei Li",
        "Christopher Manning"
    ]
    
    results = {}
    
    for author in known_authors:
        try:
            logger.info(f"获取作者 {author} 的信息...")
            info = get_author_info(author)
            h_index = info['h_index']
            citations = info['citations']
            
            logger.info(f"作者: {author}, h-index: {h_index}, 引用数: {citations}")
            
            results[author] = {
                'h_index': h_index,
                'citations': citations,
                'interests': info.get('interests', []),
                'affiliation': info.get('affiliation', '')
            }
            
        except Exception as e:
            logger.error(f"获取作者 {author} 信息时出错: {str(e)}")
            results[author] = {'error': str(e)}
    
    return results

def test_random_authors():
    """测试随机作者的h-index获取（可能是未知作者）"""
    logger.info("测试随机作者的h-index获取")
    
    random_authors = [
        "John Smith AI Researcher",
        "Jane Doe Computer Science",
        "Alice Johnson Machine Learning",
        "Bob Williams Neural Networks",
        "Carol Brown Deep Learning"
    ]
    
    results = {}
    
    for author in random_authors:
        try:
            logger.info(f"获取作者 {author} 的信息...")
            info = get_author_info(author)
            h_index = info['h_index']
            citations = info['citations']
            
            logger.info(f"作者: {author}, h-index: {h_index}, 引用数: {citations}")
            
            results[author] = {
                'h_index': h_index,
                'citations': citations,
                'interests': info.get('interests', []),
                'affiliation': info.get('affiliation', '')
            }
            
        except Exception as e:
            logger.error(f"获取作者 {author} 信息时出错: {str(e)}")
            results[author] = {'error': str(e)}
    
    return results

def test_paper_authors():
    """测试论文作者的h-index获取"""
    logger.info("测试论文作者的h-index获取")
    
    # 模拟一些论文的作者列表
    papers = [
        {
            'id': 'paper1',
            'title': 'Deep Learning Advances',
            'authors': ['Geoffrey Hinton', 'Yoshua Bengio', 'Yann LeCun']
        },
        {
            'id': 'paper2',
            'title': 'Reinforcement Learning',
            'authors': ['Andrew Ng', 'John Smith AI Researcher']
        },
        {
            'id': 'paper3',
            'title': 'Computer Vision',
            'authors': ['Fei-Fei Li', 'Ian Goodfellow']
        }
    ]
    
    results = {}
    
    for paper in papers:
        paper_id = paper['id']
        paper_title = paper['title']
        authors = paper['authors']
        
        logger.info(f"论文: {paper_title}")
        paper_results = []
        
        for author in authors:
            try:
                h_index = get_author_hindex(author)
                logger.info(f"  作者: {author}, h-index: {h_index}")
                paper_results.append({
                    'name': author,
                    'h_index': h_index
                })
            except Exception as e:
                logger.error(f"  获取作者 {author} 的h-index时出错: {str(e)}")
                paper_results.append({
                    'name': author,
                    'error': str(e)
                })
        
        results[paper_id] = {
            'title': paper_title,
            'authors': paper_results
        }
    
    return results

def main():
    """主函数"""
    logger.info("开始测试Google Scholar API")
    
    # 清理过期缓存
    clean_expired_cache()
    
    # 测试结果
    results = {
        'timestamp': datetime.now().isoformat(),
        'known_authors': test_known_authors(),
        'random_authors': test_random_authors(),
        'paper_authors': test_paper_authors()
    }
    
    # 保存测试结果
    try:
        with open('test_scholar_api_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info("测试结果已保存到 test_scholar_api_results.json")
    except Exception as e:
        logger.error(f"保存测试结果时出错: {str(e)}")
    
    logger.info("Google Scholar API 测试完成")

if __name__ == "__main__":
    main()
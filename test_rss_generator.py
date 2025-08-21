#!/usr/bin/env python3
"""
arXiv RSS Filter Bot - RSS生成测试脚本
用于测试 rss_generator.py 的RSS生成功能是否正常
"""

import logging
import os
import sys
import yaml
from datetime import datetime, timezone
import json

# 导入需要测试的模块
from rss_generator import generate_rss

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_rss_generator')

def load_test_config():
    """加载测试配置"""
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        logger.error(f"加载配置文件出错: {str(e)}")
        # 创建一个默认测试配置
        return {
            'rss_title': 'arXiv RSS Filter Bot Test Feed',
            'rss_description': 'Test feed from arXiv RSS Filter Bot',
            'output_dir': './output'
        }

def create_test_papers():
    """创建测试用的论文数据"""
    # 当前时间（带时区信息）
    now = datetime.now(timezone.utc)
    
    # 从测试结果文件加载论文数据（如果存在）
    test_result_file = 'test_scorer_result.json'
    if os.path.exists(test_result_file):
        try:
            with open(test_result_file, 'r', encoding='utf-8') as f:
                papers_data = json.load(f)
                
            # 将字符串日期转回日期对象
            for paper in papers_data:
                if 'published' in paper and paper['published']:
                    paper['published'] = datetime.fromisoformat(paper['published'])
                if 'updated' in paper and paper['updated']:
                    paper['updated'] = datetime.fromisoformat(paper['updated'])
                    
            logger.info(f"从 {test_result_file} 加载了 {len(papers_data)} 篇测试论文")
            return papers_data
        except Exception as e:
            logger.error(f"加载测试结果文件出错: {str(e)}")
    
    # 如果无法从文件加载，则创建测试数据
    logger.info("创建新的测试论文数据")
    papers = [
        {
            'id': 'test1',
            'title': 'Advanced Reinforcement Learning for Language Agent Systems',
            'authors': ['Alice Smith', 'Bob Johnson', 'Carol White'],
            'summary': 'This paper discusses reinforcement learning techniques applied to language agents.',
            'published': now,
            'updated': None,
            'categories': ['cs.AI', 'cs.LG'],
            'primary_category': 'cs.AI',
            'entry_id': 'http://arxiv.org/abs/test1',
            'pdf_url': 'http://arxiv.org/pdf/test1.pdf',
            'score': 3.15,
            'keyword_score': 2.5,
            'recency_score': 1.0,
            'author_score': 0.3
        },
        {
            'id': 'test2',
            'title': 'Neural Networks in Computer Vision',
            'authors': ['David Brown'],
            'summary': 'A study on neural networks for computer vision tasks without agent technology.',
            'published': now,
            'updated': None,
            'categories': ['cs.CV'],
            'primary_category': 'cs.CV',
            'entry_id': 'http://arxiv.org/abs/test2',
            'pdf_url': 'http://arxiv.org/pdf/test2.pdf',
            'score': 0.8,
            'keyword_score': 0.5,
            'recency_score': 0.5,
            'author_score': 0.1
        }
    ]
    return papers

def run_test():
    """运行测试"""
    logger.info("开始测试RSS生成功能")
    
    try:
        # 加载测试配置
        config = load_test_config()
        logger.info(f"测试配置: RSS标题='{config.get('rss_title', 'Test Feed')}'")
        
        # 确保输出目录存在
        output_dir = config.get('output_dir', './output')
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"输出目录: {output_dir}")
        
        # 创建测试论文
        papers = create_test_papers()
        
        # 应用分数阈值过滤
        score_threshold = config.get('score_threshold', 1.0)
        filtered_papers = [p for p in papers if p['score'] >= score_threshold]
        logger.info(f"应用分数阈值 {score_threshold}，过滤后剩余 {len(filtered_papers)}/{len(papers)} 篇论文")
        
        # 生成RSS
        output_file = os.path.join(output_dir, 'test_arxiv_filtered.xml')
        rss_url = generate_rss(
            filtered_papers, 
            output_file,
            config.get('rss_title', 'arXiv RSS Filter Bot Test Feed'),
            config.get('rss_description', 'Test feed from arXiv RSS Filter Bot')
        )
        
        logger.info(f"RSS生成成功，保存到: {output_file}")
        logger.info(f"RSS URL: {rss_url}")
        
        # 检查文件是否存在
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            logger.info(f"RSS文件大小: {file_size} 字节")
            
            # 读取文件内容前100行进行预览
            with open(output_file, 'r', encoding='utf-8') as f:
                preview_lines = [f.readline() for _ in range(20)]
            
            print("\nRSS文件内容预览 (前20行):")
            print("="*80)
            print(''.join(preview_lines))
            print("="*80)
            print(f"\n完整的RSS文件可在 {output_file} 查看")
            
            return True
        else:
            logger.error(f"RSS文件生成失败，文件不存在: {output_file}")
            return False
        
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1) 
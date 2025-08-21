#!/usr/bin/env python3
"""
arXiv RSS Filter Bot - 论文获取测试脚本
用于测试 arxiv_fetcher.py 的功能是否正常
"""

import logging
import yaml
import json
from datetime import datetime

# 导入论文获取模块
from arxiv_fetcher import fetch_latest_papers

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_fetcher')

def load_test_config():
    """加载测试配置"""
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            
        # 为了测试目的，减少获取的论文数量
        test_config = config.copy()
        test_config['max_results'] = 5  # 只获取5篇论文进行测试
        
        return test_config
    except Exception as e:
        logger.error(f"加载配置文件出错: {str(e)}")
        # 创建一个默认测试配置
        return {
            'max_results': 5,
            'categories': ['cs.AI', 'cs.LG']  # AI和机器学习类别
        }

def print_paper_details(paper):
    """打印论文详情"""
    print(f"\n{'='*80}")
    print(f"标题: {paper['title']}")
    print(f"作者: {', '.join(paper['authors'])}")
    print(f"发布时间: {paper['published'].strftime('%Y-%m-%d')}")
    print(f"类别: {', '.join(paper['categories'])}")
    print(f"摘要: {paper['summary'][:200]}...")  # 只显示摘要的前200个字符
    print(f"链接: {paper['entry_id']}")
    print(f"PDF: {paper['pdf_url']}")
    print(f"{'='*80}\n")

def run_test():
    """运行测试"""
    logger.info("开始测试 arXiv 论文获取功能")
    
    # 加载测试配置
    config = load_test_config()
    logger.info(f"测试配置: 最大结果数={config['max_results']}, 类别={config.get('categories', ['cs'])}")
    
    try:
        # 获取论文
        start_time = datetime.now()
        papers = fetch_latest_papers(config)
        end_time = datetime.now()
        
        # 计算获取时间
        fetch_time = (end_time - start_time).total_seconds()
        
        if not papers:
            logger.warning("未获取到任何论文")
            return
            
        logger.info(f"成功获取 {len(papers)} 篇论文，用时 {fetch_time:.2f} 秒")
        
        # 打印部分论文信息
        for i, paper in enumerate(papers[:3]):  # 只显示前3篇
            print_paper_details(paper)
            
        # 保存测试结果到文件
        with open('test_fetcher_result.json', 'w', encoding='utf-8') as f:
            # 转换datetime对象为字符串，避免JSON序列化错误
            serializable_papers = []
            for paper in papers:
                paper_copy = paper.copy()
                if 'published' in paper_copy:
                    paper_copy['published'] = paper_copy['published'].isoformat()
                if 'updated' in paper_copy:
                    paper_copy['updated'] = paper_copy['updated'].isoformat()
                serializable_papers.append(paper_copy)
                
            json.dump(serializable_papers, f, indent=2, ensure_ascii=False)
            
        logger.info(f"测试结果已保存到 test_fetcher_result.json")
        
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}", exc_info=True)
        
if __name__ == "__main__":
    run_test() 
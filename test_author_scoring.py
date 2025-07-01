#!/usr/bin/env python3
"""
arXiv RSS Filter Bot - 作者评分测试脚本
用于测试基于h-index的作者评分功能
"""

import logging
import sys
from paper_scorer import get_author_hindex, calculate_author_score

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_author_scoring')

def test_author_hindex():
    """测试作者h-index获取功能"""
    logger.info("测试作者h-index获取功能")
    
    # 测试知名作者
    known_authors = [
        "Geoffrey Hinton",
        "Yoshua Bengio",
        "Yann LeCun",
        "Andrew Ng",
        "Ian Goodfellow"
    ]
    
    logger.info("测试知名作者的h-index:")
    for author in known_authors:
        h_index = get_author_hindex(author)
        logger.info(f"  {author}: h-index = {h_index}")
    
    # 测试随机作者
    random_authors = [
        "John Smith",
        "Jane Doe",
        "Alice Johnson",
        "Bob Williams",
        "Carol Brown"
    ]
    
    logger.info("\n测试随机作者的h-index:")
    for author in random_authors:
        h_index = get_author_hindex(author)
        logger.info(f"  {author}: h-index = {h_index}")
    
    return True

def test_author_scoring():
    """测试作者评分功能"""
    logger.info("\n测试作者评分功能")
    
    # 创建测试论文
    test_papers = [
        {
            'title': '高影响力单作者论文',
            'authors': ['Geoffrey Hinton']
        },
        {
            'title': '多位知名作者论文',
            'authors': ['Yoshua Bengio', 'Yann LeCun', 'Ian Goodfellow']
        },
        {
            'title': '混合作者论文',
            'authors': ['Andrew Ng', 'John Smith', 'Jane Doe']
        },
        {
            'title': '普通作者论文',
            'authors': ['Alice Johnson', 'Bob Williams', 'Carol Brown']
        },
        {
            'title': '无作者论文',
            'authors': []
        }
    ]
    
    logger.info("计算不同论文的作者评分:")
    for paper in test_papers:
        score = calculate_author_score(paper)
        authors_str = ', '.join(paper['authors']) if paper['authors'] else '无作者'
        logger.info(f"  论文 '{paper['title']}' (作者: {authors_str})")
        logger.info(f"  作者评分: {score:.2f}")
        
        # 如果有作者，显示每个作者的h-index
        if paper['authors']:
            h_indices = [get_author_hindex(author) for author in paper['authors']]
            h_indices_str = ', '.join([f"{author}: {h}" for author, h in zip(paper['authors'], h_indices)])
            logger.info(f"  作者h-index: {h_indices_str}")
            
            # 如果有多个作者，显示最高和平均h-index
            if len(paper['authors']) > 1:
                max_h = max(h_indices)
                avg_h = sum(h_indices) / len(h_indices)
                combined_h = (max_h * 0.7) + (avg_h * 0.3)
                logger.info(f"  最高h-index: {max_h}, 平均h-index: {avg_h:.2f}, 综合h-index: {combined_h:.2f}")
        
        logger.info("")
    
    return True

def run_tests():
    """运行所有测试"""
    logger.info("开始测试基于h-index的作者评分系统")
    
    tests = [
        ("作者h-index获取测试", test_author_hindex),
        ("作者评分测试", test_author_scoring)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        logger.info(f"执行测试: {name}")
        if test_func():
            logger.info(f"测试通过: {name}")
            passed += 1
        else:
            logger.error(f"测试失败: {name}")
            failed += 1
    
    logger.info(f"测试完成: 通过 {passed}/{passed+failed} 测试")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
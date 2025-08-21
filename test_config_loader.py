#!/usr/bin/env python3
"""
arXiv RSS Filter Bot - 配置加载器测试脚本
用于测试 config_loader.py 的配置加载功能
"""

import logging
import os
import sys
import json
import yaml
from datetime import datetime

# 导入需要测试的模块
from config_loader import load_config

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_config_loader')

def create_test_config(filename, config_data):
    """创建测试用的配置文件"""
    try:
        with open(filename, 'w') as f:
            yaml.dump(config_data, f)
        logger.info(f"创建测试配置文件: {filename}")
        return True
    except Exception as e:
        logger.error(f"创建测试配置文件失败: {str(e)}")
        return False

def test_valid_config():
    """测试有效的配置文件"""
    logger.info("测试有效的配置文件")
    
    # 创建一个有效的配置
    test_config = {
        'keywords': ['test', 'machine learning'],
        'keyword_weight': 1.0,
        'score_threshold': 1.0,
        'max_results': 50,
        'recency_weight': 0.7,
        'author_weight': 0.3,
        'categories': ['cs.AI', 'cs.LG']
    }
    
    test_file = 'test_valid_config.yaml'
    
    if create_test_config(test_file, test_config):
        try:
            # 加载配置
            config = load_config(test_file)
            
            # 验证配置是否正确加载
            assert config['keywords'] == ['test', 'machine learning'], "关键词加载错误"
            assert config['keyword_weight'] == 1.0, "关键词权重加载错误"
            assert config['score_threshold'] == 1.0, "分数阈值加载错误"
            assert config['max_results'] == 50, "最大结果数加载错误"
            assert config['recency_weight'] == 0.7, "时间权重加载错误"
            assert config['author_weight'] == 0.3, "作者权重加载错误"
            assert config['categories'] == ['cs.AI', 'cs.LG'], "分类加载错误"
            assert config['run_hour'] == 8, "默认运行时间应为8"
            assert config['email_on_error'] is False, "默认错误邮件设置应为False"
            
            logger.info("有效配置文件测试通过")
            return True
        except Exception as e:
            logger.error(f"测试有效配置文件失败: {str(e)}")
            return False
        finally:
            # 清理测试文件
            if os.path.exists(test_file):
                os.remove(test_file)

def test_missing_required():
    """测试缺少必要参数的配置文件"""
    logger.info("测试缺少必要参数的配置文件")
    
    # 创建一个缺少必要参数的配置
    test_config = {
        'keywords': ['test'],
        # 缺少 keyword_weight
        'score_threshold': 1.0,
        # 缺少 max_results
    }
    
    test_file = 'test_missing_config.yaml'
    
    if create_test_config(test_file, test_config):
        try:
            # 尝试加载配置，应该抛出ValueError
            config = load_config(test_file)
            logger.error("测试失败：应该抛出ValueError但没有")
            return False
        except ValueError as e:
            logger.info(f"预期的错误被正确抛出: {str(e)}")
            return True
        except Exception as e:
            logger.error(f"测试失败：抛出了意外的异常类型: {type(e).__name__}")
            return False
        finally:
            # 清理测试文件
            if os.path.exists(test_file):
                os.remove(test_file)

def test_nonexistent_file():
    """测试不存在的配置文件"""
    logger.info("测试不存在的配置文件")
    
    # 使用一个肯定不存在的文件名
    test_file = f'nonexistent_config_{datetime.now().timestamp()}.yaml'
    
    try:
        # 尝试加载不存在的配置文件，应该抛出FileNotFoundError
        config = load_config(test_file)
        logger.error("测试失败：应该抛出FileNotFoundError但没有")
        return False
    except FileNotFoundError as e:
        logger.info(f"预期的错误被正确抛出: {str(e)}")
        return True
    except Exception as e:
        logger.error(f"测试失败：抛出了意外的异常类型: {type(e).__name__}")
        return False

def test_actual_config():
    """测试实际的配置文件"""
    logger.info("测试实际的配置文件 (config.yaml)")
    
    try:
        # 加载实际配置
        config = load_config()
        
        # 打印配置（不包括敏感信息）
        safe_config = config.copy()
        if 'email' in safe_config:
            if 'password' in safe_config['email']:
                safe_config['email']['password'] = '********'
                
        logger.info(f"成功加载实际配置: {json.dumps(safe_config, indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        logger.error(f"加载实际配置失败: {str(e)}")
        return False

def run_tests():
    """运行所有测试"""
    logger.info("开始测试配置加载功能")
    
    # 运行测试并计数
    tests = [
        ("有效配置测试", test_valid_config),
        ("缺少必要参数测试", test_missing_required),
        ("不存在的文件测试", test_nonexistent_file),
        ("实际配置测试", test_actual_config)
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
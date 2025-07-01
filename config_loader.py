"""
arXiv RSS Filter Bot - Configuration loader
arXiv RSS 过滤机器人 - 配置加载器

该模块负责从YAML配置文件中加载用户配置，并进行必要的验证和默认值设置。
配置文件包含关键词、过滤参数等，用于控制整个应用的行为。
"""

import yaml  # 导入YAML解析库，用于读取配置文件
import logging  # 导入日志模块
import os  # 导入操作系统模块，用于文件路径操作

logger = logging.getLogger(__name__)  # 获取当前模块的日志记录器

DEFAULT_CONFIG_FILE = "config.yaml"  # 默认配置文件名

def load_config(config_file=DEFAULT_CONFIG_FILE):
    """
    从YAML文件加载配置
    
    Args:
        config_file (str): 配置文件路径
        
    Returns:
        dict: 配置参数字典
        
    Raises:
        FileNotFoundError: 配置文件不存在时抛出
        ValueError: 配置缺少必要参数时抛出
    """
    try:
        # 检查配置文件是否存在
        if not os.path.exists(config_file):
            logger.error(f"Configuration file {config_file} not found")  # 记录错误：配置文件未找到
            raise FileNotFoundError(f"Configuration file {config_file} not found")  # 抛出文件未找到异常
        
        # 打开并解析YAML配置文件
        with open(config_file, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file) or {}  # 安全加载YAML内容，如果文件不存在则返回空字典
            
        # 验证必要的配置项是否存在
        required_keys = ['keywords', 'max_results']  # 必需的配置键
        for key in required_keys:
            if key not in config:
                logger.error(f"Missing required configuration: {key}")  # 记录错误：缺少必要配置
                raise ValueError(f"Missing required configuration: {key}")  # 抛出值错误异常
        
        # 设置默认值，如果配置中不包含这些键
        config.setdefault('recency_weight', 0.3)  # 设置默认时效性权重为0.3
        config.setdefault('author_weight', 0.2)  # 设置默认作者影响力权重为0.2
        config.setdefault('run_hour', None)  # 默认不设置定时运行
        config.setdefault('email_on_error', False)  # 默认不发送错误邮件
        config.setdefault('max_days_old', 30)  # 默认只获取30天内的论文
        config.setdefault('history_enabled', True)  # 默认启用历史记录功能
        
        # 处理日期范围配置（如果存在）
        if 'date_range' in config:
            date_range = config['date_range']
            # 验证日期范围格式
            if not isinstance(date_range, dict):
                logger.warning("date_range should be a dictionary, ignoring")
                config.pop('date_range')
            else:
                # 验证年份和月份
                if 'year' in date_range and not isinstance(date_range['year'], int):
                    logger.warning("date_range.year should be an integer, ignoring")
                    date_range.pop('year')
                
                if 'month' in date_range and not (isinstance(date_range['month'], int) and 1 <= date_range['month'] <= 12):
                    logger.warning("date_range.month should be an integer between 1 and 12, ignoring")
                    date_range.pop('month')
                
                # 如果年份和月份都被移除，则移除整个date_range
                if not date_range:
                    logger.warning("date_range is empty after validation, ignoring")
                    config.pop('date_range')
                else:
                    logger.info(f"Using date range filter: {date_range}")
                
        logger.info(f"配置加载完成，关键词数量: {len(config.get('keywords', []))}")
        return config  # 返回完整的配置字典
        
    except Exception as e:  # 捕获所有可能的异常
        logger.error(f"Error loading configuration: {str(e)}", exc_info=True)  # 记录错误详情
        raise  # 重新抛出异常，让调用者处理

def save_config(config, config_file=DEFAULT_CONFIG_FILE):
    """
    将配置保存到YAML文件
    
    Args:
        config (dict): 配置参数字典
        config_file (str): 配置文件路径
        
    Returns:
        bool: 保存是否成功
    """
    try:
        # 确保目录存在
        config_dir = os.path.dirname(os.path.abspath(config_file))
        os.makedirs(config_dir, exist_ok=True)
        
        # 写入配置文件
        with open(config_file, 'w', encoding='utf-8') as file:
            yaml.dump(config, file, default_flow_style=False)  # 将配置写入YAML文件
            
        logger.info(f"Configuration saved to {config_file}")  # 记录保存成功信息
        return True  # 返回成功标志
        
    except Exception as e:  # 捕获所有可能的异常
        logger.error(f"Error saving configuration: {str(e)}", exc_info=True)  # 记录错误详情
        return False  # 返回失败标志 
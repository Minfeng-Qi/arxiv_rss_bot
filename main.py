#!/usr/bin/env python3
"""
arXiv RSS Filter Bot - Main script
arXiv RSS 过滤机器人 - 主脚本

这是项目的主要入口点，负责协调整个工作流程：
1. 从arXiv获取最新论文
2. 根据关键词和日期过滤论文
3. 提取作者信息和机构
4. 生成RSS订阅源
5. 处理错误并发送通知
6. 支持定时执行
"""

import logging  # 导入日志模块，用于记录程序运行状态
import os  # 导入操作系统模块，用于文件和目录操作
import sys  # 导入系统模块
import traceback  # 导入异常跟踪模块
from datetime import datetime, timedelta  # 导入日期时间模块
import uuid  # 导入UUID模块，用于生成唯一标识符
import json  # 导入JSON模块，用于处理JSON数据
import time  # 导入时间模块

# 导入定时任务相关模块
from apscheduler.schedulers.blocking import BlockingScheduler  # 阻塞式调度器
from apscheduler.triggers.cron import CronTrigger  # Cron风格的触发器

# 导入自定义模块
from arxiv_fetcher import fetch_latest_papers  # 论文获取模块
from paper_processor import process_papers  # 论文处理模块
from rss_generator import generate_rss  # RSS生成模块
from config_loader import load_config  # 配置加载模块
from error_notifier import send_error_notification  # 错误通知模块
from email_notifier import send_notification  # 邮件通知模块（可选）
from email_subscription import run_subscription  # 邮件订阅模块

# 设置日志系统
# 配置日志格式、级别和输出位置
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 设置日志格式：时间-名称-级别-消息
    handlers=[
        # 将日志写入文件，文件名包含当天日期
        logging.FileHandler(f"logs/arxiv_rss_bot_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()  # 同时将日志输出到控制台
    ]
)
logger = logging.getLogger(__name__)  # 获取当前模块的日志记录器

# 定义输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")  # 设置输出目录为当前文件同级的output目录
LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")  # 设置日志目录为当前文件同级的logs目录
HISTORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history")  # 设置历史记录目录

# 确保必要的目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)  # 创建输出目录（如果不存在）
os.makedirs(LOGS_DIR, exist_ok=True)  # 创建日志目录（如果不存在）
os.makedirs(HISTORY_DIR, exist_ok=True)  # 创建历史记录目录（如果不存在）

def setup_logging():
    """设置日志记录器"""
    # 获取当前日期作为日志文件名
    log_filename = datetime.now().strftime("%Y%m%d") + ".log"  # 日志文件名格式：20240630.log
    log_file = os.path.join(LOGS_DIR, log_filename)  # 日志文件路径
    
    # 配置日志记录器
    logging.basicConfig(
        level=logging.INFO,  # 日志级别
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
        handlers=[
            logging.FileHandler(log_file),  # 输出到文件
            logging.StreamHandler(sys.stdout)  # 输出到标准输出
        ]
    )
    
    # 降低第三方库的日志级别，减少无关日志信息
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("feedgen").setLevel(logging.WARNING)
    
    return logging.getLogger("arXiv_RSS_Bot")  # 返回配置好的日志记录器

def save_history_record(config, processed_papers, output_file):
    """
    保存处理历史记录
    
    Args:
        config (dict): 使用的配置
        processed_papers (list): 处理后的论文列表
        output_file (str): 生成的RSS文件路径
        
    Returns:
        str: 生成的历史记录ID
    """
    # 检查是否启用历史记录
    if not config.get('history_enabled', True):
        return None
    
    try:
        # 生成唯一ID
        history_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # 创建历史记录
        history_record = {
            'id': history_id,
            'timestamp': timestamp,
            'config': {
                'keywords': config.get('keywords', []),
                'max_days_old': config.get('max_days_old', 30),
                'categories': config.get('categories', [])
            },
            'papers_count': len(processed_papers),
            'papers': [{
                'title': paper['title'],
                'id': paper['id'],
                'published': paper['published'].isoformat() if paper.get('published') else None,
                'categories': paper.get('categories', []),
                'keyword_matches': paper.get('keyword_matches', [])
            } for paper in processed_papers],
            'output_file': os.path.basename(output_file)
        }
        
        # 保存为JSON文件
        history_file = os.path.join(HISTORY_DIR, f"{history_id}.json")
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_record, f, indent=2)
        
        logger.info(f"历史记录已保存: {history_file}")
        return history_id
    except Exception as e:
        logger.error(f"保存历史记录失败: {str(e)}")
        return None

def run_pipeline():
    """运行完整的处理流水线
    
    这是主要的工作流程函数，包括：
    1. 加载用户配置
    2. 从arXiv获取最新论文
    3. 根据关键词和日期过滤论文
    4. 提取作者信息和机构
    5. 生成RSS订阅源
    6. 处理可能出现的错误
    
    Returns:
        dict: 包含处理结果的字典，包括生成的RSS文件路径、处理的论文数量等
    """
    try:
        logger.info("Starting arXiv RSS Filter Bot pipeline")  # 记录流水线启动日志
        
        # 加载配置文件
        config = load_config()  # 从config.yaml加载用户配置
        logger.info(f"Loaded configuration with {len(config['keywords'])} keywords")  # 记录加载了多少关键词
        
        # 获取最新论文
        # 增加日期范围获取更多论文
        max_days = config.get('max_days_old', 30) 
        # 设置获取数量为max_days * 每天平均论文数 * 类别数
        categories_count = len(config.get('categories', ['cs.AI']))
        fetch_max = min(1000, max(100, max_days * categories_count * 15))
        logger.info(f"Fetching up to {fetch_max} papers from the last {max_days} days")
        
        # 修改获取数量
        config_for_fetch = config.copy()
        config_for_fetch['max_results'] = fetch_max
        
        # 记录开始获取论文的时间
        fetch_start_time = datetime.now()
        
        # 尝试获取论文，加入重试逻辑
        max_retries = 3
        retry_count = 0
        papers = []
        
        while retry_count < max_retries:
            try:
                papers = fetch_latest_papers(config_for_fetch)  # 获取最新论文
                if papers:  # 如果成功获取论文
                    break  # 跳出重试循环
            except Exception as e:
                retry_count += 1
                logger.warning(f"Attempt {retry_count}/{max_retries} failed: {str(e)}")
                if retry_count >= max_retries:
                    raise  # 重试次数用完，重新抛出异常
                time.sleep(60)  # 等待1分钟后重试
        
        logger.info(f"Fetched {len(papers)} papers from arXiv")  # 记录获取的论文数量
        
        # 处理论文（过滤、提取信息）
        processed_papers = process_papers(papers, config)  # 处理论文
        logger.info(f"Processed down to {len(processed_papers)} papers after filtering")  # 记录过滤后的论文数量
        
        if processed_papers:  # 如果有通过过滤的论文
            # 每次都用新的now生成唯一文件名
            now = datetime.now()
            date_str = now.strftime('%Y%m%d')
            time_str = now.strftime('%H%M%S')
            # 关键词简写
            keywords = config.get('keywords', [])
            def keyword_abbr(word):
                return ''.join([w[0].upper() for w in word.split() if w])
            abbrs = [keyword_abbr(k) for k in keywords][:3]  # 最多3个
            abbr_str = '_'.join(abbrs) if abbrs else 'ALL'
            filename = f"{date_str}_{time_str}_{abbr_str}.xml"
            output_file = os.path.join(OUTPUT_DIR, filename)
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            # 生成RSS文件
            rss_file = generate_rss(
                processed_papers, 
                output_file,
                config.get('rss_title', 'arXiv RSS Filter Bot - Personalized Papers'),
                config.get('rss_description', 'Automatically filtered arXiv papers based on your research interests')
            )
            logger.info(f"Generated RSS feed at {rss_file}")
            # 保存历史记录
            history_id = save_history_record(config, processed_papers, output_file)
            logger.info(f"Saved history record with ID: {history_id}")
            
            # 运行邮件订阅功能，发送最新论文
            if config.get('email_subscription', False):
                logger.info("Running email subscription...")
                subscription_result = run_subscription()
                if subscription_result:
                    logger.info("Email subscription completed successfully")
                else:
                    logger.warning("Email subscription did not send any emails")
            
            # 记录处理时间
            elapsed_time = (datetime.now() - fetch_start_time).total_seconds()
            logger.info(f"Pipeline completed in {elapsed_time:.2f} seconds. Generated {len(processed_papers)} papers.")
            return {
                "success": True,
                "message": "Pipeline completed successfully",
                "papers_count": len(processed_papers),
                "output_file": os.path.basename(output_file),
                "history_id": history_id,
                "elapsed_time": f"{elapsed_time:.2f}s"
            }
        else:  # 如果没有通过过滤的论文
            logger.info("No papers passed filters, no RSS generated")  # 记录没有生成RSS的信息
            return {
                "success": True,
                "message": "No papers passed filters",
                "papers_count": 0
            }
        
    except Exception as e:  # 捕获所有可能的异常
        logger.error(f"Error in pipeline: {str(e)}", exc_info=True)  # 记录错误详情，包括堆栈跟踪
        if config.get('email_on_error', False):  # 如果配置了错误邮件通知
            send_error_notification(str(e), config.get('email', {}))  # 发送错误通知邮件
        return {
            "success": False,
            "error": str(e),
            "message": "Pipeline failed"
        }

def schedule_job():
    """设置定时任务
    
    配置调度器，使流水线按照用户设定的时间每天自动运行
    """
    config = load_config()  # 加载配置
    run_hour = config.get('run_hour', 8)  # 获取运行时间，默认为早上8点
    
    scheduler = BlockingScheduler()  # 创建阻塞式调度器
    trigger = CronTrigger(hour=run_hour, minute=0)  # 创建每天指定小时运行的触发器
    scheduler.add_job(run_pipeline, trigger=trigger)  # 添加运行流水线的任务
    
    logger.info(f"Scheduled daily job to run at {run_hour}:00")  # 记录定时任务设置成功
    scheduler.start()  # 启动调度器，此调用会阻塞当前线程

def main():
    """
    主函数，协调整个处理流程
    """
    logger.info("arXiv RSS Filter Bot pipeline started")  # 记录开始信息
    
    try:
        # 步骤1：加载配置文件
        config = load_config()  # 加载配置
        
        # 步骤2：获取最新论文
        # 增加日期范围获取更多论文
        max_days = config.get('max_days_old', 30) 
        # 设置获取数量为max_days * 每天平均论文数 * 类别数
        categories_count = len(config.get('categories', ['cs.AI']))
        fetch_max = min(1000, max(100, max_days * 10 * categories_count))
        logger.info(f"Fetching up to {fetch_max} papers from the last {max_days} days")
        
        # 修改获取数量
        config_for_fetch = config.copy()
        config_for_fetch['max_results'] = fetch_max
        
        papers = fetch_latest_papers(config_for_fetch)  # 获取最新论文
        logger.info(f"Fetched {len(papers)} papers")  # 记录获取的论文数量
        
        # 步骤3：处理论文（过滤、提取信息）
        processed_papers = process_papers(papers, config)  # 处理论文
        logger.info(f"Processed down to {len(processed_papers)} papers")  # 记录处理后的论文数量
        
        # 步骤4：生成RSS文件
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")  # 日期格式：YYYYMMDD
        time_str = now.strftime("%H%M%S")  # 时间格式：HHMMSS
        output_file = os.path.join(OUTPUT_DIR, f"arxiv_filtered_{date_str}_{time_str}.xml")  # 输出文件路径，包含时间戳
        generate_rss(processed_papers, output_file)  # 生成RSS文件
        logger.info(f"Generated RSS feed: {output_file}")  # 记录RSS生成完成
        
        # 步骤5：保存历史记录
        history_id = save_history_record(config, processed_papers, output_file)
        logger.info(f"Saved history record with ID: {history_id}")
        
        # 完成
        logger.info("arXiv RSS Filter Bot pipeline completed successfully")  # 记录处理成功
        
    except Exception as e:  # 捕获所有异常
        # 记录处理失败详情
        logger.error(f"Pipeline failed: {str(e)}")  # 记录错误信息
        logger.error(traceback.format_exc())  # 记录完整的异常堆栈
        
        # 如果配置了错误邮件通知，发送错误通知
        try:
            if config.get('email_on_error') and config.get('email_address'):  # 检查是否需要发送错误通知
                logger.info(f"Sending error notification to {config['email_address']}")  # 记录发送通知的信息
                error_msg = f"Pipeline failed: {str(e)}\n\n{traceback.format_exc()}"  # 错误消息
                send_notification(config['email_address'], "arXiv RSS Filter Bot Error", error_msg)  # 发送错误通知
        except Exception as email_error:
            logger.error(f"Failed to send error notification: {str(email_error)}")  # 记录发送通知失败的信息
        
        # 返回错误状态码
        sys.exit(1)  # 以错误代码退出

if __name__ == "__main__":
    logger = setup_logging()  # 设置日志记录器
    
    # 检查运行模式：一次性执行还是定时任务
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":  # 如果有--schedule参数
        schedule_job()  # 以定时任务模式运行
    else:
        main()  # 执行主函数，包括运行流水线 
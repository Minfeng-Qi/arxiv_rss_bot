#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Conference Paper Scheduler
会议论文定时调度器

该模块负责根据配置自动调度会议论文的获取和推送
"""

import os
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from config_loader import load_config
from conference_subscription import run_conference_pipeline

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConferenceScheduler:
    """会议论文定时调度器"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.config = None
        self.load_config()
        self.setup_scheduler()
    
    def load_config(self):
        """加载配置"""
        try:
            self.config = load_config()
            logger.info("会议调度器配置加载成功")
        except Exception as e:
            logger.error(f"加载配置失败: {str(e)}")
            self.config = {}
    
    def setup_scheduler(self):
        """设置调度任务"""
        if not self.config:
            logger.error("没有可用的配置，跳过调度器设置")
            return
        
        conferences_config = self.config.get('conferences', {})
        if not conferences_config.get('enabled', False):
            logger.info("会议论文功能未启用，跳过调度器设置")
            return
        
        conference_list = conferences_config.get('conference_list', [])
        
        # 按推送频率分组
        monthly_conferences = []
        quarterly_conferences = []
        
        for conf in conference_list:
            frequency = conf.get('push_frequency', 'manual')
            if frequency == 'monthly':
                monthly_conferences.append(conf['name'])
            elif frequency == 'quarterly':
                quarterly_conferences.append(conf['name'])
        
        # 设置月度任务 - 每月第一天上午9点
        if monthly_conferences:
            self.scheduler.add_job(
                func=self.run_monthly_conferences,
                trigger=CronTrigger(day=1, hour=9, minute=0),
                id='monthly_conference_job',
                name='Monthly Conference Papers',
                args=[monthly_conferences],
                replace_existing=True
            )
            logger.info(f"已设置月度会议推送任务，涵盖会议: {', '.join(monthly_conferences)}")
        
        # 设置季度任务 - 每季度第一个月第一天上午10点
        if quarterly_conferences:
            self.scheduler.add_job(
                func=self.run_quarterly_conferences,
                trigger=CronTrigger(month='1,4,7,10', day=1, hour=10, minute=0),
                id='quarterly_conference_job',
                name='Quarterly Conference Papers',
                args=[quarterly_conferences],
                replace_existing=True
            )
            logger.info(f"已设置季度会议推送任务，涵盖会议: {', '.join(quarterly_conferences)}")
        
        # 设置每日检查任务 - 检查是否有需要更新的会议
        self.scheduler.add_job(
            func=self.daily_check,
            trigger=CronTrigger(hour=8, minute=0),
            id='daily_conference_check',
            name='Daily Conference Check',
            replace_existing=True
        )
        logger.info("已设置每日会议检查任务")
    
    def run_monthly_conferences(self, conference_names):
        """运行月度会议推送"""
        logger.info(f"开始执行月度会议论文推送: {', '.join(conference_names)}")
        try:
            # 临时修改配置，只处理月度会议
            original_config = self.config.copy()
            
            # 过滤出月度会议
            filtered_conferences = []
            for conf in self.config['conferences']['conference_list']:
                if conf['name'] in conference_names:
                    filtered_conferences.append(conf)
            
            # 临时修改配置
            self.config['conferences']['conference_list'] = filtered_conferences
            
            # 运行会议流程
            result = run_conference_pipeline()
            
            # 恢复原配置
            self.config = original_config
            
            if result:
                logger.info(f"月度会议推送完成: {result}")
            else:
                logger.warning("月度会议推送没有结果")
                
        except Exception as e:
            logger.error(f"月度会议推送失败: {str(e)}")
    
    def run_quarterly_conferences(self, conference_names):
        """运行季度会议推送"""
        logger.info(f"开始执行季度会议论文推送: {', '.join(conference_names)}")
        try:
            # 临时修改配置，只处理季度会议
            original_config = self.config.copy()
            
            # 过滤出季度会议
            filtered_conferences = []
            for conf in self.config['conferences']['conference_list']:
                if conf['name'] in conference_names:
                    filtered_conferences.append(conf)
            
            # 临时修改配置
            self.config['conferences']['conference_list'] = filtered_conferences
            
            # 运行会议流程
            result = run_conference_pipeline()
            
            # 恢复原配置
            self.config = original_config
            
            if result:
                logger.info(f"季度会议推送完成: {result}")
            else:
                logger.warning("季度会议推送没有结果")
                
        except Exception as e:
            logger.error(f"季度会议推送失败: {str(e)}")
    
    def daily_check(self):
        """每日检查任务"""
        logger.info("执行每日会议检查")
        try:
            # 检查是否有会议需要立即处理
            # 这里可以添加特殊逻辑，比如检查新会议、重要更新等
            
            current_date = datetime.now()
            
            # 检查是否是特殊日期，需要额外推送
            if current_date.day == 15:  # 每月15日额外检查一次
                logger.info("月中额外检查会议更新")
                # 可以在这里添加额外的检查逻辑
            
            logger.info("每日会议检查完成")
            
        except Exception as e:
            logger.error(f"每日会议检查失败: {str(e)}")
    
    def start(self):
        """启动调度器"""
        try:
            self.scheduler.start()
            logger.info("会议论文调度器已启动")
            
            # 打印当前任务
            jobs = self.scheduler.get_jobs()
            if jobs:
                logger.info(f"当前活跃任务数量: {len(jobs)}")
                for job in jobs:
                    logger.info(f"  - {job.name}: {job.next_run_time}")
            else:
                logger.info("没有活跃的调度任务")
                
        except Exception as e:
            logger.error(f"启动调度器失败: {str(e)}")
    
    def stop(self):
        """停止调度器"""
        try:
            self.scheduler.shutdown()
            logger.info("会议论文调度器已停止")
        except Exception as e:
            logger.error(f"停止调度器失败: {str(e)}")
    
    def get_job_status(self):
        """获取任务状态"""
        jobs = self.scheduler.get_jobs()
        job_info = []
        
        for job in jobs:
            try:
                next_run = getattr(job, 'next_run_time', None)
                if next_run:
                    next_run_str = next_run.isoformat()
                else:
                    next_run_str = None
            except Exception:
                next_run_str = None
                
            job_info.append({
                'id': job.id,
                'name': job.name,
                'next_run': next_run_str,
                'trigger': str(job.trigger)
            })
        
        return {
            'running': self.scheduler.running,
            'job_count': len(jobs),
            'jobs': job_info
        }
    
    def run_immediate_test(self):
        """立即运行一次测试"""
        logger.info("执行立即测试运行")
        try:
            result = run_conference_pipeline()
            logger.info(f"立即测试运行完成: {result}")
            return result
        except Exception as e:
            logger.error(f"立即测试运行失败: {str(e)}")
            return False

# 全局调度器实例
_conference_scheduler = None

def get_conference_scheduler():
    """获取全局调度器实例"""
    global _conference_scheduler
    if _conference_scheduler is None:
        _conference_scheduler = ConferenceScheduler()
    return _conference_scheduler

def start_conference_scheduler():
    """启动会议论文调度器"""
    scheduler = get_conference_scheduler()
    scheduler.start()
    return scheduler

def stop_conference_scheduler():
    """停止会议论文调度器"""
    global _conference_scheduler
    if _conference_scheduler:
        _conference_scheduler.stop()
        _conference_scheduler = None

if __name__ == "__main__":
    # 命令行运行时启动调度器
    import signal
    import time
    
    def signal_handler(signum, frame):
        logger.info("收到停止信号，正在关闭调度器...")
        stop_conference_scheduler()
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("启动会议论文调度器...")
    scheduler = start_conference_scheduler()
    
    try:
        # 保持程序运行
        while True:
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭...")
        stop_conference_scheduler()
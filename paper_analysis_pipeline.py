#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文分析流水线
整合DeepSeek AI分析和Notion集成的完整流程
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from config_loader import load_config
from deepseek_analyzer import DeepSeekAnalyzer
from notion_integrator import NotionIntegrator

logger = logging.getLogger(__name__)

class PaperAnalysisPipeline:
    """论文分析流水线"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化分析流水线"""
        self.config = config or load_config()
        
        # 初始化分析器
        self.deepseek_analyzer = DeepSeekAnalyzer(self.config)
        self.notion_integrator = NotionIntegrator(self.config)
        
        # 获取AI分析配置
        ai_config = self.config.get('ai_analysis', {})
        self.auto_analysis_enabled = ai_config.get('auto_analysis_enabled', False)
        self.max_papers_per_batch = ai_config.get('max_papers_per_batch', 20)
        
        # 创建分析结果目录
        self.analysis_dir = "analysis_results"
        os.makedirs(self.analysis_dir, exist_ok=True)
    
    def is_enabled(self) -> bool:
        """检查分析流水线是否启用"""
        return (self.deepseek_analyzer.is_enabled() or 
                self.notion_integrator.is_enabled())
    
    def analyze_papers(self, papers: List[Dict[str, Any]], force_analysis: bool = False) -> Dict[str, Any]:
        """分析论文的主要方法"""
        if not papers:
            logger.info("没有论文需要分析")
            return {'success': True, 'analyzed_count': 0, 'results': []}
        
        # 检查是否应该进行分析
        if not force_analysis and not self.auto_analysis_enabled:
            logger.info("自动分析未启用，跳过AI分析")
            return {'success': True, 'analyzed_count': 0, 'results': []}
        
        if not self.is_enabled():
            logger.warning("AI分析功能未启用")
            return {'success': False, 'error': 'AI分析功能未启用', 'results': []}
        
        logger.info(f"开始AI分析流水线，待分析论文数: {len(papers)}")
        
        try:
            # 智能筛选论文
            selected_papers = self._smart_select_papers(papers)
            logger.info(f"智能筛选后论文数: {len(selected_papers)}")
            
            # 使用DeepSeek进行AI分析
            analysis_results = []
            if self.deepseek_analyzer.is_enabled():
                logger.info("开始DeepSeek AI分析...")
                analysis_results = self.deepseek_analyzer.analyze_papers_batch(selected_papers)
                logger.info(f"DeepSeek分析完成，成功分析 {len(analysis_results)} 篇论文")
            
            # 保存分析结果
            results_file = ""
            if analysis_results:
                results_file = self.deepseek_analyzer.save_analysis_results(analysis_results, self.analysis_dir)
            
            # 同步到Notion
            notion_count = 0
            if analysis_results and self.notion_integrator.is_enabled():
                logger.info("开始同步到Notion...")
                notion_count = self.notion_integrator.sync_analysis_results(analysis_results)
                logger.info(f"Notion同步完成，成功创建 {notion_count} 个页面")
            
            # 生成分析报告
            report = self._generate_analysis_report(analysis_results, papers, selected_papers)
            
            return {
                'success': True,
                'analyzed_count': len(analysis_results),
                'notion_count': notion_count,
                'results': analysis_results,
                'results_file': results_file,
                'report': report
            }
            
        except Exception as e:
            logger.error(f"AI分析流水线执行失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'analyzed_count': 0,
                'results': []
            }
    
    def _smart_select_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """智能筛选论文"""
        ai_config = self.config.get('ai_analysis', {})
        smart_selection = ai_config.get('smart_selection', {})
        
        if not smart_selection.get('enabled', True):
            # 如果未启用智能筛选，直接返回限制数量的论文
            return papers[:self.max_papers_per_batch]
        
        # 这里可以添加更复杂的筛选逻辑
        # 例如基于关键词匹配、作者权重、期刊影响因子等
        
        # 当前简单实现：按发布时间排序，选择最新的论文
        try:
            sorted_papers = sorted(
                papers, 
                key=lambda x: x.get('published', x.get('pubDate', '')),
                reverse=True
            )
            return sorted_papers[:self.max_papers_per_batch]
        except Exception as e:
            logger.warning(f"智能筛选失败，使用默认方法: {str(e)}")
            return papers[:self.max_papers_per_batch]
    
    def _generate_analysis_report(self, analysis_results: List[Dict[str, Any]], 
                                 original_papers: List[Dict[str, Any]], 
                                 selected_papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成分析报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_papers': len(original_papers),
            'selected_papers': len(selected_papers),
            'analyzed_papers': len(analysis_results),
            'analysis_rate': len(analysis_results) / len(selected_papers) if selected_papers else 0,
            'categories': {},
            'average_score': 0.0,
            'high_quality_papers': []
        }
        
        if not analysis_results:
            return report
        
        # 统计类别分布
        categories = {}
        total_score = 0
        high_quality_threshold = 0.7
        
        for result in analysis_results:
            analysis = result.get('analysis', {})
            
            # 统计类别
            category = analysis.get('category', 'Other')
            categories[category] = categories.get(category, 0) + 1
            
            # 计算平均分数
            score = analysis.get('score', 0)
            total_score += score
            
            # 收集高质量论文
            if score >= high_quality_threshold:
                report['high_quality_papers'].append({
                    'title': result.get('title', ''),
                    'score': score,
                    'category': category
                })
        
        report['categories'] = categories
        report['average_score'] = total_score / len(analysis_results)
        
        return report
    
    def run_analysis_pipeline(self, papers: List[Dict[str, Any]], save_report: bool = True) -> Dict[str, Any]:
        """运行完整的分析流水线"""
        logger.info("启动AI论文分析流水线")
        
        # 执行分析
        result = self.analyze_papers(papers, force_analysis=True)
        
        # 保存报告
        if save_report and result.get('success', False):
            self._save_pipeline_report(result)
        
        # 记录流水线执行结果
        if result.get('success', False):
            logger.info(f"AI分析流水线执行成功: 分析了 {result.get('analyzed_count', 0)} 篇论文")
        else:
            logger.error(f"AI分析流水线执行失败: {result.get('error', '未知错误')}")
        
        return result
    
    def _save_pipeline_report(self, result: Dict[str, Any]) -> str:
        """保存流水线报告"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(self.analysis_dir, f"pipeline_report_{timestamp}.json")
            
            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"流水线报告已保存: {report_file}")
            return report_file
            
        except Exception as e:
            logger.error(f"保存流水线报告失败: {str(e)}")
            return ""

def run_ai_analysis(papers: List[Dict[str, Any]], config: Dict[str, Any] = None) -> Dict[str, Any]:
    """便捷函数：运行AI分析流水线"""
    pipeline = PaperAnalysisPipeline(config)
    return pipeline.run_analysis_pipeline(papers)

def check_ai_analysis_status(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """检查AI分析功能状态"""
    if config is None:
        config = load_config()
    
    pipeline = PaperAnalysisPipeline(config)
    
    status = {
        'pipeline_enabled': pipeline.is_enabled(),
        'auto_analysis_enabled': pipeline.auto_analysis_enabled,
        'deepseek_enabled': pipeline.deepseek_analyzer.is_enabled(),
        'notion_enabled': pipeline.notion_integrator.is_enabled(),
        'max_papers_per_batch': pipeline.max_papers_per_batch,
        'analysis_dir': pipeline.analysis_dir
    }
    
    return status

if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    # 检查状态
    status = check_ai_analysis_status()
    print("AI分析功能状态:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # 测试分析
    test_papers = [
        {
            'title': 'Test Paper: Advanced Techniques in Deep Learning',
            'description': 'This paper presents novel approaches to deep learning optimization and regularization techniques.',
            'published': '2025-08-20',
            'arxiv_id': 'test.001'
        }
    ]
    
    pipeline = PaperAnalysisPipeline()
    if pipeline.is_enabled():
        result = pipeline.run_analysis_pipeline(test_papers)
        print(f"\\n测试结果: {result.get('success', False)}")
        if result.get('success'):
            print(f"分析论文数: {result.get('analyzed_count', 0)}")
    else:
        print("\\nAI分析功能未启用")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion数据库管理工具
用于查看和管理AI分析结果
"""

import requests
import json
import logging
from datetime import datetime
from config_loader import load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotionManager:
    """Notion数据库管理器"""
    
    def __init__(self):
        self.config = load_config()
        ai_config = self.config.get('ai_analysis', {})
        notion_config = ai_config.get('notion', {})
        
        self.integration_token = notion_config.get('integration_token', '')
        self.database_id = notion_config.get('database_id', '')
        
        self.base_url = 'https://api.notion.com/v1'
        self.headers = {
            'Authorization': f'Bearer {self.integration_token}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }
    
    def get_database_info(self):
        """获取数据库信息"""
        if not self.database_id:
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/databases/{self.database_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取数据库信息失败: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取数据库信息异常: {str(e)}")
            return None
    
    def query_database(self, page_size=10, filter_conditions=None):
        """查询数据库内容"""
        if not self.database_id:
            return None
        
        query_data = {
            'page_size': page_size,
            'sorts': [
                {
                    'property': '分析日期',
                    'direction': 'descending'
                }
            ]
        }
        
        if filter_conditions:
            query_data['filter'] = filter_conditions
        
        try:
            response = requests.post(
                f"{self.base_url}/databases/{self.database_id}/query",
                headers=self.headers,
                json=query_data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"查询数据库失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"查询数据库异常: {str(e)}")
            return None
    
    def get_recent_analyses(self, count=5):
        """获取最近的分析结果"""
        result = self.query_database(page_size=count)
        if not result:
            return []
        
        analyses = []
        for page in result.get('results', []):
            properties = page.get('properties', {})
            
            analysis = {
                'id': page.get('id'),
                'url': page.get('url'),
                'title': self._extract_title(properties.get('标题', {})),
                'paper_id': self._extract_rich_text(properties.get('论文ID', {})),
                'importance': self._extract_select(properties.get('重要性', {})),
                'category': self._extract_select(properties.get('分类', {})),
                'analysis_date': self._extract_date(properties.get('分析日期', {})),
                'status': self._extract_select(properties.get('状态', {})),
                'authors': self._extract_rich_text(properties.get('作者', {})),
                'is_llm_related': self._extract_checkbox(properties.get('是否LLM相关', {}))
            }
            analyses.append(analysis)
        
        return analyses
    
    def _extract_title(self, title_prop):
        """提取标题"""
        try:
            return title_prop.get('title', [{}])[0].get('text', {}).get('content', '')
        except:
            return ''
    
    def _extract_rich_text(self, text_prop):
        """提取富文本"""
        try:
            return text_prop.get('rich_text', [{}])[0].get('text', {}).get('content', '')
        except:
            return ''
    
    def _extract_number(self, number_prop):
        """提取数字"""
        try:
            return number_prop.get('number', 0)
        except:
            return 0
    
    def _extract_select(self, select_prop):
        """提取选择"""
        try:
            return select_prop.get('select', {}).get('name', '')
        except:
            return ''
    
    def _extract_date(self, date_prop):
        """提取日期"""
        try:
            return date_prop.get('date', {}).get('start', '')
        except:
            return ''
    
    def _extract_checkbox(self, checkbox_prop):
        """提取复选框"""
        try:
            return checkbox_prop.get('checkbox', False)
        except:
            return False
    
    def get_statistics(self):
        """获取统计信息"""
        result = self.query_database(page_size=100)  # 获取更多数据用于统计
        if not result:
            return {}
        
        pages = result.get('results', [])
        
        stats = {
            'total_papers': len(pages),
            'categories': {},
            'average_score': 0,
            'high_quality_papers': 0,
            'recent_count': 0
        }
        
        total_score = 0
        high_quality_threshold = 0.7
        recent_threshold = '2025-08-01'  # 最近一个月
        
        for page in pages:
            properties = page.get('properties', {})
            
            # 统计类别
            category = self._extract_select(properties.get('类别', {}))
            if category:
                stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            # 统计分数
            score = self._extract_number(properties.get('分数', {}))
            total_score += score
            
            if score >= high_quality_threshold:
                stats['high_quality_papers'] += 1
            
            # 统计最近论文
            analysis_date = self._extract_date(properties.get('分析日期', {}))
            if analysis_date >= recent_threshold:
                stats['recent_count'] += 1
        
        if len(pages) > 0:
            stats['average_score'] = total_score / len(pages)
        
        return stats

def main():
    """主函数"""
    print("=== Notion AI分析数据库管理器 ===")
    
    manager = NotionManager()
    
    if not manager.database_id:
        print("❌ 未配置Notion数据库ID")
        return
    
    # 获取数据库信息
    print("\n📊 数据库信息:")
    db_info = manager.get_database_info()
    if db_info:
        title = db_info.get('title', [{}])[0].get('text', {}).get('content', '未知')
        print(f"数据库名称: {title}")
        print(f"数据库ID: {manager.database_id}")
        print(f"创建时间: {db_info.get('created_time', '未知')}")
        print(f"最后编辑: {db_info.get('last_edited_time', '未知')}")
    
    # 获取最近分析
    print("\n📝 最近分析结果:")
    recent_analyses = manager.get_recent_analyses(5)
    
    if recent_analyses:
        for i, analysis in enumerate(recent_analyses, 1):
            print(f"\n{i}. {analysis['title']}")
            print(f"   论文ID: {analysis['paper_id']}")
            print(f"   重要性: {analysis['importance']}")
            print(f"   分类: {analysis['category']}")
            print(f"   作者: {analysis['authors']}")
            print(f"   LLM相关: {'✓' if analysis['is_llm_related'] else '✗'}")
            print(f"   分析日期: {analysis['analysis_date']}")
            print(f"   状态: {analysis['status']}")
            print(f"   链接: {analysis['url']}")
    else:
        print("暂无分析结果")
    
    # 获取统计信息
    print("\n📈 统计信息:")
    stats = manager.get_statistics()
    
    print(f"总论文数: {stats.get('total_papers', 0)}")
    print(f"平均分数: {stats.get('average_score', 0):.2f}")
    print(f"高质量论文数 (≥0.7): {stats.get('high_quality_papers', 0)}")
    print(f"最近分析数: {stats.get('recent_count', 0)}")
    
    print("\n📊 类别分布:")
    categories = stats.get('categories', {})
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count} 篇")
    
    print(f"\n🔗 数据库链接: https://www.notion.so/{manager.database_id}")

if __name__ == "__main__":
    main()
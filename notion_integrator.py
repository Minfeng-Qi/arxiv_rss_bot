#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion集成模块
用于将AI分析结果保存到Notion数据库
"""

import json
import logging
import requests
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from config_loader import load_config

logger = logging.getLogger(__name__)

class NotionIntegrator:
    """Notion集成器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化Notion集成器"""
        self.config = config
        ai_config = config.get('ai_analysis', {})
        notion_config = ai_config.get('notion', {})
        
        self.integration_token = notion_config.get('integration_token', '')
        self.database_id = notion_config.get('database_id', '')
        self.enabled = notion_config.get('enabled', False)
        
        self.base_url = 'https://api.notion.com/v1'
        self.headers = {
            'Authorization': f'Bearer {self.integration_token}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }
        
        if not self.integration_token or not self.enabled:
            logger.warning("Notion集成未启用或令牌未配置")
    
    def is_enabled(self) -> bool:
        """检查是否启用Notion集成"""
        return self.enabled and bool(self.integration_token) and bool(self.database_id)
    
    def test_connection(self) -> bool:
        """测试Notion连接"""
        if not self.integration_token:
            logger.error("Notion集成令牌未配置")
            return False
        
        try:
            # 测试API连接
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Notion连接测试成功")
                return True
            else:
                logger.error(f"Notion连接测试失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Notion连接测试异常: {str(e)}")
            return False
    
    def create_database_page(self, analysis_result: Dict[str, Any]) -> bool:
        """在Notion数据库中创建页面"""
        if not self.is_enabled():
            logger.warning("Notion集成未启用")
            return False
        
        if not self.database_id:
            logger.error("Notion数据库ID未配置")
            return False
        
        try:
            # 构建页面属性
            properties = self._build_page_properties(analysis_result)
            
            # 构建页面内容
            children = self._build_page_content(analysis_result)
            
            page_data = {
                'parent': {'database_id': self.database_id},
                'properties': properties,
                'children': children
            }
            
            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=page_data,
                timeout=30
            )
            
            if response.status_code == 200:
                page_info = response.json()
                page_url = page_info.get('url', '')
                logger.info(f"成功创建Notion页面: {page_url}")
                return True
            else:
                logger.error(f"创建Notion页面失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"创建Notion页面异常: {str(e)}")
            return False
    
    def _build_page_properties(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """构建页面属性（适配现有数据库结构）"""
        analysis = analysis_result.get('analysis', {})
        
        properties = {
            '标题': {
                'title': [
                    {
                        'text': {
                            'content': analysis_result.get('title', '未知标题')
                        }
                    }
                ]
            },
            '论文ID': {
                'rich_text': [
                    {
                        'text': {
                            'content': analysis_result.get('paper_id', '')
                        }
                    }
                ]
            },
            '分析日期': {
                'date': {
                    'start': analysis_result.get('analysis_date', datetime.now().isoformat())[:10]
                }
            },
            '发布日期': {
                'date': {
                    'start': self._parse_date(analysis_result.get('published_date', ''))
                }
            },
            '状态': {
                'select': {
                    'name': analysis_result.get('status', 'success')
                }
            }
        }
        
        # 添加论文链接（如果有arxiv_id）
        paper_id = analysis_result.get('paper_id', '')
        if paper_id:
            arxiv_url = f"https://arxiv.org/abs/{paper_id}"
            properties['论文链接'] = {
                'url': arxiv_url
            }
        
        # 适配现有字段
        # 使用"分类"字段代替"类别"
        category = analysis.get('category', 'Other')
        properties['分类'] = {
            'select': {
                'name': category
            }
        }
        
        # 使用"重要性"字段显示分数等级
        score = analysis.get('score', 0.5)
        if score >= 0.8:
            importance = '高'
        elif score >= 0.6:
            importance = '中'
        else:
            importance = '低'
        
        properties['重要性'] = {
            'select': {
                'name': importance
            }
        }
        
        # 添加作者信息
        authors = analysis_result.get('authors', [])
        if authors:
            authors_text = ', '.join(authors) if isinstance(authors, list) else str(authors)
            properties['作者'] = {
                'rich_text': [
                    {
                        'text': {
                            'content': authors_text
                        }
                    }
                ]
            }
        
        # 设置领域标签
        keywords = analysis.get('keywords', [])
        if keywords:
            # 将关键词作为领域标签
            field_options = []
            for keyword in keywords[:5]:  # 最多5个标签
                field_options.append({'name': keyword})
            
            properties['领域'] = {
                'multi_select': field_options
            }
        
        # 判断是否LLM相关
        llm_keywords = ['large language model', 'LLM', 'GPT', 'language model', 'transformer']
        is_llm_related = any(keyword.lower() in str(analysis).lower() for keyword in llm_keywords)
        properties['是否LLM相关'] = {
            'checkbox': is_llm_related
        }
        
        return properties
    
    def _build_page_content(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """构建页面内容"""
        analysis = analysis_result.get('analysis', {})
        
        children = []
        
        # 添加核心摘要
        core_summary = analysis.get('core_summary', '')
        if core_summary:
            children.extend([
                {
                    'object': 'block',
                    'type': 'heading_2',
                    'heading_2': {
                        'rich_text': [{'type': 'text', 'text': {'content': '🎯 核心内容'}}]
                    }
                },
                {
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [{'type': 'text', 'text': {'content': core_summary}}]
                    }
                }
            ])
        
        # 添加关键技术
        key_techniques = analysis.get('key_techniques', [])
        if key_techniques:
            children.append({
                'object': 'block',
                'type': 'heading_2',
                'heading_2': {
                    'rich_text': [{'type': 'text', 'text': {'content': '🔧 关键技术'}}]
                }
            })
            
            for technique in key_techniques:
                children.append({
                    'object': 'block',
                    'type': 'bulleted_list_item',
                    'bulleted_list_item': {
                        'rich_text': [{'type': 'text', 'text': {'content': technique}}]
                    }
                })
        
        # 添加主要贡献
        contributions = analysis.get('contributions', [])
        if contributions:
            children.append({
                'object': 'block',
                'type': 'heading_2',
                'heading_2': {
                    'rich_text': [{'type': 'text', 'text': {'content': '💡 主要贡献'}}]
                }
            })
            
            for contribution in contributions:
                children.append({
                    'object': 'block',
                    'type': 'bulleted_list_item',
                    'bulleted_list_item': {
                        'rich_text': [{'type': 'text', 'text': {'content': contribution}}]
                    }
                })
        
        # 添加深度见解
        insights = analysis.get('insights', '')
        if insights:
            children.extend([
                {
                    'object': 'block',
                    'type': 'heading_2',
                    'heading_2': {
                        'rich_text': [{'type': 'text', 'text': {'content': '🔍 深度见解'}}]
                    }
                },
                {
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [{'type': 'text', 'text': {'content': insights}}]
                    }
                }
            ])
        
        # 添加评估
        evaluation = analysis.get('evaluation', '')
        if evaluation:
            children.extend([
                {
                    'object': 'block',
                    'type': 'heading_2',
                    'heading_2': {
                        'rich_text': [{'type': 'text', 'text': {'content': '📊 方法评估'}}]
                    }
                },
                {
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [{'type': 'text', 'text': {'content': evaluation}}]
                    }
                }
            ])
        
        # 添加关键词
        keywords = analysis.get('keywords', [])
        if keywords:
            keywords_text = ', '.join(keywords)
            children.extend([
                {
                    'object': 'block',
                    'type': 'heading_2',
                    'heading_2': {
                        'rich_text': [{'type': 'text', 'text': {'content': '🏷️ 关键词'}}]
                    }
                },
                {
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [{'type': 'text', 'text': {'content': keywords_text}}]
                    }
                }
            ])
        
        # 添加作者信息
        authors = analysis_result.get('authors', [])
        if authors:
            authors_text = ', '.join(authors) if isinstance(authors, list) else str(authors)
            children.extend([
                {
                    'object': 'block',
                    'type': 'heading_2',
                    'heading_2': {
                        'rich_text': [{'type': 'text', 'text': {'content': '👥 作者'}}]
                    }
                },
                {
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [{'type': 'text', 'text': {'content': authors_text}}]
                    }
                }
            ])
        
        return children
    
    def _parse_date(self, date_str: str) -> str:
        """解析日期字符串"""
        if not date_str:
            return datetime.now().isoformat()[:10]
        
        try:
            # 尝试多种日期格式
            for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
                try:
                    dt = datetime.strptime(date_str[:len(fmt)], fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # 如果都失败了，返回当前日期
            return datetime.now().strftime('%Y-%m-%d')
            
        except Exception:
            return datetime.now().strftime('%Y-%m-%d')
    
    def sync_analysis_results(self, analysis_results: List[Dict[str, Any]]) -> int:
        """同步分析结果到Notion"""
        if not self.is_enabled():
            logger.warning("Notion集成未启用，跳过同步")
            return 0
        
        if not analysis_results:
            logger.info("没有分析结果需要同步")
            return 0
        
        success_count = 0
        
        for i, result in enumerate(analysis_results, 1):
            try:
                logger.info(f"正在创建第 {i}/{len(analysis_results)} 个Notion页面")
                
                if self.create_database_page(result):
                    success_count += 1
                
                # 添加延迟避免API限流
                if i < len(analysis_results):
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"同步第 {i} 个结果时出错: {str(e)}")
                continue
        
        logger.info(f"Notion同步完成，成功创建 {success_count}/{len(analysis_results)} 个页面")
        return success_count

def sync_to_notion(analysis_results: List[Dict[str, Any]], config: Dict[str, Any] = None) -> int:
    """便捷函数：同步分析结果到Notion"""
    if config is None:
        config = load_config()
    
    integrator = NotionIntegrator(config)
    return integrator.sync_analysis_results(analysis_results)

if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    config = load_config()
    integrator = NotionIntegrator(config)
    
    if integrator.is_enabled():
        # 测试连接
        if integrator.test_connection():
            print("Notion连接测试成功")
        else:
            print("Notion连接测试失败")
    else:
        print("Notion集成未启用，请检查配置")
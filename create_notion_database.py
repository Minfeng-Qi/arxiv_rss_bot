#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建Notion数据库用于存储AI分析结果
"""

import requests
import json
import logging
from datetime import datetime
from config_loader import load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_analysis_database():
    """创建AI分析结果数据库"""
    config = load_config()
    ai_config = config.get('ai_analysis', {})
    notion_config = ai_config.get('notion', {})
    
    integration_token = notion_config.get('integration_token', '')
    
    if not integration_token:
        logger.error("Notion集成令牌未配置")
        return None
    
    headers = {
        'Authorization': f'Bearer {integration_token}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    
    # 首先获取用户信息，找到可用的父页面
    try:
        user_response = requests.get(
            'https://api.notion.com/v1/users/me',
            headers=headers,
            timeout=10
        )
        
        if user_response.status_code != 200:
            logger.error(f"获取用户信息失败: {user_response.text}")
            return None
            
        # 搜索可用的页面作为父页面
        search_response = requests.post(
            'https://api.notion.com/v1/search',
            headers=headers,
            json={
                'filter': {
                    'property': 'object',
                    'value': 'page'
                },
                'page_size': 10
            },
            timeout=10
        )
        
        if search_response.status_code != 200:
            logger.error(f"搜索页面失败: {search_response.text}")
            return None
            
        search_results = search_response.json()
        pages = search_results.get('results', [])
        
        if not pages:
            logger.error("未找到可用的父页面，请在Notion中创建一个页面并授权给集成")
            return None
        
        # 使用第一个找到的页面作为父页面
        parent_page = pages[0]
        parent_id = parent_page['id']
        parent_title = parent_page.get('properties', {}).get('title', {}).get('title', [{}])[0].get('text', {}).get('content', '未知页面')
        
        logger.info(f"使用父页面: {parent_title} ({parent_id})")
        
        # 创建数据库结构
        database_data = {
            'parent': {
                'type': 'page_id',
                'page_id': parent_id
            },
            'title': [
                {
                    'type': 'text',
                    'text': {
                        'content': 'AI论文分析结果'
                    }
                }
            ],
            'properties': {
                '标题': {
                    'title': {}
                },
                '论文ID': {
                    'rich_text': {}
                },
                '论文链接': {
                    'url': {}
                },
                '分数': {
                    'number': {
                        'format': 'number'
                    }
                },
                '类别': {
                    'select': {
                        'options': [
                            {'name': 'LLM&AI Agents', 'color': 'blue'},
                            {'name': 'Reinforcement Learning', 'color': 'green'},
                            {'name': 'Multimodal&Vision', 'color': 'orange'},
                            {'name': 'Foundation Models', 'color': 'purple'},
                            {'name': 'Security&Privacy', 'color': 'red'},
                            {'name': 'Other', 'color': 'gray'}
                        ]
                    }
                },
                '分析日期': {
                    'date': {}
                },
                '发布日期': {
                    'date': {}
                },
                '状态': {
                    'select': {
                        'options': [
                            {'name': 'success', 'color': 'green'},
                            {'name': 'pending', 'color': 'yellow'},
                            {'name': 'failed', 'color': 'red'}
                        ]
                    }
                },
                '关键词': {
                    'multi_select': {
                        'options': [
                            {'name': 'large language model', 'color': 'blue'},
                            {'name': 'reinforcement learning', 'color': 'green'},
                            {'name': 'multimodal', 'color': 'orange'},
                            {'name': 'transformer', 'color': 'purple'},
                            {'name': 'deep learning', 'color': 'red'},
                            {'name': 'neural network', 'color': 'pink'},
                            {'name': 'AI agent', 'color': 'brown'},
                            {'name': 'computer vision', 'color': 'yellow'}
                        ]
                    }
                }
            }
        }
        
        # 创建数据库
        response = requests.post(
            'https://api.notion.com/v1/databases',
            headers=headers,
            json=database_data,
            timeout=30
        )
        
        if response.status_code == 200:
            database_info = response.json()
            database_id = database_info['id']
            database_url = database_info['url']
            
            logger.info(f"✅ 成功创建Notion数据库!")
            logger.info(f"数据库ID: {database_id}")
            logger.info(f"数据库URL: {database_url}")
            
            return database_id
        else:
            logger.error(f"❌ 创建数据库失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"创建数据库时出错: {str(e)}")
        return None

def update_config_with_database_id(database_id):
    """更新配置文件中的数据库ID"""
    try:
        config = load_config()
        
        # 更新数据库ID
        if 'ai_analysis' not in config:
            config['ai_analysis'] = {}
        if 'notion' not in config['ai_analysis']:
            config['ai_analysis']['notion'] = {}
        
        config['ai_analysis']['notion']['database_id'] = database_id
        
        # 保存配置
        import yaml
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        logger.info(f"✅ 配置文件已更新，数据库ID: {database_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 更新配置文件失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== 创建Notion AI分析数据库 ===")
    
    database_id = create_analysis_database()
    
    if database_id:
        print(f"\n✅ 数据库创建成功!")
        print(f"数据库ID: {database_id}")
        
        # 更新配置文件
        if update_config_with_database_id(database_id):
            print("✅ 配置文件已自动更新")
            print("\n现在可以使用Notion集成功能了!")
        else:
            print("⚠️ 请手动将以下数据库ID添加到config.yaml中:")
            print(f"ai_analysis.notion.database_id: {database_id}")
    else:
        print("\n❌ 数据库创建失败")
        print("请检查:")
        print("1. Notion集成令牌是否正确")
        print("2. 是否在Notion中创建了页面并授权给集成")
        print("3. 网络连接是否正常")
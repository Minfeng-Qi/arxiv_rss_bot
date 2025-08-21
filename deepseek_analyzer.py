#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek AI论文分析模块
用于使用DeepSeek API对arXiv论文进行深度分析
"""

import json
import logging
import requests
import time
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from config_loader import load_config

logger = logging.getLogger(__name__)

class DeepSeekAnalyzer:
    """DeepSeek AI分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化分析器"""
        self.config = config
        ai_config = config.get('ai_analysis', {})
        deepseek_config = ai_config.get('deepseek', {})
        
        self.api_key = deepseek_config.get('api_key', '')
        self.enabled = deepseek_config.get('enabled', False)
        self.base_url = 'https://api.deepseek.com/chat/completions'
        
        # 分析设置
        self.max_papers = ai_config.get('max_papers_per_batch', 20)
        self.min_score_threshold = ai_config.get('smart_selection', {}).get('min_score_threshold', 0.6)
        
        if not self.api_key or not self.enabled:
            logger.warning("DeepSeek API未启用或API密钥未配置")
    
    def is_enabled(self) -> bool:
        """检查是否启用AI分析"""
        return self.enabled and bool(self.api_key)
    
    def analyze_paper(self, paper: Dict[str, Any], paper_index: int, total_papers: int) -> Optional[Dict[str, Any]]:
        """分析单篇论文"""
        if not self.is_enabled():
            logger.warning("DeepSeek分析器未启用")
            return None
            
        logger.info(f"正在分析第 {paper_index}/{total_papers} 篇论文")
        
        title = paper.get('title', '')
        abstract = paper.get('description', paper.get('summary', ''))
        
        # 构建分析提示
        prompt = self._build_analysis_prompt(title, abstract)
        
        try:
            # 调用DeepSeek API
            response = self._call_deepseek_api(prompt)
            
            if response:
                # 解析分析结果
                analysis_result = self._parse_analysis_response(response, paper)
                logger.info(f"成功分析论文: {title[:60]}...")
                return analysis_result
            else:
                logger.error(f"API调用失败: {title}")
                return None
                
        except Exception as e:
            logger.error(f"分析论文时出错: {str(e)}")
            return None
    
    def _build_analysis_prompt(self, title: str, abstract: str) -> str:
        """构建深度分析提示词"""
        prompt = f"""<think>
作为一名资深的AI研究专家和学术评审员，我需要对这篇论文进行全面深度的分析。我将从技术创新、方法论、实验设计、理论贡献、实际应用价值等多个维度进行专业评估。

论文信息：
- 标题：{title}
- 摘要：{abstract}

分析框架：
1. 技术创新性分析：识别核心技术突破点和创新机制
2. 方法论评估：分析所用方法的科学性和有效性
3. 理论贡献：评估对现有理论体系的推进作用
4. 实验验证：分析实验设计的合理性和结果的可信度
5. 应用前景：评估实际应用价值和产业化潜力
6. 技术局限性：识别方法的边界条件和改进空间
7. 学术影响力：预测对领域发展的推动作用
</think>

作为AI领域的资深研究专家，请对以下学术论文进行深度专业分析：

**论文标题**: {title}

**论文摘要**: {abstract}

请进行全面深度的学术分析，从以下维度进行专业评估并以JSON格式返回：

{{
  "core_summary": "核心内容和主要思想的深度总结(150-200字，要体现论文的核心价值和技术本质)",
  "technical_innovation": {{
    "key_breakthroughs": ["技术突破点1", "技术突破点2", "技术突破点3"],
    "novel_mechanisms": "创新机制和原理描述(100-150字)",
    "differentiation": "与现有方法的核心差异化(80-120字)"
  }},
  "methodology_analysis": {{
    "approach": "所采用的核心方法论(80-100字)",
    "technical_depth": "技术深度评估(复杂度、理论基础、实现难度)(60-80字)",
    "scientific_rigor": "科学严谨性评价(实验设计、数据验证等)(60-80字)"
  }},
  "contributions": {{
    "theoretical": ["理论贡献1", "理论贡献2"],
    "practical": ["实践贡献1", "实践贡献2"],
    "methodological": ["方法论贡献1", "方法论贡献2"]
  }},
  "deep_insights": {{
    "significance": "学术意义和价值深度解读(120-150字)",
    "implications": "对领域发展的启示和影响(100-120字)",
    "future_directions": "可能引发的研究方向(80-100字)"
  }},
  "critical_evaluation": {{
    "strengths": ["优势1", "优势2", "优势3"],
    "limitations": ["局限性1", "局限性2"],
    "improvement_suggestions": ["改进建议1", "改进建议2"]
  }},
  "application_potential": {{
    "immediate_applications": ["直接应用场景1", "直接应用场景2"],
    "long_term_impact": "长期应用前景和产业价值(80-100字)",
    "commercialization": "商业化可能性评估(60-80字)"
  }},
  "technical_details": {{
    "key_algorithms": ["核心算法1", "核心算法2"],
    "datasets_benchmarks": ["数据集/基准1", "数据集/基准2"],
    "performance_metrics": ["性能指标1", "性能指标2"]
  }},
  "comparative_analysis": {{
    "baseline_methods": ["对比方法1", "对比方法2"],
    "performance_gains": "性能提升情况描述(60-80字)",
    "competitive_advantages": "竞争优势分析(60-80字)"
  }},
  "research_quality": {{
    "novelty_score": 0.85,
    "technical_difficulty": 0.8,
    "practical_value": 0.9,
    "experimental_rigor": 0.85,
    "overall_score": 0.85
  }},
  "classification": {{
    "primary_category": "主要类别",
    "secondary_categories": ["次要类别1", "次要类别2"],
    "research_area": "具体研究领域",
    "llm_relevance": true
  }},
  "keywords": {{
    "technical_terms": ["技术术语1", "技术术语2", "技术术语3"],
    "research_themes": ["研究主题1", "研究主题2"],
    "application_domains": ["应用领域1", "应用领域2"]
  }},
  "expert_recommendation": {{
    "target_audience": ["目标读者群体1", "目标读者群体2"],
    "reading_priority": "high/medium/low",
    "follow_up_papers": "建议关注的后续研究方向(60-80字)"
  }}
}}

**分析要求**：
1. **专业深度**：以资深研究员的视角进行分析，体现专业判断力
2. **技术精准**：准确识别核心技术点，避免泛泛而谈
3. **客观评价**：既要识别创新价值，也要指出潜在局限
4. **前瞻性**：评估对未来研究方向的指导意义
5. **实用性**：分析实际应用价值和产业化前景

**评分标准**：
- 创新性 (0-1)：技术突破程度和原创性
- 技术难度 (0-1)：实现复杂度和理论深度
- 实用价值 (0-1)：解决实际问题的能力
- 实验严谨性 (0-1)：验证方法的科学性
- 综合评分 (0-1)：整体学术价值

**类别选择**：LLM&AI Agents, Reinforcement Learning, Multimodal&Vision, Foundation Models, Computer Vision, NLP&Language, Security&Privacy, Robotics&Control, Other

请严格按照JSON格式返回，确保分析的专业性和深度。"""

        return prompt
    
    def _call_deepseek_api(self, prompt: str) -> Optional[str]:
        """调用DeepSeek API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'deepseek-chat',
            'messages': [
                {
                    'role': 'system',
                    'content': '你是一位资深的AI研究专家和学术评审员，具有深厚的技术背景和敏锐的学术洞察力。请以专业、客观、深入的视角进行论文分析。'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 4000,  # 增加token数量以支持深度分析
            'temperature': 0.2,  # 降低温度以提高分析的准确性和一致性
            'top_p': 0.85,       # 调整top_p以平衡创造性和准确性
            'stream': False      # 确保不使用流式响应
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # 提取JSON内容
                if '<think>' in content and '</think>' in content:
                    # 提取深度思考内容
                    think_match = re.search(r'<think>(.*?)</think>', content, re.DOTALL)
                    if think_match:
                        think_content = think_match.group(1).strip()
                        logger.info(f"成功提取深度思考内容，长度: {len(think_content)}")
                    
                    # 提取JSON内容
                    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
                
                return content
            else:
                logger.error(f"API请求失败，状态码: {response.status_code}, 响应: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"API调用异常: {str(e)}")
            return None
    
    def _parse_analysis_response(self, response: str, paper: Dict[str, Any]) -> Dict[str, Any]:
        """解析深度分析响应"""
        try:
            # 清理响应内容，提取JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            # 解析JSON
            analysis = json.loads(response)
            
            # 验证深度分析的核心字段
            core_fields = ['core_summary', 'technical_innovation', 'methodology_analysis', 'deep_insights']
            parsed_core_fields = [field for field in core_fields if field in analysis]
            
            # 验证评分字段
            quality_fields = ['research_quality', 'classification']
            parsed_quality_fields = [field for field in quality_fields if field in analysis]
            
            logger.info(f"成功解析核心分析: {parsed_core_fields}")
            logger.info(f"成功解析质量评估: {parsed_quality_fields}")
            
            # 提取关键信息用于兼容性
            try:
                # 从新结构中提取传统字段
                extracted_info = {
                    'score': analysis.get('research_quality', {}).get('overall_score', 0.8),
                    'category': analysis.get('classification', {}).get('primary_category', '未分类'),
                    'keywords': [],
                    'llm_related': analysis.get('classification', {}).get('llm_relevance', False)
                }
                
                # 合并关键词
                if 'keywords' in analysis:
                    keywords = analysis['keywords']
                    if isinstance(keywords, dict):
                        extracted_info['keywords'] = (
                            keywords.get('technical_terms', []) + 
                            keywords.get('research_themes', []) + 
                            keywords.get('application_domains', [])
                        )[:5]  # 限制关键词数量
                    elif isinstance(keywords, list):
                        extracted_info['keywords'] = keywords[:5]
                
                # 将提取的信息添加到分析中
                analysis.update(extracted_info)
                
            except Exception as e:
                logger.warning(f"提取兼容性信息时出错: {str(e)}")
            
            # 构建完整的分析结果
            result = {
                'paper_id': paper.get('arxiv_id', paper.get('id', '')),
                'title': paper.get('title', ''),
                'authors': paper.get('authors', []),
                'published_date': paper.get('published', paper.get('pubDate', '')),
                'analysis_date': datetime.now().isoformat(),
                'analysis': analysis,
                'analysis_depth': 'deep_analysis',  # 标记为深度分析
                'status': 'success'
            }
            
            # 记录分析质量统计
            if 'research_quality' in analysis:
                quality = analysis['research_quality']
                logger.info(f"论文质量评分 - 创新性: {quality.get('novelty_score', 'N/A')}, "
                          f"技术难度: {quality.get('technical_difficulty', 'N/A')}, "
                          f"实用价值: {quality.get('practical_value', 'N/A')}, "
                          f"综合评分: {quality.get('overall_score', 'N/A')}")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}")
            logger.error(f"响应内容预览: {response[:500]}...")
            
            # 尝试基础解析作为降级处理
            try:
                logger.info("尝试基础解析作为降级处理...")
                return self._parse_basic_response(response, paper)
            except:
                return None
                
        except Exception as e:
            logger.error(f"解析深度分析结果时出错: {str(e)}")
            return None
    
    def _parse_basic_response(self, response: str, paper: Dict[str, Any]) -> Dict[str, Any]:
        """基础解析作为降级处理"""
        try:
            # 简单的文本解析
            basic_analysis = {
                'core_summary': f"AI分析摘要：{response[:200]}...",
                'score': 0.7,
                'category': 'Other',
                'keywords': ['AI', '机器学习'],
                'llm_related': 'language model' in response.lower() or 'llm' in response.lower()
            }
            
            result = {
                'paper_id': paper.get('arxiv_id', paper.get('id', '')),
                'title': paper.get('title', ''),
                'authors': paper.get('authors', []),
                'published_date': paper.get('published', paper.get('pubDate', '')),
                'analysis_date': datetime.now().isoformat(),
                'analysis': basic_analysis,
                'analysis_depth': 'basic_fallback',  # 标记为降级处理
                'status': 'partial_success'
            }
            
            logger.warning("使用基础解析作为降级处理")
            return result
            
        except Exception as e:
            logger.error(f"基础解析也失败: {str(e)}")
            return None
    
    def analyze_papers_batch(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量分析论文"""
        if not self.is_enabled():
            logger.warning("DeepSeek分析器未启用，跳过分析")
            return []
        
        # 限制分析数量
        papers_to_analyze = papers[:self.max_papers]
        logger.info(f"开始批量分析 {len(papers_to_analyze)} 篇论文")
        
        results = []
        
        for i, paper in enumerate(papers_to_analyze, 1):
            try:
                analysis_result = self.analyze_paper(paper, i, len(papers_to_analyze))
                if analysis_result:
                    results.append(analysis_result)
                
                # 添加延迟避免API限流
                if i < len(papers_to_analyze):
                    time.sleep(2)
                    
            except Exception as e:
                logger.error(f"分析第 {i} 篇论文时出错: {str(e)}")
                continue
        
        logger.info(f"批量分析完成，成功分析 {len(results)} 篇论文")
        return results
    
    def save_analysis_results(self, results: List[Dict[str, Any]], output_dir: str = "analysis_results") -> str:
        """保存分析结果"""
        import os
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_arxiv_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        try:
            # 准备保存的数据
            save_data = {
                'timestamp': datetime.now().isoformat(),
                'total_papers': len(results),
                'analysis_config': {
                    'max_papers': self.max_papers,
                    'min_score_threshold': self.min_score_threshold
                },
                'results': results
            }
            
            # 保存到文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"分析结果已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"保存分析结果失败: {str(e)}")
            return ""

def analyze_papers_with_deepseek(papers: List[Dict[str, Any]], config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """便捷函数：使用DeepSeek分析论文"""
    if config is None:
        config = load_config()
    
    analyzer = DeepSeekAnalyzer(config)
    return analyzer.analyze_papers_batch(papers)

if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    test_papers = [
        {
            'title': 'Test Paper: Large Language Models for Code Generation',
            'description': 'This paper presents a novel approach to automatic code generation using large language models. We demonstrate significant improvements in code quality and generation speed.',
            'arxiv_id': 'test.001',
            'published': '2025-08-20'
        }
    ]
    
    config = load_config()
    analyzer = DeepSeekAnalyzer(config)
    
    if analyzer.is_enabled():
        results = analyzer.analyze_papers_batch(test_papers)
        if results:
            filepath = analyzer.save_analysis_results(results)
            print(f"测试完成，结果保存到: {filepath}")
    else:
        print("DeepSeek分析器未启用，请检查配置")
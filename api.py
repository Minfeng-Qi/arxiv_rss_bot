#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API服务器，用于提供Web界面与后端通信的接口
"""

import os
import json
import logging
import yaml
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# 创建日志记录器
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义目录路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
HISTORY_DIR = os.path.join(BASE_DIR, "history")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# 确保目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# 导入本地模块（确保这些模块正确）
try:
    from config_loader import load_config, save_config
    from main import run_pipeline_with_subscription, run_pipeline
except ImportError as e:
    logger.error(f"导入本地模块失败: {e}")
    # 提供备用实现以确保API服务能启动
    def load_config():
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            return {}
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return {}
    
    def save_config(config, file_path=CONFIG_PATH):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False)
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    def run_pipeline():
        logger.error("无法运行主流程，因为main模块导入失败")
        return {"error": "main模块导入失败，无法运行流程"}
    
    def run_pipeline_with_subscription():
        logger.error("无法运行完整流程，因为main模块导入失败")
        return {"error": "main模块导入失败，无法运行完整流程"}

app = Flask(__name__)
CORS(app)

@app.route('/api/run', methods=['POST'])
def run_bot():
    """触发机器人运行"""
    try:
        logger.info("Manual run triggered via API")
        result = run_pipeline_with_subscription()
        
        # 如果运行成功并生成了新的输出文件，返回更详细的信息
        if result.get('success') and result.get('output_file'):
            output_file = result.get('output_file')
            history_id = result.get('history_id')
            papers_count = result.get('papers_count', 0)
            elapsed_time = result.get('elapsed_time', '')
            
            return jsonify({
                'success': True, 
                'message': f'Pipeline completed successfully. Generated {papers_count} papers.',
                'result': {
                    'output_file': output_file,
                    'history_id': history_id,
                    'papers_count': papers_count,
                    'timestamp': datetime.now().isoformat(),
                    'elapsed_time': elapsed_time
                }
            })
        else:
            # 如果没有生成新的输出文件或运行失败
            return jsonify({
                'success': result.get('success', False),
                'message': result.get('message', 'Unknown error'),
                'result': result
            })
    except Exception as e:
        logger.error(f"Error running pipeline: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/run/rss-only', methods=['POST'])
def run_bot_rss_only():
    """触发机器人运行（仅生成RSS，不发送邮件）"""
    try:
        logger.info("Manual RSS-only run triggered via API")
        result = run_pipeline()
        
        # 如果运行成功并生成了新的输出文件，返回更详细的信息
        if result.get('success') and result.get('output_file'):
            output_file = result.get('output_file')
            history_id = result.get('history_id')
            papers_count = result.get('papers_count', 0)
            elapsed_time = result.get('elapsed_time', '')
            
            return jsonify({
                'success': True, 
                'message': f'RSS generation completed successfully. Generated {papers_count} papers (no email sent).',
                'result': {
                    'output_file': output_file,
                    'history_id': history_id,
                    'papers_count': papers_count,
                    'timestamp': datetime.now().isoformat(),
                    'elapsed_time': elapsed_time,
                    'email_sent': False
                }
            })
        else:
            # 如果没有生成新的输出文件或运行失败
            return jsonify({
                'success': result.get('success', False),
                'message': result.get('message', 'Unknown error'),
                'result': result
            })
    except Exception as e:
        logger.error(f"Error running RSS-only pipeline: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """获取或更新配置"""
    try:
        if request.method == 'GET':
            config = load_config()
            return jsonify({'success': True, 'config': config})
        else:
            data = request.json
            new_config = data.get('config', {})
            save_config(new_config, CONFIG_PATH)
            return jsonify({'success': True, 'message': 'Configuration updated'})
    except Exception as e:
        logger.error(f"Error with configuration: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/output', methods=['GET'])
def list_output():
    """列出输出文件"""
    try:
        # 获取所有XML文件
        files = []
        
        if os.path.exists(OUTPUT_DIR):
            files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.xml')]
        
        # 确保文件存在
        if not files:
            logger.info("No output files found")
            return jsonify({'success': True, 'files': []})
            
        # 按文件名排序，格式为arxiv_filtered_YYYYMMDD_HHMMSS.xml，最新的排前面
        def extract_date(filename):
            try:
                if 'arxiv_filtered_' in filename:
                    date_part = filename.replace('arxiv_filtered_', '').replace('.xml', '')
                    if '_' in date_part:  # 包含时间戳
                        date_str, time_str = date_part.split('_')
                        return f"{date_str}{time_str}"  # 返回YYYYMMDDHHMMSS格式用于排序
                    return date_part  # 仅日期部分
                return '0'  # 无法提取日期时的默认值
            except Exception:
                return '0'
                
        files.sort(key=extract_date, reverse=True)  # 按日期排序，最新的排前面
        
        logger.info(f"Found {len(files)} output files")
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        logger.error(f"Error listing output files: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/output/<filename>', methods=['GET', 'DELETE'])
def get_output_file(filename):
    """获取特定输出文件的内容"""
    try:
        if request.method == 'GET':
            file_path = os.path.join(OUTPUT_DIR, filename)
            if not os.path.exists(file_path):
                return jsonify({'success': False, 'error': 'File not found'}), 404
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return jsonify({'success': True, 'filename': filename, 'content': content})
        elif request.method == 'DELETE':
            file_path = os.path.join(OUTPUT_DIR, filename)
            if not os.path.exists(file_path):
                return jsonify({'success': False, 'error': 'File not found'}), 404
            os.remove(file_path)
            return jsonify({'success': True, 'message': 'File deleted'})
    except Exception as e:
        logger.error(f"Error reading output file: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/email/test', methods=['POST'])
def test_email_config():
    """测试邮件配置是否有效"""
    try:
        data = request.json
        email_config = data.get('email_config', {})
        
        # 检查必要的配置
        required_fields = ['smtp_server', 'port', 'username', 'password', 'recipient']
        missing_fields = [field for field in required_fields if not email_config.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False, 
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # 导入邮件发送模块
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # 创建测试邮件
        msg = MIMEMultipart()
        msg['From'] = email_config['username']
        msg['To'] = email_config['recipient']
        msg['Subject'] = 'arXiv RSS Filter Bot - Email Configuration Test'
        
        body = """
        <html>
        <body>
            <h2>Email Configuration Test</h2>
            <p>This is a test email to verify your email configuration for arXiv RSS Filter Bot.</p>
            <p>If you received this email, your configuration is working correctly.</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # 发送邮件
        with smtplib.SMTP(email_config['smtp_server'], email_config['port']) as server:
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
        
        return jsonify({
            'success': True, 
            'message': f'Test email sent successfully to {email_config["recipient"]}'
        })
        
    except Exception as e:
        logger.error(f"Error testing email configuration: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get the bot status."""
    try:
        status = {
            'lastRun': None,
            'paperCount': 0,
            'latestOutput': None,
            'papers': []
        }
        
        # Check output directory for latest file
        if os.path.exists(OUTPUT_DIR):
            files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.xml')]
            files.sort(reverse=True)  # Most recent first
            
            if files:
                latest_file = files[0]
                status['latestOutput'] = latest_file
                
                # Extract date from filename including timestamp if available
                if 'arxiv_filtered_' in latest_file:
                    # 尝试提取完整的日期和时间戳
                    date_part = latest_file.replace('arxiv_filtered_', '').replace('.xml', '')
                    try:
                        if '_' in date_part:  # 包含日期和时间
                            date_str, time_str = date_part.split('_')
                            # 格式为YYYYMMDD_HHMMSS
                            full_datetime = datetime.strptime(f"{date_str}_{time_str}", '%Y%m%d_%H%M%S')
                        else:  # 仅包含日期
                            date_str = date_part
                            # 格式为YYYYMMDD，使用当前时间作为时间部分
                            date_only = datetime.strptime(date_str, '%Y%m%d')
                            now = datetime.now()
                            full_datetime = datetime(
                                year=date_only.year, 
                                month=date_only.month, 
                                day=date_only.day,
                                hour=now.hour,
                                minute=now.minute,
                                second=now.second
                            )
                        
                        # 确保返回的时间包含时区信息，这样前端可以正确显示
                        status['lastRun'] = full_datetime.astimezone().isoformat()
                    except ValueError as e:
                        logger.warning(f"无法解析文件名中的日期时间: {e}")
                        status['lastRun'] = datetime.now().astimezone().isoformat()
                else:
                    status['lastRun'] = datetime.now().astimezone().isoformat()
                
                # Count papers in the RSS file
                try:
                    import xml.etree.ElementTree as ET
                    tree = ET.parse(os.path.join(OUTPUT_DIR, latest_file))
                    root = tree.getroot()
                    items = root.findall('./channel/item')
                    status['paperCount'] = len(items)
                    
                    # Add full data needed for dashboard
                    status['papers'] = []
                    for item in items:
                        title_elem = item.find('title')
                        description_elem = item.find('description')
                        
                        paper_data = {
                            'title': title_elem.text if title_elem is not None else 'Untitled',
                            'keywords': [],
                        }
                        
                        # Extract keywords from description
                        if description_elem is not None:
                            desc_text = description_elem.text
                            keywords_match = None
                            if desc_text:
                                keywords_match = desc_text.find('Matched keywords:')
                                if keywords_match >= 0:
                                    keywords_text = desc_text[keywords_match + len('Matched keywords:'):].split('.')[0].strip()
                                    paper_data['keywords'] = [kw.strip() for kw in keywords_text.split(',')]
                                    
                        status['papers'].append(paper_data)
                        
                except Exception as e:
                    logger.warning(f"Error extracting paper data: {str(e)}")
        
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def list_history():
    """列出历史记录"""
    try:
        # 支持分页
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 50)  # 最大50条每页
        
        # 获取所有历史记录文件
        history_files = [f for f in os.listdir(HISTORY_DIR) if f.endswith('.json')]
        
        # 按文件修改时间排序（最新在前）
        history_files.sort(key=lambda f: os.path.getmtime(os.path.join(HISTORY_DIR, f)), reverse=True)
        
        # 计算分页
        total = len(history_files)
        total_pages = (total - 1) // per_page + 1 if total > 0 else 1
        
        # 分页切片
        start = (page - 1) * per_page
        end = start + per_page
        page_files = history_files[start:end]
        
        # 读取历史记录元数据
        records = []
        for file in page_files:
            try:
                with open(os.path.join(HISTORY_DIR, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 只返回元数据，不包含完整论文列表
                    summary = {
                        'id': data.get('id'),
                        'timestamp': data.get('timestamp'),
                        'papers_count': data.get('papers_count', 0),
                        'keywords': data.get('config', {}).get('keywords', []),
                        'categories': data.get('config', {}).get('categories', []),
                        'output_file': data.get('output_file')
                    }
                    records.append(summary)
            except Exception as e:
                logger.error(f"Error reading history file {file}: {str(e)}")
        
        return jsonify({
            'success': True, 
            'records': records,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages
            }
        })
    except Exception as e:
        logger.error(f"Error listing history records: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history/<record_id>', methods=['GET'])
def get_history_record(record_id):
    """获取特定历史记录详情"""
    try:
        file_path = os.path.join(HISTORY_DIR, f"{record_id}.json")
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'History record not found'}), 404
            
        with open(file_path, 'r', encoding='utf-8') as f:
            record = json.load(f)
            
        return jsonify({'success': True, 'record': record})
    except Exception as e:
        logger.error(f"Error getting history record: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """获取日志文件"""
    try:
        if not os.path.exists(LOGS_DIR):
            return jsonify({'success': True, 'logs': []})
            
        log_files = [f for f in os.listdir(LOGS_DIR) if f.endswith('.log')]
        log_files.sort(reverse=True)  # Most recent first
        
        # Get most recent log file
        if not log_files:
            return jsonify({'success': True, 'logs': []})
            
        latest_log = os.path.join(LOGS_DIR, log_files[0])
        
        with open(latest_log, 'r', encoding='utf-8') as f:
            log_content = f.read().splitlines()
            # Return the last 100 lines maximum
            logs = log_content[-100:] if len(log_content) > 100 else log_content
        
        return jsonify({'success': True, 'logs': logs, 'file': log_files[0]})
    except Exception as e:
        logger.error(f"Error reading logs: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/subscription/history', methods=['GET'])
def get_subscription_history():
    """获取订阅历史记录"""
    try:
        SUBSCRIPTION_HISTORY_FILE = os.path.join(BASE_DIR, "subscription_history.json")
        
        if not os.path.exists(SUBSCRIPTION_HISTORY_FILE):
            return jsonify({
                'success': True, 
                'history': {
                    'sent_papers': [],
                    'last_sent': None,
                    'count': 0
                }
            })
        
        with open(SUBSCRIPTION_HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
            
        # 添加计数
        history['count'] = len(history.get('sent_papers', []))
        
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        logger.error(f"Error getting subscription history: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/conference/run', methods=['POST'])
def run_conference_pipeline():
    """触发会议论文获取和推送流程"""
    try:
        logger.info("Manual conference pipeline run triggered via API")
        
        # 导入会议相关模块
        from conference_subscription import run_conference_pipeline
        
        result = run_conference_pipeline()
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Conference pipeline completed successfully',
                'result': result
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Conference pipeline completed with no results',
                'result': result
            })
            
    except Exception as e:
        logger.error(f"Error running conference pipeline: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/conference/fetch', methods=['POST'])
def run_conference_fetch_only():
    """仅触发会议论文获取（不推送邮件）"""
    try:
        logger.info("Manual conference fetch triggered via API")
        
        # 导入会议获取模块
        from openreview_fetcher import run_conference_fetch
        
        result = run_conference_fetch()
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Conference papers fetched successfully',
                'result': result
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Conference fetch completed with no results',
                'result': result
            })
            
    except Exception as e:
        logger.error(f"Error fetching conference papers: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/conference/subscription', methods=['POST'])
def run_conference_subscription_only():
    """仅触发会议论文订阅推送（基于已有文件）"""
    try:
        logger.info("Manual conference subscription triggered via API")
        
        # 导入会议订阅模块
        from conference_subscription import process_conference_subscription
        
        result = process_conference_subscription()
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Conference subscription emails sent successfully',
                'result': result
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Conference subscription completed with no new papers',
                'result': result
            })
            
    except Exception as e:
        logger.error(f"Error processing conference subscription: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/conference/output', methods=['GET'])
def list_conference_output():
    """列出会议论文输出文件"""
    try:
        conference_output_dir = os.path.join(BASE_DIR, "conference_output")
        
        # 获取所有JSON文件
        files = []
        
        if os.path.exists(conference_output_dir):
            files = [f for f in os.listdir(conference_output_dir) if f.endswith('.json')]
        
        if not files:
            logger.info("No conference output files found")
            return jsonify({'success': True, 'files': []})
            
        # 按文件修改时间排序，最新的排前面
        files.sort(key=lambda f: os.path.getmtime(os.path.join(conference_output_dir, f)), reverse=True)
        
        logger.info(f"Found {len(files)} conference output files")
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        logger.error(f"Error listing conference output files: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/conference/output/<filename>', methods=['GET', 'DELETE'])
def get_conference_output_file(filename):
    """获取或删除特定会议论文文件的内容"""
    try:
        conference_output_dir = os.path.join(BASE_DIR, "conference_output")
        file_path = os.path.join(conference_output_dir, filename)
        
        if request.method == 'GET':
            if not os.path.exists(file_path):
                return jsonify({'success': False, 'error': 'File not found'}), 404
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            return jsonify({'success': True, 'filename': filename, 'content': content})
        elif request.method == 'DELETE':
            if not os.path.exists(file_path):
                return jsonify({'success': False, 'error': 'File not found'}), 404
            os.remove(file_path)
            return jsonify({'success': True, 'message': 'File deleted'})
    except Exception as e:
        logger.error(f"Error handling conference output file: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/conference/subscription/history', methods=['GET'])
def get_conference_subscription_history():
    """获取会议订阅历史记录"""
    try:
        conference_history_file = os.path.join(BASE_DIR, "conference_subscription_history.json")
        
        if not os.path.exists(conference_history_file):
            return jsonify({
                'success': True, 
                'history': {
                    'sent_papers': [],
                    'last_sent': None,
                    'sent_by_conference': {},
                    'count': 0
                }
            })
        
        with open(conference_history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
            
        # 添加计数
        history['count'] = len(history.get('sent_papers', []))
        
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        logger.error(f"Error getting conference subscription history: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/conference/scheduler/start', methods=['POST'])
def start_conference_scheduler_api():
    """启动会议论文调度器"""
    try:
        from conference_scheduler import start_conference_scheduler
        
        scheduler = start_conference_scheduler()
        status = scheduler.get_job_status()
        
        return jsonify({
            'success': True,
            'message': 'Conference scheduler started successfully',
            'scheduler_status': status
        })
    except Exception as e:
        logger.error(f"Error starting conference scheduler: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/conference/scheduler/stop', methods=['POST'])
def stop_conference_scheduler_api():
    """停止会议论文调度器"""
    try:
        from conference_scheduler import stop_conference_scheduler
        
        stop_conference_scheduler()
        
        return jsonify({
            'success': True,
            'message': 'Conference scheduler stopped successfully'
        })
    except Exception as e:
        logger.error(f"Error stopping conference scheduler: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/conference/scheduler/status', methods=['GET'])
def get_conference_scheduler_status():
    """获取会议论文调度器状态"""
    try:
        from conference_scheduler import get_conference_scheduler
        
        scheduler = get_conference_scheduler()
        status = scheduler.get_job_status()
        
        return jsonify({
            'success': True,
            'scheduler_status': status
        })
    except Exception as e:
        logger.error(f"Error getting conference scheduler status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/conference/scheduler/test', methods=['POST'])
def test_conference_scheduler():
    """测试会议论文调度器立即运行"""
    try:
        from conference_scheduler import get_conference_scheduler
        
        scheduler = get_conference_scheduler()
        result = scheduler.run_immediate_test()
        
        return jsonify({
            'success': True,
            'message': 'Conference scheduler test completed',
            'result': result
        })
    except Exception as e:
        logger.error(f"Error testing conference scheduler: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/docs', methods=['GET'])
def get_api_docs():
    """API documentation endpoint."""
    docs = {
        'description': 'arXiv RSS Filter Bot API with Conference Extension',
        'version': '1.1.0',
        'endpoints': [
            {
                'path': '/api/config',
                'methods': ['GET', 'POST'],
                'description': 'Get or update configuration'
            },
            {
                'path': '/api/run',
                'methods': ['POST'],
                'description': 'Trigger bot execution (RSS + email)'
            },
            {
                'path': '/api/run/rss-only',
                'methods': ['POST'],
                'description': 'Trigger RSS generation only (no email)'
            },
            {
                'path': '/api/output',
                'methods': ['GET'],
                'description': 'List all available output RSS files'
            },
            {
                'path': '/api/output/<filename>',
                'methods': ['GET', 'DELETE'],
                'description': 'Get or delete the content of a specific RSS file'
            },
            {
                'path': '/api/logs',
                'methods': ['GET'],
                'description': 'Get recent logs'
            },
            {
                'path': '/api/status',
                'methods': ['GET'],
                'description': 'Get the bot status'
            },
            {
                'path': '/api/history',
                'methods': ['GET'],
                'description': 'List history records'
            },
            {
                'path': '/api/history/<record_id>',
                'methods': ['GET'],
                'description': 'Get history record details'
            },
            {
                'path': '/api/email/test',
                'methods': ['POST'],
                'description': 'Test email configuration'
            },
            {
                'path': '/api/subscription/history',
                'methods': ['GET'],
                'description': 'Get subscription history'
            },
            {
                'path': '/api/conference/run',
                'methods': ['POST'],
                'description': 'Trigger conference paper fetch and subscription pipeline'
            },
            {
                'path': '/api/conference/fetch',
                'methods': ['POST'],
                'description': 'Trigger conference paper fetch only'
            },
            {
                'path': '/api/conference/subscription',
                'methods': ['POST'],
                'description': 'Trigger conference subscription only'
            },
            {
                'path': '/api/conference/output',
                'methods': ['GET'],
                'description': 'List all conference output files'
            },
            {
                'path': '/api/conference/output/<filename>',
                'methods': ['GET', 'DELETE'],
                'description': 'Get or delete conference output file'
            },
            {
                'path': '/api/conference/subscription/history',
                'methods': ['GET'],
                'description': 'Get conference subscription history'
            },
            {
                'path': '/api/conference/scheduler/start',
                'methods': ['POST'],
                'description': 'Start conference paper scheduler'
            },
            {
                'path': '/api/conference/scheduler/stop',
                'methods': ['POST'],
                'description': 'Stop conference paper scheduler'
            },
            {
                'path': '/api/conference/scheduler/status',
                'methods': ['GET'],
                'description': 'Get conference scheduler status'
            },
            {
                'path': '/api/conference/scheduler/test',
                'methods': ['POST'],
                'description': 'Test conference scheduler immediate run'
            }
        ]
    }
    return jsonify(docs)

if __name__ == '__main__':
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=8001)
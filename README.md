# 📚 arXiv RSS Filter Bot with Conference Extension
# arXiv RSS 过滤机器人 + 顶级会议论文推送

🎯 **智能学术论文推送系统** - 自动从arXiv获取最新论文，并支持从OpenReview获取顶级AI和安全会议的高质量论文。根据您的研究兴趣进行智能过滤，提取作者和机构信息，并生成个性化RSS订阅源。支持现代化Web界面和智能邮件推送系统。

[English](#features) | [中文说明](#功能特性)

## Features

### 🚀 **Core Features**
- ✅ **Dual Paper Source**: arXiv API + OpenReview for comprehensive coverage
- ✅ **Intelligent Filtering**: Advanced keyword and category-based filtering
- ✅ **Smart Scheduling**: Customizable push frequencies for different sources
- ✅ **Modern Web Interface**: Vue.js dashboard with real-time status monitoring
- ✅ **Email Subscription**: HTML-formatted emails with categorized papers
- ✅ **API-First Design**: Complete REST API for integration and automation

### 📖 **arXiv Integration**
- ✅ **Automatic Paper Fetching**: Uses arXiv API to fetch the latest papers from specified categories
- ✅ **Keyword Filtering**: Filters papers based on keywords in title and abstract
- ✅ **Date-based Filtering**: Only keeps papers published within a specified time range
- ✅ **Specific Period Filtering**: Filter papers by specific year and/or month
- ✅ **Author Information Extraction**: Extracts and displays author names and affiliations
- ✅ **Extended Time Range**: Support for fetching papers up to 365 days old
- ✅ **Daily Push**: Automated daily delivery at 7:00 AM

### 🎓 **Conference Paper Integration** ⭐ **NEW**
- ✅ **Top-Tier Conferences**: ICLR, NeurIPS, ICML, AAAI, IJCAI for AI/ML
- ✅ **Security Conferences**: IEEE S&P, CCS, USENIX Security, NDSS, AISec for security
- ✅ **Cryptography Conferences**: CRYPTO, EUROCRYPT for cryptographic research  
- ✅ **OpenReview Integration**: Direct access to peer-reviewed conference papers
- ✅ **Smart Categorization**: AI/ML, Security, Cryptography, and AI Security categories
- ✅ **Flexible Scheduling**: Monthly pushes for AI/ML, quarterly for security conferences
- ✅ **Automatic Scheduler**: Background job system with configurable triggers

### 🎯 **Advanced Features**
- ✅ **RSS Generation**: Automatically generates an RSS feed compatible with any reader
- ✅ **Comprehensive Logging**: Detailed logs to track every step of the process
- ✅ **Robust Error Handling**: Fallback mechanisms for API issues and timezone handling
- ✅ **Historical Records**: Saves historical query results for future reference and comparison
- ✅ **Pagination Support**: Browse through large sets of filtered papers with ease
- ✅ **Batch Processing**: Efficiently processes large numbers of papers in batches
- ✅ **Duplicate Prevention**: Advanced tracking to prevent duplicate paper delivery

## Requirements

- Python 3.7+
- Node.js 18+ (for web interface)
- Required Python packages:
  - feedparser
  - pyyaml
  - feedgen
  - requests
  - arxiv
  - apscheduler
  - flask (for API)
  - flask-cors
  - smtplib (for email functionality)

## 🚀 **Quick Start**

### Option 1: Complete Setup (Recommended)
```bash
# Clone repository
git clone https://github.com/Minfeng-Qi/arxiv_rss_bot.git
cd arxiv_rss_bot

# Install dependencies
pip install -r requirements.txt

# Configure your settings
cp config.yaml.example config.yaml
nano config.yaml

# Start the API server
python api.py

# Access the web interface at http://localhost:8001
```

### Option 2: Docker Deployment (Coming Soon)
```bash
docker run -p 8001:8001 -v $(pwd)/config.yaml:/app/config.yaml arxiv-bot:latest
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Minfeng-Qi/arxiv_rss_bot.git
cd arxiv_rss_bot
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. Install Node.js dependencies for the web interface:
```bash
cd frontend
npm install
cd ..
```

4. Configure your preferences in `config.yaml` (see [Configuration](#configuration) section) or use the web interface

## Usage

### Run Complete Application (API + Web Interface)

To start both the API backend and web interface:

```bash
./run_app.sh
```

Then open your browser to:
- Web Interface: http://localhost:5173
- API: http://localhost:8000

### Run Backend Only

To fetch papers, filter them, and generate an RSS file immediately:

```bash
python main.py
```

### Schedule Daily Runs

To run the bot on a schedule (it will run daily at the hour specified in the config):

```bash
python main.py --schedule
```

### Run Frontend Development Server

```bash
cd frontend
npm run dev
```

## Configuration

You can configure the system either through the web interface or by editing `config.yaml`:

```yaml
# config.yaml
keywords:
  - reinforcement learning
  - LLM agents
  - large language model
  - foundation model
  - multimodal
max_days_old: 365    # Only include papers published within this many days (up to 365)
max_results: 1000    # Maximum papers to include in the final output
categories:          # arXiv categories to fetch from
  - cs.AI           # Artificial Intelligence
  - cs.LG           # Machine Learning
  - cs.CL           # Computation and Language
run_hour: 7          # Hour of day to run when scheduled (24h format) - arXiv papers at 7:00 AM
email_on_error: true # Send email on error
author_weight: 0.2   # Weight for author matching
recency_weight: 0.3  # Weight for recency in ranking
email:               # Email configuration for notifications
  smtp_server: smtp.gmail.com
  port: 587
  username: your_email@gmail.com
  password: your_app_password  # Use app password for Gmail
  recipient: your_email@gmail.com
history_enabled: true # Enable saving historical records of query results
email_subscription: true # Enable email subscription for new papers

# ⭐ NEW: Conference Paper Configuration
conferences:
  enabled: true  # Enable conference paper fetching
  openreview:
    baseurl: https://api2.openreview.net
    username: ""  # Optional: OpenReview username (leave empty for anonymous access)
    password: ""  # Optional: OpenReview password
  
  # Conference push settings
  conference_email:
    enabled: true  # Enable conference paper email subscription
    subject_prefix: "[Conference Papers]"
    separate_by_category: true

# Optional: Filter papers by specific year and/or month  
# date_range:
#   year: 2025      # Optional: Specify a year
#   month: 5        # Optional: Specify a month (1-12)
```

## Web Interface

The web interface provides an intuitive way to manage the arXiv RSS Filter Bot:

### Dashboard
- View configuration summary
- See latest feed information
- Check paper statistics
- Run the bot on demand
- View recent activity
- Monitor email subscription status

### Configuration
- Edit keywords for filtering
- Select arXiv categories
- Set filter parameters (max results, date ranges)
- Configure scheduling
- Set up error notifications
- Configure email subscription settings

### Feeds
- View generated feeds
- Browse filtered papers with pagination
- See author and institution information
- Access paper PDFs and abstracts
- Copy RSS feed URLs for use in feed readers
- Download RSS feeds directly

### History
- Browse historical query results
- View details of past queries including keywords and categories
- See matched papers for each historical record
- Download historical RSS files
- Compare results over time

## Email Subscription

The system supports automatic sending of latest papers to specified email, avoiding sending duplicate papers.

### Configure Email Subscription

Set the following in `config.yaml` or through the web interface:

```yaml
email_subscription: true  # Enable email subscription
email:
  smtp_server: smtp.gmail.com
  port: 587
  username: your_email@gmail.com
  password: your_app_password  # Use app password for Gmail
  recipient: your_email@gmail.com
```

### Running

1. **Manually**: `python3 email_subscription.py`
2. **Scheduled**: `python3 main.py --schedule` (will run daily at the specified hour)

### Avoid Duplicate Sending

The system records sent paper IDs to avoid sending the same paper again. Sent papers are saved in `subscription_history.json`.

## 📡 **API Endpoints**

The backend provides a comprehensive REST API (v1.1.0) with 21+ endpoints:

### **Core arXiv API**
- `GET /api/config` - Get current configuration
- `POST /api/config` - Update configuration  
- `POST /api/run` - Run complete pipeline (RSS + email)
- `POST /api/run/rss-only` - ⭐ **NEW** Run RSS generation only (no email)
- `GET /api/status` - Get bot status and paper statistics
- `GET /api/logs` - Get recent application logs

### **Feed Management**
- `GET /api/output` - List all generated RSS files
- `GET /api/output/<filename>` - Get/delete specific RSS file content
- `GET /api/history` - Get historical records with pagination
- `GET /api/history/<record_id>` - Get specific historical record details

### **Email & Subscription**
- `POST /api/email/test` - Test email configuration
- `GET /api/subscription/history` - Get arXiv subscription history

### **⭐ Conference Paper API (NEW)**
- `POST /api/conference/run` - Run complete conference pipeline
- `POST /api/conference/fetch` - Fetch conference papers only
- `POST /api/conference/subscription` - Send conference emails only
- `GET /api/conference/output` - List conference paper files
- `GET /api/conference/output/<filename>` - Get/delete conference files
- `GET /api/conference/subscription/history` - Get conference subscription history

### **⭐ Scheduler Management (NEW)**
- `POST /api/conference/scheduler/start` - Start conference scheduler
- `POST /api/conference/scheduler/stop` - Stop conference scheduler
- `GET /api/conference/scheduler/status` - Get scheduler status and next runs
- `POST /api/conference/scheduler/test` - Test immediate scheduler run

### **Documentation**
- `GET /api/docs` - Get complete API documentation

## 🕐 **Push Schedule Overview**

| **Source** | **Frequency** | **Time** | **Content** |
|-----------|--------------|----------|-------------|
| arXiv | Daily | 7:00 AM | Latest papers from your categories |
| AI/ML Conferences | Monthly | 1st day, 9:00 AM | ICLR, NeurIPS, ICML, AAAI, IJCAI |
| Security Conferences | Quarterly | 1st day, 10:00 AM | IEEE S&P, CCS, USENIX, NDSS, AISec |
| Daily Check | Daily | 8:00 AM | System health and special updates |

## Filtering System

Papers are filtered based on several criteria:

1. **Keyword Matching**: Papers containing your keywords in the title or abstract are included
   - If no keywords are specified, all papers pass this filter
   - The RSS output will show which keywords matched for each paper
   - Multi-word keywords are properly supported for precise matching

2. **Date Filtering**: Only papers published or updated within the specified time range are included
   - You can include papers up to 365 days old
   - Adjust this by changing the `max_days_old` parameter in the config file

3. **Period Filtering**: Optionally filter papers by specific year and/or month
   - You can specify a year, a month, or both in the `date_range` configuration
   - When both year and month are specified, only papers from that specific period will be included
   - When only year is specified, papers from any month of that year will be included
   - When only month is specified, papers from that month of any year will be included

## Extended Time Range Support

The system now supports fetching papers up to 365 days old:

- Uses batch fetching for efficient retrieval of older papers
- Automatically divides requests into manageable time periods
- Handles arXiv API limitations gracefully
- Provides comprehensive coverage of papers from the past year

## Output Files

- **RSS Feed**: `output/YYYYMMDD_HHMMSS_KW.xml` (where KW is an abbreviation of keywords)
- **Logs**: `logs/arxiv_rss_bot_YYYYMMDD.log`
- **History Records**: `history/UUID.json`
- **Subscription History**: `subscription_history.json`

## Customizing arXiv Categories

You can fetch papers from any combination of arXiv categories. For a complete list, see the [arXiv category taxonomy](https://arxiv.org/category_taxonomy).

Popular categories:
- `cs.AI`: Artificial Intelligence
- `cs.LG`: Machine Learning
- `cs.CL`: Computation and Language (NLP)
- `cs.CV`: Computer Vision
- `cs.RO`: Robotics
- `stat.ML`: Statistics - Machine Learning
- `cs.DB`: Databases
- `cs.IR`: Information Retrieval
- `cs.HC`: Human-Computer Interaction

## 功能特性

- ✅ **自动获取论文**: 使用arXiv API获取指定类别的最新论文
- ✅ **关键词过滤**: 根据标题和摘要中的关键词过滤论文
- ✅ **日期过滤**: 仅保留指定时间范围内发布的论文
- ✅ **特定时期过滤**: 按特定年份和/或月份过滤论文
- ✅ **作者信息提取**: 提取并显示作者姓名和所属机构
- ✅ **RSS生成**: 自动生成兼容任何阅读器的RSS订阅源
- ✅ **Web界面**: 现代化Vue.js仪表盘，便于配置和管理订阅源
- ✅ **定时运行**: 可按照设定的时间每天自动运行
- ✅ **错误通知**: 可配置的邮件错误提醒系统
- ✅ **邮件订阅**: 自动发送新论文到邮箱，避免重复发送
- ✅ **全面日志记录**: 详细记录每一步操作的日志
- ✅ **灵活配置**: 通过UI界面或配置文件轻松自定义所有参数
- ✅ **健壮的错误处理**: 针对API问题和时区处理的备用机制
- ✅ **历史记录**: 保存查询结果的历史记录，便于将来参考和比较
- ✅ **分页支持**: 轻松浏览大量已过滤的论文
- ✅ **扩展时间范围**: 支持获取长达365天前的论文
- ✅ **批量处理**: 高效处理大量论文的批处理功能

## 系统要求

- Python 3.7+
- Node.js 18+ (用于Web界面)
- 所需Python依赖包:
  - feedparser
  - pyyaml
  - feedgen
  - requests
  - arxiv
  - apscheduler
  - flask (用于API)
  - flask-cors

## 安装方法

1. 克隆此仓库:
```bash
git clone https://github.com/Minfeng-Qi/arxiv_rss_bot.git
cd arxiv_rss_bot
```

2. 安装所需的Python依赖包:
```bash
pip install -r requirements.txt
```

3. 安装Web界面的Node.js依赖:
```bash
cd frontend
npm install
cd ..
```

4. 在`config.yaml`中配置您的偏好设置(参见[配置说明](#配置说明)部分)或使用Web界面

## 使用方法

### 运行完整应用(API + Web界面)

启动后端API和Web界面:

```bash
./run_app.sh
```

然后在浏览器中打开:
- Web界面: http://localhost:5173
- API: http://localhost:8000

### 仅运行后端

立即获取论文、过滤并生成RSS文件:

```bash
python main.py
```

### 设置定时运行

按照预定计划运行机器人(将在配置中指定的小时每天运行):

```bash
python main.py --schedule
```

## 配置说明

您可以通过Web界面或编辑`config.yaml`来配置系统:

```yaml
# config.yaml
keywords:
  - reinforcement learning
  - LLM agents
  - large language model
  - foundation model
  - multimodal
max_days_old: 365    # 仅包含在此天数内发布的论文（最多365天）
max_results: 1000    # 最终输出中包含的最大论文数量
categories:          # 要获取的arXiv类别
  - cs.LG           # 机器学习
  - cs.AI           # 人工智能
  - cs.CL           # 计算与语言(NLP)
run_hour: 8          # 定时运行时的小时(24小时制)
email_on_error: true # 出错时发送邮件
author_weight: 0.2   # 作者匹配的权重
recency_weight: 0.3  # 时效性在排名中的权重
email:               # 邮件配置
  smtp_server: smtp.gmail.com
  port: 587
  username: your_email@gmail.com
  password: your_password
  recipient: your_email@gmail.com
history_enabled: true # 启用保存查询结果的历史记录
email_subscription: true # 启用邮件订阅新论文

# 可选：按特定年份和/或月份过滤论文
# date_range:
#   year: 2025      # 可选：指定年份
#   month: 5        # 可选：指定月份（1-12）
```

## Web界面

Web界面提供了直观的方式来管理arXiv RSS过滤机器人:

### 仪表盘
- 查看配置摘要
- 查看最新订阅源信息
- 查看论文统计数据
- 按需运行机器人
- 查看最近活动
- 监控邮件订阅状态

### 配置
- 编辑过滤用的关键词
- 选择arXiv类别
- 设置过滤参数（最大结果数，日期范围）
- 配置定时计划
- 设置错误通知
- 配置邮件订阅设置

### 订阅源
- 查看生成的订阅源
- 使用分页浏览已过滤的论文
- 查看作者和机构信息
- 访问论文PDF和摘要
- 复制RSS订阅源URL，用于订阅阅读器
- 直接下载RSS订阅源

## 邮件订阅

系统支持自动发送最新论文到指定邮箱，避免发送重复的论文。

### 配置邮件订阅

在 `config.yaml` 或通过Web界面设置：

```yaml
email_subscription: true  # 是否启用邮件订阅功能
email:
  smtp_server: smtp.gmail.com
  port: 587
  username: your_email@gmail.com
  password: your_password  # 对于Gmail，请使用应用专用密码
  recipient: your_email@gmail.com
```

### 运行方式

1. **手动运行**：`python3 email_subscription.py`
2. **定时运行**：`python3 main.py --schedule`（将在每天配置的时间自动运行）

### 避免重复发送

系统会记录已发送的论文ID，避免重复发送同一篇论文。历史记录保存在 `subscription_history.json` 文件中。

## API接口

后端API支持以下接口:

- `GET /api/config` - 获取当前配置
- `POST /api/config` - 更新配置
- `POST /api/run` - 手动运行RSS机器人
- `GET /api/output` - 列出所有生成的RSS文件
- `GET /api/output/<filename>` - 获取特定RSS文件内容
- `GET /api/status` - 获取机器人状态信息
- `GET /api/logs` - 获取最近日志
- `GET /api/history` - 获取历史记录列表（带分页）
- `GET /api/history/<record_id>` - 获取特定历史记录的详细信息
- `GET /api/subscription/history` - 获取订阅历史记录
- `POST /api/email/test` - 测试邮件配置

## 过滤系统

论文基于多个标准进行过滤:

1. **关键词匹配**: 标题或摘要中包含您关键词的论文将被包含
   - 如果未指定关键词，所有论文都通过此过滤器
   - RSS输出将显示每篇论文匹配了哪些关键词
   - 正确支持多词关键词以进行精确匹配

2. **日期过滤**: 仅包含在指定时间范围内发布或更新的论文
   - 可以包含长达365天前的论文
   - 您可以通过更改配置文件中的`max_days_old`参数来调整此范围

3. **时期过滤**: 可选择按特定年份和/或月份过滤论文
   - 您可以在`date_range`配置中指定年份、月份或两者都指定
   - 当同时指定年份和月份时，只有该特定时期的论文会被包含
   - 当只指定年份时，该年份任何月份的论文都会被包含
   - 当只指定月份时，任何年份该月份的论文都会被包含

## 扩展时间范围支持

系统现在支持获取长达365天前的论文：

- 使用批量获取方式高效检索较旧的论文
- 自动将请求分为可管理的时间段
- 优雅处理arXiv API的限制
- 提供对过去一年论文的全面覆盖

## 输出文件

- **RSS订阅源**: `output/YYYYMMDD_HHMMSS_KW.xml`（其中KW是关键词的缩写）
- **日志**: `logs/arxiv_rss_bot_YYYYMMDD.log`
- **历史记录**: `history/UUID.json`
- **订阅历史**: `subscription_history.json`

## 自定义arXiv类别

您可以获取任意组合的arXiv类别的论文。完整列表请参见[arXiv类别分类](https://arxiv.org/category_taxonomy)。

常用类别:
- `cs.AI`: 人工智能
- `cs.LG`: 机器学习
- `cs.CL`: 计算与语言(自然语言处理)
- `cs.CV`: 计算机视觉
- `cs.RO`: 机器人学
- `stat.ML`: 统计-机器学习
- `cs.DB`: 数据库
- `cs.IR`: 信息检索
- `cs.HC`: 人机交互
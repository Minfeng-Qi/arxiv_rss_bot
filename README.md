# arXiv RSS Filter Bot with AI Analysis

一个智能的arXiv论文过滤和分析系统，具备完整的工作流程：**论文获取 → 邮件推送 → 智能精选 → AI分析 → Notion同步**

## ✨ 核心特性

- 🔍 **智能论文获取**: 从arXiv自动获取最新的机器学习、人工智能相关论文
- 📧 **快速邮件推送**: 优先发送论文列表，让用户快速获得最新信息
- 🎯 **智能精选分析**: 从推送论文中智能筛选最有价值的进行AI分析
- 🤖 **AI深度分析**: 使用DeepSeek AI对精选论文进行中文深度分析和总结
- 📝 **真实数据保障**: 确保所有数据（标题、作者、日期）都来自真实arXiv论文
- 🗃️ **Notion集成**: 自动将AI分析结果保存到Notion数据库
- ⏰ **定时自动化**: 每天定时运行，无需人工干预
- 🛡️ **智能监控**: 完善的错误处理和重试机制

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆仓库
git clone https://github.com/Minfeng-Qi/arxiv_rss_bot.git
cd arxiv_rss_bot

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或在Windows上: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置设置

编辑 `config.yaml` 配置以下信息：

```yaml
# 基础设置
keywords:
  - "reinforcement learning"
  - "LLM agents"
  - "large language model"
  - "foundation model"
  - "multimodal"

run_hour: 7  # 每天运行时间（24小时制）
email_subscription: true

# 邮件配置
email:
  smtp_server: "smtp.163.com"
  port: 465  # SSL端口
  username: "your-email@163.com"
  password: "your-app-password"
  recipient: "recipient@gmail.com"

# AI分析配置
ai_analysis:
  auto_analysis_enabled: true
  max_papers_per_batch: 20
  
  # DeepSeek AI配置
  deepseek:
    enabled: true
    api_key: "your-deepseek-api-key"  # 从 https://platform.deepseek.com 获取
    
  # Notion集成配置  
  notion:
    enabled: true
    integration_token: "your-notion-integration-token"
    database_id: "your-notion-database-id"
    
  # 智能精选配置
  smart_selection:
    enabled: true
    min_score_threshold: 0.6  # 最低分数阈值
```

### 3. 启动服务

#### 后台运行（推荐）
```bash
# 启动完整服务（调度器 + API）
./run_background.sh

# 查看运行状态
ps aux | grep python

# 查看日志
tail -f logs/scheduler_output.log
```

#### 手动运行
```bash
# 一次性运行完整流程
python main.py

# 仅发送邮件订阅
python email_subscription.py

# 仅运行AI分析
python paper_analysis_pipeline.py
```

## 📊 工作流程

### 优化后的执行顺序

1. **📚 论文获取** (2-3分钟)
   - 从arXiv获取最新论文
   - 根据关键词和分类过滤
   - 生成RSS订阅源

2. **📧 邮件推送** (立即)
   - 快速发送分类整理的论文邮件
   - 用户可立即开始阅读论文
   - 避免等待AI分析完成

3. **🎯 智能精选** (1分钟)
   - 从推送的论文中智能筛选
   - 基于多维度评分算法
   - 选择最有价值的论文进行AI分析

4. **🤖 AI分析** (10-15分钟)
   - 使用DeepSeek AI深度分析精选论文
   - 生成中文总结和见解
   - 确保所有数据真实可靠

5. **📝 Notion同步** (2-3分钟)
   - 将AI分析结果保存到Notion数据库
   - 包含完整的真实论文信息
   - 自动分类和标签

### 智能精选算法

评分维度权重：
- **基础分数**: 50%
- **关键词匹配**: 40% (高价值关键词额外加分)
- **时效性**: 20% (最新论文优先)
- **作者权威性**: 10% (多作者合作加分)
- **论文质量**: 10% (详细摘要加分)
- **LLM相关性**: 20% (相关术语加分)

## 📝 Notion数据库结构

系统会在Notion中创建包含以下字段的数据库：

| 字段名 | 类型 | 描述 |
|--------|------|------|
| 标题 | Title | 论文标题 |
| 论文ID | Rich Text | arXiv ID |
| 作者 | Rich Text | 作者列表 |
| 分析日期 | Date | AI分析日期 |
| 发布日期 | Date | 论文发布日期 |
| 重要性 | Select | 高/中/低 |
| 分类 | Select | LLM&AI Agents/Multimodal&Vision等 |
| 是否LLM相关 | Checkbox | 自动判断 |
| 状态 | Select | 分析状态 |
| 论文链接 | URL | arXiv链接 |

## 🔧 管理命令

### 服务管理
```bash
# 启动服务
./run_background.sh

# 停止服务
./stop_services.sh

# 查看服务状态
ps aux | grep "main.py\|api.py"

# 查看进程ID
cat scheduler.pid
cat api.pid
```

### 日志查看
```bash
# 调度器日志
tail -f logs/scheduler_output.log

# API服务日志
tail -f logs/api_output.log

# 今日运行日志
tail -f logs/arxiv_rss_bot_$(date +%Y%m%d).log
```

### 数据管理
```bash
# 查看Notion数据库
python notion_manager.py

# 查看分析结果
ls -la analysis_results/

# 查看生成的RSS
ls -la output/
```

## ⚙️ 高级配置

### 自定义关键词权重
```yaml
# 在config.yaml中调整
recency_weight: 0.3  # 时效性权重
author_weight: 0.2   # 作者权重
max_days_old: 365    # 论文时间范围（天）
```

### 邮件分类配置
```yaml
paper_categories:
  🤖 LLM & AI Agents:
    - "large language model"
    - "LLM agents"
    - "AI agent"
  🎨 Multimodal & Vision:
    - "multimodal"
    - "computer vision"
    - "vision-language"
```

## 🛡️ 数据安全

### 真实数据保障
- ✅ 所有论文ID来自真实arXiv
- ✅ 标题和作者信息保持原样
- ✅ 发布日期使用论文实际发布时间
- ✅ AI分析基于真实论文内容
- ❌ 绝不生成虚假或测试数据

### API密钥安全
- 配置文件不要提交到版本控制
- 使用环境变量存储敏感信息
- 定期轮换API密钥

## 📈 监控和调试

### 性能监控
```bash
# 查看系统资源使用
htop

# 查看网络连接
netstat -tulpn | grep python

# 查看磁盘使用
df -h
du -sh logs/ output/ analysis_results/
```

### 常见问题

**Q: 邮件发送失败**
```bash
# 检查邮件配置
python -c "from email_subscription import *; test_email_config()"
```

**Q: AI分析失败**
```bash
# 检查DeepSeek API
python -c "from deepseek_analyzer import *; test_deepseek_connection()"
```

**Q: Notion同步失败**
```bash
# 检查Notion连接
python -c "from notion_integrator import *; test_notion_connection()"
```

## 🎯 最佳实践

1. **定期备份**: 备份重要的分析结果和配置
2. **监控日志**: 定期检查错误日志，及时处理异常
3. **API配额**: 注意DeepSeek API的使用配额限制
4. **数据清理**: 定期清理过期的日志和临时文件

## 📞 支持

- 遇到问题请查看 `logs/` 目录下的日志文件
- 系统会自动重试失败的操作
- 重要数据都有本地备份

---

**由 [Claude Code](https://claude.ai/code) 协助开发** 🤖

*最后更新: 2025-08-20*
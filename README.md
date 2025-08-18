# arXiv RSS Filter Bot with AI Analysis

一个智能的arXiv论文过滤和分析系统，具备以下功能：

- 🔍 **智能论文获取**: 从arXiv自动获取最新的机器学习、人工智能相关论文
- 🎯 **智能分类筛选**: 根据关键词和分类智能筛选相关论文
- 🤖 **AI深度分析**: 使用DeepSeek AI对论文进行中文深度分析和总结
- 📝 **Notion集成**: 自动将分析结果保存到Notion数据库
- 📧 **邮件订阅**: 支持邮件推送和RSS订阅
- 🛡️ **智能监控**: 自动监控分析质量，失败时自动恢复
- 🔄 **容错机制**: 完善的重试和错误处理机制

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆仓库
git clone https://github.com/Minfeng-Qi/arxiv_rss_bot.git
cd arxiv_rss_bot

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置设置

复制配置文件模板：
```bash
cp config.example.yaml config.yaml
```

编辑 `config.yaml` 配置以下信息：

```yaml
# AI论文分析配置
ai_analysis:
  # DeepSeek AI配置
  deepseek:
    enabled: true
    api_key: "your-deepseek-api-key"  # 从 https://platform.deepseek.com 获取
    
  # Notion集成配置  
  notion:
    enabled: true
    integration_token: "your-notion-integration-token"  # 从 Notion 集成页面获取
    database_id: "your-notion-database-id"  # Notion 数据库 ID
```

### 3. 运行系统

#### 一次性运行
```bash
python main.py
```

#### 定时运行（推荐）
```bash
# 设置定时任务（每天7:00运行）
python main.py --schedule
```

#### 设置监控系统
```bash
# 运行设置脚本
./setup_monitoring.sh
```

## 📊 主要功能

### AI论文分析
- 使用DeepSeek AI进行深度分析
- 自动生成中文论文总结
- 智能分类和质量评估
- 每日最多分析20篇高质量论文

### 智能监控
- 自动检查分析结果完整性
- 失败时自动恢复
- 详细的日志和错误追踪
- 系统健康状态监控

### 数据集成
- Notion数据库自动同步
- 本地JSON文件备份
- RSS订阅源生成
- 邮件推送支持

## 🛡️ 容错和监控

系统具备完善的容错机制：
- API调用重试（3次，间隔5秒）
- 文件完整性验证
- 自动质量检查
- 智能恢复机制

## 📝 配置说明

主要配置项：
- `max_papers_per_batch: 20` - 每批分析论文数量
- `auto_analysis_enabled: true` - 启用自动分析
- `smart_selection.enabled: true` - 智能论文筛选

## 🔧 部署

使用提供的脚本进行一键部署：
```bash
./setup_monitoring.sh
```

## ⚠️ 注意事项

- 请妥善保管API密钥，不要提交到版本控制
- 需要有效的DeepSeek API密钥和Notion集成令牌
- 建议定期备份重要的分析结果

---

**由 [Claude Code](https://claude.ai/code) 协助开发** 🤖
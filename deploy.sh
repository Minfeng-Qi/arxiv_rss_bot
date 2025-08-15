#!/bin/bash

# arXiv RSS Filter Bot 部署脚本
# 用于在服务器上设置和运行项目

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

echo -e "${BLUE}开始部署 arXiv RSS Filter Bot...${NC}"

# 创建必要的目录
mkdir -p output
mkdir -p logs
mkdir -p history
mkdir -p cache

# 检查Python虚拟环境
if [ ! -d ".venv" ]; then
    echo -e "${BLUE}创建Python虚拟环境...${NC}"
    python3 -m venv .venv
fi

# 激活虚拟环境
echo -e "${GREEN}激活虚拟环境...${NC}"
source .venv/bin/activate

# 安装依赖
echo -e "${BLUE}安装Python依赖...${NC}"
pip install -r requirements.txt

# 创建系统服务文件
echo -e "${BLUE}创建系统服务文件...${NC}"

# 获取当前目录的绝对路径
CURRENT_DIR=$(pwd)
USER=$(whoami)

# 创建调度器服务文件
echo -e "${GREEN}创建调度器服务文件...${NC}"
cat > arxiv-scheduler.service << EOF
[Unit]
Description=arXiv RSS Filter Bot Scheduler
After=network.target

[Service]
User=${USER}
WorkingDirectory=${CURRENT_DIR}
ExecStart=${CURRENT_DIR}/.venv/bin/python main.py --schedule
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 创建API服务文件
echo -e "${GREEN}创建API服务文件...${NC}"
cat > arxiv-api.service << EOF
[Unit]
Description=arXiv RSS Filter Bot API
After=network.target

[Service]
User=${USER}
WorkingDirectory=${CURRENT_DIR}
ExecStart=${CURRENT_DIR}/.venv/bin/python api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}服务文件已创建${NC}"
echo -e "${BLUE}要安装系统服务，请以root用户运行以下命令:${NC}"
echo -e "${RED}sudo cp arxiv-scheduler.service /etc/systemd/system/${NC}"
echo -e "${RED}sudo cp arxiv-api.service /etc/systemd/system/${NC}"
echo -e "${RED}sudo systemctl daemon-reload${NC}"
echo -e "${RED}sudo systemctl enable arxiv-scheduler.service${NC}"
echo -e "${RED}sudo systemctl enable arxiv-api.service${NC}"
echo -e "${RED}sudo systemctl start arxiv-scheduler.service${NC}"
echo -e "${RED}sudo systemctl start arxiv-api.service${NC}"

# 创建后台运行脚本（不使用systemd的替代方案）
echo -e "${BLUE}创建后台运行脚本...${NC}"
cat > run_background.sh << EOF
#!/bin/bash

# 激活虚拟环境
source .venv/bin/activate

# 创建必要的目录
mkdir -p output logs history cache

# 启动调度器（定时任务）
echo "启动arXiv RSS调度器..."
nohup python main.py --schedule > logs/scheduler_output.log 2>&1 &
echo \$! > scheduler.pid
echo "调度器已启动，PID: \$(cat scheduler.pid)"

# 启动API服务
echo "启动arXiv RSS API服务..."
nohup python api.py > logs/api_output.log 2>&1 &
echo \$! > api.pid
echo "API服务已启动，PID: \$(cat api.pid)"

echo "所有服务已启动"
echo "查看日志: tail -f logs/scheduler_output.log 或 tail -f logs/api_output.log"
EOF

# 创建停止脚本
echo -e "${BLUE}创建停止脚本...${NC}"
cat > stop_services.sh << EOF
#!/bin/bash

# 停止服务
if [ -f scheduler.pid ]; then
    echo "停止调度器..."
    kill \$(cat scheduler.pid) 2>/dev/null || echo "调度器已经停止"
    rm scheduler.pid
fi

if [ -f api.pid ]; then
    echo "停止API服务..."
    kill \$(cat api.pid) 2>/dev/null || echo "API服务已经停止"
    rm api.pid
fi

echo "所有服务已停止"
EOF

# 添加执行权限
chmod +x run_background.sh
chmod +x stop_services.sh

echo -e "${GREEN}部署准备完成!${NC}"
echo -e "${BLUE}你可以选择以下方式之一运行服务:${NC}"
echo -e "1. 使用systemd（推荐用于生产环境）:"
echo -e "   按照上面显示的命令安装并启动系统服务"
echo -e "2. 使用后台进程（简单方式）:"
echo -e "   运行 ./run_background.sh 启动服务"
echo -e "   运行 ./stop_services.sh 停止服务"
echo -e "${GREEN}完成!${NC}" 

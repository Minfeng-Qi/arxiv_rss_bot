#!/bin/bash

# 激活虚拟环境
source .venv/bin/activate

# 创建必要的目录
mkdir -p output logs history cache

# 启动调度器（定时任务）
echo "启动arXiv RSS调度器..."
nohup python main.py --schedule > logs/scheduler_output.log 2>&1 &
echo $! > scheduler.pid
echo "调度器已启动，PID: $(cat scheduler.pid)"

# 启动API服务
echo "启动arXiv RSS API服务..."
nohup python api.py > logs/api_output.log 2>&1 &
echo $! > api.pid
echo "API服务已启动，PID: $(cat api.pid)"

echo "所有服务已启动"
echo "查看日志: tail -f logs/scheduler_output.log 或 tail -f logs/api_output.log"

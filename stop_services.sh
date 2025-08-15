#!/bin/bash

# 停止服务
if [ -f scheduler.pid ]; then
    echo "停止调度器..."
    kill $(cat scheduler.pid) 2>/dev/null || echo "调度器已经停止"
    rm scheduler.pid
fi

if [ -f api.pid ]; then
    echo "停止API服务..."
    kill $(cat api.pid) 2>/dev/null || echo "API服务已经停止"
    rm api.pid
fi

echo "所有服务已停止"

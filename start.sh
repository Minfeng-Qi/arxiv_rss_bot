#!/bin/bash

# arXiv RSS Filter Bot Starter Script

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install or update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if running in scheduled mode
if [ "$1" == "--schedule" ]; then
    echo "Starting arXiv RSS Filter Bot in scheduled mode..."
    python3 main.py --schedule
else
    echo "Running arXiv RSS Filter Bot once..."
    python3 main.py
fi 
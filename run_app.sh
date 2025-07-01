#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting arXiv RSS Filter Bot Application...${NC}"

# Create necessary directories if they don't exist
mkdir -p output
mkdir -p logs

# Check if Python virtual environment exists
if [ -d "venv" ]; then
  echo -e "${GREEN}Activating virtual environment...${NC}"
  source venv/bin/activate
else
  echo -e "${BLUE}No virtual environment found. Using system Python...${NC}"
fi

# Start Flask API in background
echo -e "${GREEN}Starting API server on http://localhost:8000...${NC}"
python api.py &
API_PID=$!

# Give the API a moment to start
sleep 2

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
  echo -e "${RED}Error: frontend directory not found!${NC}"
  echo -e "${RED}Stopping API server...${NC}"
  kill $API_PID
  exit 1
fi

# Start the frontend development server
echo -e "${GREEN}Starting frontend development server on http://localhost:5173...${NC}"
cd frontend
npm run dev

# When the frontend server stops, also stop the API server
echo -e "${BLUE}Stopping API server...${NC}"
kill $API_PID

echo -e "${GREEN}All services stopped. Thank you for using arXiv RSS Filter Bot!${NC}"
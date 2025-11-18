#!/bin/bash

# Run script for Document Intelligence Platform

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Document Intelligence Platform...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Running setup...${NC}"
    ./setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Please run setup.sh first.${NC}"
    exit 1
fi

# Function to check if a service is running
check_service() {
    local port=$1
    local name=$2

    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✓ $name is running on port $port${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  $name is not running on port $port${NC}"
        return 1
    fi
}

# Check services
echo -e "${YELLOW}Checking services...${NC}"
check_service 5432 "PostgreSQL" || echo "  Start with: pg_ctl start"
check_service 6379 "Redis" || echo "  Start with: redis-server"

echo ""
echo -e "${BLUE}Choose how to run:${NC}"
echo "1) API only"
echo "2) Dashboard only"
echo "3) Both (recommended)"
echo "4) API + Dashboard + Celery worker"

read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo -e "${BLUE}Starting FastAPI backend...${NC}"
        python src/api/main.py
        ;;
    2)
        echo -e "${BLUE}Starting Streamlit dashboard...${NC}"
        streamlit run frontend/app.py
        ;;
    3)
        echo -e "${BLUE}Starting both API and Dashboard...${NC}"
        echo -e "${YELLOW}Opening two terminals...${NC}"

        # Start API in background
        python src/api/main.py &
        API_PID=$!

        # Wait a bit for API to start
        sleep 3

        # Start Streamlit
        streamlit run frontend/app.py

        # Cleanup on exit
        kill $API_PID
        ;;
    4)
        echo -e "${BLUE}Starting full stack (API + Dashboard + Celery)...${NC}"

        # Start API in background
        python src/api/main.py &
        API_PID=$!

        # Start Celery worker in background
        celery -A src.tasks worker --loglevel=info &
        CELERY_PID=$!

        # Wait a bit
        sleep 3

        # Start Streamlit
        streamlit run frontend/app.py

        # Cleanup on exit
        kill $API_PID $CELERY_PID
        ;;
    *)
        echo -e "${YELLOW}Invalid choice${NC}"
        exit 1
        ;;
esac

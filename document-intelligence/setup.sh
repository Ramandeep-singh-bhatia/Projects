#!/bin/bash

# Setup script for Document Intelligence Platform

set -e

echo "🚀 Setting up Document Intelligence Platform..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env file with your configuration${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p data/uploads data/processed data/samples logs
echo -e "${GREEN}✓ Directories created${NC}"

# Check for required services
echo -e "${YELLOW}Checking required services...${NC}"

# Check PostgreSQL
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL found${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL not found. Please install PostgreSQL 14+${NC}"
fi

# Check Redis
if command -v redis-cli &> /dev/null; then
    echo -e "${GREEN}✓ Redis found${NC}"
else
    echo -e "${YELLOW}⚠️  Redis not found. Please install Redis 7+${NC}"
fi

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys and configuration"
echo "2. Create PostgreSQL database: createdb document_intelligence"
echo "3. Start Redis: redis-server"
echo "4. Run the application: ./run.sh"
echo ""
echo "For more information, see README.md"

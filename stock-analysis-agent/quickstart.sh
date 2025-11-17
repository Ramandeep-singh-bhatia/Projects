#!/bin/bash

# Quick Start Script for Stock Analysis Agent
# Automates the initial setup process

set -e  # Exit on error

echo "=================================="
echo "Stock Analysis Agent - Quick Start"
echo "=================================="
echo ""
echo "⚠  DISCLAIMER: Educational tool only!"
echo "   NOT for actual trading decisions."
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    echo "❌ Error: Python 3.11 or higher required"
    echo "   Current version: $python_version"
    echo "   Please install Python 3.11+ and try again"
    exit 1
fi

echo "✓ Python version OK: $python_version"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install requirements
echo "Installing Python dependencies..."
echo "(This may take a few minutes...)"
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"
echo ""

# Download NLTK data
echo "Downloading NLP data for sentiment analysis..."
python3 -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('vader_lexicon', quiet=True); nltk.download('stopwords', quiet=True)" 2>/dev/null
echo "✓ NLP data downloaded"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p data logs
echo "✓ Directories created"
echo ""

# Initialize database and config
echo "Initializing system..."
python3 -m src.cli setup <<EOF
n
EOF
echo "✓ System initialized"
echo ""

# Run tests
echo "Running system tests..."
python3 -m src.cli test
echo ""

echo "=================================="
echo "✨ Setup Complete! ✨"
echo "=================================="
echo ""
echo "You can now use the system!"
echo ""
echo "Try these commands:"
echo "  • Get stock quote:    python -m src.cli market quote AAPL"
echo "  • Scan latest news:   python -m src.cli news scan"
echo "  • Analyze a stock:    python -m src.cli analyze stock TSLA"
echo "  • Show all commands:  python -m src.cli --help"
echo ""
echo "📚 For detailed guide, see: GETTING_STARTED.md"
echo ""
echo "To activate virtual environment in future sessions:"
echo "  source venv/bin/activate"
echo ""
echo "Happy learning! 📈"
echo ""

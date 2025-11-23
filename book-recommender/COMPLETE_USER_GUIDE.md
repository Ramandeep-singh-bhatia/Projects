# Intelligent Personal Book Recommender System
## Complete User Guide & Documentation

**Version 3.0.0**
*Last Updated: November 2025*

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [Getting Started](#3-getting-started)
4. [Installation Guide](#4-installation-guide)
5. [Configuration](#5-configuration)
6. [Running the Application](#6-running-the-application)
7. [User Guide](#7-user-guide)
8. [Features Deep Dive](#8-features-deep-dive)
9. [API Documentation](#9-api-documentation)
10. [Database Schema](#10-database-schema)
11. [Development Guide](#11-development-guide)
12. [Deployment Guide](#12-deployment-guide)
13. [Troubleshooting](#13-troubleshooting)
14. [FAQ](#14-faq)
15. [Appendix](#15-appendix)

---

# 1. Introduction

## 1.1 What is the Intelligent Personal Book Recommender System?

The Intelligent Personal Book Recommender System is a comprehensive, AI-powered application designed to enhance your reading journey. Unlike generic book recommendation services, this system learns your unique reading personality, tracks your growth, and provides personalized guidance on what to read next and when you're ready for challenging books.

## 1.2 Key Capabilities

**Core Features:**
- 📚 **AI-Powered Recommendations** - Get personalized book suggestions based on your reading DNA
- 🧬 **Reading DNA Profile** - Understand your reading personality and preferences
- ➕ **Manual Book Entry** - Add any book via search, ISBN, or manual entry
- 🤔 **"Should I Read This?"** - Evaluate if you're ready for specific books
- 🔮 **Future Reads Management** - Queue books you're not ready for yet
- 📊 **Reading Analytics** - Track your progress, stats, and growth
- 📖 **Reading Coach** - Get personalized reading plans and pacing advice
- 🔤 **Vocabulary Builder** - Learn new words with spaced repetition
- 📚 **Series Tracker** - Manage book series automatically
- 📅 **Annual Reports** - Year-end "Spotify Wrapped" style summaries

**What Makes It Special:**
- **Local-First**: All data stored on your device (SQLite database)
- **Privacy-Focused**: No data sharing with external services
- **AI-Enhanced**: Powered by Claude Sonnet 4.5 for intelligent insights
- **Library Integration**: Check Sno-Isle Libraries availability
- **Growth-Oriented**: Helps you expand your reading horizons systematically

## 1.3 Who Should Use This?

This system is perfect for:
- 📖 Avid readers who want to track and optimize their reading
- 🎯 People looking to expand their reading horizons systematically
- 📚 Readers who get overwhelmed by TBR (To Be Read) lists
- 🤓 Anyone who wants data-driven insights into their reading habits
- 👥 Book club members tracking multiple series and recommendations
- 🎓 Students building reading skills progressively

## 1.4 System Requirements

**Minimum Requirements:**
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Python**: 3.8 or higher
- **Node.js**: 14.x or higher
- **RAM**: 2GB minimum
- **Storage**: 500MB for application + database growth
- **Internet**: Required for AI features and book metadata

**Recommended:**
- **Python**: 3.10+
- **Node.js**: 16.x+
- **RAM**: 4GB+
- **Storage**: 2GB+
- **Internet**: Stable broadband connection

---

# 2. System Overview

## 2.1 Architecture

The system follows a modern full-stack architecture:

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │Dashboard │  │My Books  │  │Add Book  │  │Future   │ │
│  │  Page    │  │  Page    │  │  Modal   │  │ Reads   │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────┘
                           │
                    HTTP/REST API
                           │
┌─────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │              API Routes Layer                     │  │
│  │  /api/books  /api/enhanced  /api/manual          │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │              Services Layer                       │  │
│  │  • Recommendation Engine  • Reading Coach        │  │
│  │  • Book Analysis         • Evaluation Service    │  │
│  │  • Vocabulary Builder    • Series Tracker        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼───┐   ┌───▼────┐  ┌───▼─────┐
         │SQLite  │   │Claude  │  │External │
         │Database│   │AI API  │  │Book APIs│
         └────────┘   └────────┘  └─────────┘
```

## 2.2 Technology Stack

**Frontend:**
- **Framework**: React 18+ with TypeScript
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Charts**: Recharts for visualizations
- **Styling**: CSS3 with custom design system

**Backend:**
- **Framework**: FastAPI (Python)
- **Database**: SQLite with optimized indexes
- **AI**: Anthropic Claude Sonnet 4.5
- **External APIs**:
  - Google Books API
  - Open Library API
  - Free Dictionary API
  - Sno-Isle Libraries (web scraping)

**Development Tools:**
- **Package Managers**: pip (Python), npm (Node.js)
- **Version Control**: Git
- **API Documentation**: FastAPI automatic OpenAPI docs

## 2.3 Data Flow

### Book Recommendation Flow:
```
1. User selects genre
2. Frontend requests recommendations from backend
3. Backend fetches user's reading history from database
4. Backend calls Claude AI with user profile + history
5. Claude generates personalized recommendations
6. Backend fetches book metadata from external APIs
7. Backend checks Sno-Isle library availability
8. Results returned to frontend and displayed
```

### Book Evaluation Flow:
```
1. User requests evaluation for a book
2. Backend fetches book analysis from database (or generates if new)
3. Backend fetches user's Reading DNA profile
4. Backend calls Claude AI for readiness assessment
5. AI analyzes 5 factors and generates score (0-100)
6. If score < 75, suggest Future Reads or Prep Plan
7. Results displayed with actionable recommendations
```

## 2.4 Database Structure

The system uses SQLite with **30+ tables** organized into functional groups:

**Core Tables:**
- `books` - Book metadata
- `reading_log` - Reading activity tracking
- `user_preferences` - User settings

**AI & Recommendations:**
- `recommendations` - AI-generated suggestions
- `reading_dna_profile` - User's reading personality
- `book_analysis` - AI analysis of books
- `book_complexity` - Difficulty scoring

**Advanced Features:**
- `reading_plans` - Personalized reading roadmaps
- `future_reads` - Books queued for later
- `vocabulary` - Word learning system
- `book_series` - Series management
- `annual_reports` - Year-end summaries

**Tracking & Analytics:**
- `reading_stats` - Daily statistics
- `reading_sessions` - Session-level tracking
- `book_interactions` - All user interactions
- `readiness_checkpoints` - Progress monitoring

---

# 3. Getting Started

## 3.1 Quick Start (5 Minutes)

If you just want to get the app running quickly:

```bash
# 1. Clone the repository (if not already done)
cd /path/to/book-recommender

# 2. Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 4. Run backend
python -m app.main

# 5. In a new terminal, set up frontend
cd ../frontend
npm install
npm start

# 6. Open browser to http://localhost:3000
```

## 3.2 First-Time Setup Checklist

- [ ] Install Python 3.8+
- [ ] Install Node.js 14+
- [ ] Get Anthropic API key (https://console.anthropic.com)
- [ ] Clone/download the repository
- [ ] Install backend dependencies
- [ ] Install frontend dependencies
- [ ] Configure environment variables
- [ ] Initialize database
- [ ] Start backend server
- [ ] Start frontend development server
- [ ] Access application in browser

## 3.3 What You'll Need

### Anthropic API Key (Required for AI Features)

1. **Sign up**: Go to https://console.anthropic.com
2. **Create API Key**: Navigate to API Keys section
3. **Copy key**: Copy your API key (starts with `sk-ant-`)
4. **Add to .env**: Paste in backend/.env file

**Cost Estimates:**
- First $5 in credits are free
- Typical usage: $0.01-0.05 per book recommendation
- Heavy usage (100 evaluations/month): ~$5-10/month
- Light usage (10-20 evaluations/month): ~$1-2/month

### Optional: Sno-Isle Libraries

If you're in the Sno-Isle Libraries service area (Washington State):
- No setup needed - library checking works automatically
- Shows book availability and formats at local libraries

If you're elsewhere:
- The app still works fully - just won't show library availability
- You can modify `library_checker.py` to support your local library

---

# 4. Installation Guide

## 4.1 Prerequisites Installation

### 4.1.1 Install Python

**Windows:**
```bash
# Download from python.org
# Or use winget:
winget install Python.Python.3.11
```

**macOS:**
```bash
# Using Homebrew:
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Verify installation:**
```bash
python --version  # Should show Python 3.8+
pip --version
```

### 4.1.2 Install Node.js

**Windows:**
```bash
# Download from nodejs.org
# Or use winget:
winget install OpenJS.NodeJS
```

**macOS:**
```bash
# Using Homebrew:
brew install node
```

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs
```

**Verify installation:**
```bash
node --version  # Should show v14+
npm --version
```

### 4.1.3 Install Git (if not already installed)

**Windows:**
```bash
winget install Git.Git
```

**macOS:**
```bash
brew install git
```

**Linux:**
```bash
sudo apt install git
```

## 4.2 Clone the Repository

```bash
# Option 1: Clone from GitHub (if using version control)
git clone https://github.com/yourusername/book-recommender.git
cd book-recommender

# Option 2: If you already have the files
cd /path/to/book-recommender
```

## 4.3 Backend Setup

### 4.3.1 Create Virtual Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

### 4.3.2 Install Dependencies

```bash
# Make sure virtual environment is activated
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**What gets installed:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `anthropic` - Claude AI SDK
- `aiohttp` - Async HTTP client
- `beautifulsoup4` - Web scraping
- `pydantic` - Data validation
- `python-dotenv` - Environment management
- `python-multipart` - File upload support

### 4.3.3 Create Environment File

```bash
# Create .env file from example
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Required .env contents:**
```env
# Anthropic API Configuration
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# Database Configuration
DATABASE_PATH=./data/books.db

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000

# External APIs (Optional - defaults provided)
GOOGLE_BOOKS_API_KEY=  # Optional, works without it
```

### 4.3.4 Initialize Database

The database will be created automatically on first run, but you can initialize it manually:

```bash
python -c "from app.database.database import init_database; init_database()"
```

This creates:
- `./data/` directory
- `./data/books.db` SQLite database
- All 30+ tables with indexes

## 4.4 Frontend Setup

### 4.4.1 Install Node Modules

```bash
cd ../frontend

# Install all dependencies
npm install
```

**What gets installed:**
- `react` & `react-dom` - UI framework
- `react-router-dom` - Routing
- `axios` - HTTP client
- `recharts` - Charts and visualizations
- `typescript` - Type safety
- `@types/*` - TypeScript definitions

### 4.4.2 Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit .env
nano .env
```

**Required .env contents:**
```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000

# Optional: Enable debug mode
REACT_APP_DEBUG=false
```

### 4.4.3 Build Frontend (Optional)

For development, you'll use `npm start`. For production:

```bash
npm run build
# Creates optimized build in ./build directory
```

## 4.5 Verify Installation

### 4.5.1 Check Backend

```bash
cd backend

# Activate virtual environment if not already active
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run tests (if available)
pytest

# Check imports work
python -c "from app.main import app; print('✓ Backend OK')"
```

### 4.5.2 Check Frontend

```bash
cd frontend

# Check for errors
npm run build

# Should complete without errors
```

## 4.6 Common Installation Issues

### Issue: pip install fails with "externally managed environment"

**Solution (Linux):**
```bash
# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: npm install fails with permission errors

**Solution:**
```bash
# Fix npm permissions (macOS/Linux)
sudo chown -R $USER ~/.npm
npm install

# Or use nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
npm install
```

### Issue: Python version too old

**Solution:**
```bash
# Install specific Python version
# macOS:
brew install python@3.11

# Ubuntu:
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv
```

### Issue: SQLite database locked

**Solution:**
```bash
# Stop all running instances
pkill -f "python.*app.main"

# Remove lock if exists
rm -f ./data/books.db-wal ./data/books.db-shm
```

---

# 5. Configuration

## 5.1 Environment Variables

### 5.1.1 Backend Configuration (.env)

**Complete .env file with all options:**

```env
# ============================================
# ANTHROPIC API CONFIGURATION (Required)
# ============================================
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# ============================================
# DATABASE CONFIGURATION
# ============================================
# Path to SQLite database file
DATABASE_PATH=./data/books.db

# Database connection pool settings
DB_TIMEOUT=30
DB_CHECK_SAME_THREAD=False

# ============================================
# SERVER CONFIGURATION
# ============================================
# Host to bind to (0.0.0.0 for all interfaces)
API_HOST=0.0.0.0

# Port to run on
API_PORT=8000

# Enable auto-reload on code changes (dev only)
API_RELOAD=true

# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# ============================================
# EXTERNAL API KEYS (Optional)
# ============================================
# Google Books API (works without, but better with)
GOOGLE_BOOKS_API_KEY=

# ============================================
# FEATURE FLAGS
# ============================================
# Enable/disable features
ENABLE_LIBRARY_CHECKING=true
ENABLE_AI_FEATURES=true
ENABLE_EXTERNAL_APIS=true

# ============================================
# AI MODEL CONFIGURATION
# ============================================
# Claude model to use
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# Temperature settings (0-1, higher = more creative)
AI_TEMPERATURE_RECOMMENDATIONS=0.7
AI_TEMPERATURE_ANALYSIS=0.6
AI_TEMPERATURE_EVALUATION=0.7

# Max tokens for AI responses
AI_MAX_TOKENS=4096

# ============================================
# CACHING CONFIGURATION
# ============================================
# Cache recommendations for N hours
RECOMMENDATION_CACHE_HOURS=24

# Cache book analysis for N days
ANALYSIS_CACHE_DAYS=30

# ============================================
# RATE LIMITING
# ============================================
# Max requests per minute (per IP)
RATE_LIMIT_PER_MINUTE=60

# Max concurrent AI requests
MAX_CONCURRENT_AI_REQUESTS=5

# ============================================
# CORS CONFIGURATION
# ============================================
# Allowed origins (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Enable credentials
ALLOW_CREDENTIALS=true
```

### 5.1.2 Frontend Configuration (.env)

**Complete .env file for frontend:**

```env
# ============================================
# API CONFIGURATION
# ============================================
# Backend API URL
REACT_APP_API_URL=http://localhost:8000

# API timeout in milliseconds
REACT_APP_API_TIMEOUT=30000

# ============================================
# FEATURE FLAGS
# ============================================
# Enable debug mode
REACT_APP_DEBUG=false

# Enable analytics tracking
REACT_APP_ENABLE_ANALYTICS=false

# ============================================
# UI CONFIGURATION
# ============================================
# Items per page for lists
REACT_APP_ITEMS_PER_PAGE=20

# Enable dark mode
REACT_APP_DARK_MODE=false

# ============================================
# EXTERNAL SERVICES
# ============================================
# Google Analytics ID (if using)
REACT_APP_GA_ID=

# Sentry DSN for error tracking (if using)
REACT_APP_SENTRY_DSN=
```

## 5.2 Database Configuration

### 5.2.1 Database Location

By default, the database is created at `./data/books.db`. To change:

```env
# Absolute path
DATABASE_PATH=/var/lib/book-recommender/books.db

# Relative path
DATABASE_PATH=./custom/location/books.db
```

### 5.2.2 Database Backup

**Manual backup:**
```bash
# Simple copy
cp ./data/books.db ./data/books.backup.db

# With timestamp
cp ./data/books.db "./data/books.backup.$(date +%Y%m%d).db"
```

**Automated backup script:**
```bash
#!/bin/bash
# backup-db.sh

BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"

# Create backup with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp ./data/books.db "$BACKUP_DIR/books_$TIMESTAMP.db"

# Keep only last 7 days
find "$BACKUP_DIR" -name "books_*.db" -mtime +7 -delete

echo "Backup created: books_$TIMESTAMP.db"
```

**Set up cron job (Linux/macOS):**
```bash
# Run daily at 2 AM
crontab -e

# Add this line:
0 2 * * * cd /path/to/book-recommender/backend && ./backup-db.sh
```

### 5.2.3 Database Maintenance

**Optimize database (vacuum):**
```bash
sqlite3 ./data/books.db "VACUUM;"
```

**Check database integrity:**
```bash
sqlite3 ./data/books.db "PRAGMA integrity_check;"
```

**View database size:**
```bash
ls -lh ./data/books.db
```

## 5.3 AI Model Configuration

### 5.3.1 Choosing the Right Model

The system uses Claude Sonnet 4.5 by default. You can configure different models:

```env
# Fastest, cheapest (good for development)
ANTHROPIC_MODEL=claude-haiku-3-5-20250929

# Balanced (default, recommended)
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# Most capable (expensive, for complex analysis)
ANTHROPIC_MODEL=claude-opus-4-20250929
```

**Cost Comparison:**
- Haiku: $0.25 per million input tokens / $1.25 per million output
- Sonnet: $3 per million input tokens / $15 per million output
- Opus: $15 per million input tokens / $75 per million output

**Typical token usage per operation:**
- Book recommendation: ~2,000 tokens
- Book analysis: ~1,500 tokens
- Readiness evaluation: ~2,500 tokens
- Preparation plan: ~2,000 tokens

### 5.3.2 Temperature Settings

Temperature controls randomness (0 = deterministic, 1 = very creative):

```env
# Conservative (more consistent)
AI_TEMPERATURE_RECOMMENDATIONS=0.5
AI_TEMPERATURE_ANALYSIS=0.4
AI_TEMPERATURE_EVALUATION=0.5

# Balanced (default)
AI_TEMPERATURE_RECOMMENDATIONS=0.7
AI_TEMPERATURE_ANALYSIS=0.6
AI_TEMPERATURE_EVALUATION=0.7

# Creative (more varied)
AI_TEMPERATURE_RECOMMENDATIONS=0.9
AI_TEMPERATURE_ANALYSIS=0.8
AI_TEMPERATURE_EVALUATION=0.9
```

### 5.3.3 Rate Limiting AI Calls

To control costs and comply with rate limits:

```env
# Max concurrent AI requests (prevents rate limit errors)
MAX_CONCURRENT_AI_REQUESTS=5

# Cooldown between requests (milliseconds)
AI_REQUEST_COOLDOWN=100
```

## 5.4 Library Integration Configuration

### 5.4.1 Sno-Isle Libraries

Enabled by default for Washington State users:

```env
ENABLE_LIBRARY_CHECKING=true
LIBRARY_SYSTEM=snoisle
```

### 5.4.2 Adding Other Library Systems

To add support for your local library:

1. Edit `backend/app/services/library_checker.py`
2. Add your library's catalog URL pattern
3. Update the scraping logic for your library's HTML structure

Example for a custom library:

```python
# In library_checker.py

async def check_custom_library(self, isbn: str) -> Dict[str, Any]:
    """Check availability at Custom Library"""
    url = f"https://catalog.customlibrary.org/search?isbn={isbn}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            # Customize based on your library's HTML
            available = soup.find('span', class_='availability')

            return {
                'available': 'Available' in available.text if available else False,
                'formats': self._extract_formats(soup),
                'url': url
            }
```

## 5.5 External API Configuration

### 5.5.1 Google Books API

While optional, it improves book metadata quality:

1. Go to https://console.cloud.google.com
2. Create a new project
3. Enable "Books API"
4. Create credentials (API key)
5. Add to `.env`:

```env
GOOGLE_BOOKS_API_KEY=AIzaSyYourKeyHere
```

### 5.5.2 API Fallback Behavior

When external APIs fail:
1. Try Google Books API first (if key provided)
2. Fall back to Open Library API
3. If both fail, allow manual entry
4. Log warning but don't crash

## 5.6 Advanced Configuration

### 5.6.1 Performance Tuning

For better performance with large databases:

```env
# Database
DB_TIMEOUT=60
DB_POOL_SIZE=20

# Caching
RECOMMENDATION_CACHE_HOURS=48
ANALYSIS_CACHE_DAYS=60

# Pagination
DEFAULT_PAGE_SIZE=50
MAX_PAGE_SIZE=200
```

### 5.6.2 Development vs Production

**Development settings:**
```env
API_RELOAD=true
LOG_LEVEL=DEBUG
REACT_APP_DEBUG=true
ALLOWED_ORIGINS=*
```

**Production settings:**
```env
API_RELOAD=false
LOG_LEVEL=WARNING
REACT_APP_DEBUG=false
ALLOWED_ORIGINS=https://yourdomain.com
```

---

# 6. Running the Application

## 6.1 Development Mode

### 6.1.1 Start Backend Server

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run with auto-reload
python -m app.main

# Alternative: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**You should see:**
```
Initializing Enhanced Book Recommender API...
✓ Database initialized (with Tier 1 & 2 enhancements)
✓ AI Recommendation Engine initialized
✓ Enhanced Services initialized:
  - AI Reading Coach
  - Reading DNA Profiler
  - Mood-Based Recommendations
  - Completion Predictor
  - Reading Journal with AI Insights
  - Annual Reports Generator
✓ Manual Entry & Evaluation Services initialized:
  - Manual Book Addition with AI Analysis
  - 'Should I Read This?' Evaluation System
  - Future Reads Management
  - Readiness Monitoring
  - Preparation Plan Generator
✓ Vocabulary Builder ready
✓ Series Tracker ready
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Backend is now running at: http://localhost:8000**

### 6.1.2 Start Frontend Development Server

In a **new terminal** (keep backend running):

```bash
# Navigate to frontend directory
cd frontend

# Start React development server
npm start
```

**You should see:**
```
Compiled successfully!

You can now view book-recommender in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.x:3000

Note that the development build is not optimized.
To create a production build, use npm run build.

webpack compiled successfully
```

**Frontend is now running at: http://localhost:3000**

### 6.1.3 Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## 6.2 Production Mode

### 6.2.1 Build Frontend for Production

```bash
cd frontend

# Create optimized production build
npm run build

# This creates ./build directory with optimized files
```

### 6.2.2 Run Backend in Production

**Option 1: Using Uvicorn directly**
```bash
cd backend
source venv/bin/activate

# Run without reload, with workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Option 2: Using Gunicorn (recommended for Linux)**
```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

**Option 3: Using systemd service (Linux)**

Create `/etc/systemd/system/book-recommender.service`:

```ini
[Unit]
Description=Book Recommender API
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/book-recommender/backend
Environment="PATH=/path/to/book-recommender/backend/venv/bin"
ExecStart=/path/to/book-recommender/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable book-recommender
sudo systemctl start book-recommender

# Check status
sudo systemctl status book-recommender

# View logs
sudo journalctl -u book-recommender -f
```

### 6.2.3 Serve Frontend

**Option 1: Using nginx (recommended)**

Install nginx:
```bash
# Ubuntu/Debian
sudo apt install nginx

# macOS
brew install nginx
```

Configure nginx (`/etc/nginx/sites-available/book-recommender`):
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        root /path/to/book-recommender/frontend/build;
        try_files $uri /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and reload:
```bash
sudo ln -s /etc/nginx/sites-available/book-recommender /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**Option 2: Using serve (simple)**
```bash
# Install serve globally
npm install -g serve

# Serve the build directory
serve -s build -l 3000
```

## 6.3 Docker Deployment

### 6.3.1 Create Docker Files

**Backend Dockerfile** (`backend/Dockerfile`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile** (`frontend/Dockerfile`):
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Docker Compose** (`docker-compose.yml`):
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_PATH=/app/data/books.db
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### 6.3.2 Run with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

## 6.4 Running on Different Ports

### 6.4.1 Change Backend Port

```bash
# Option 1: Environment variable
API_PORT=5000 python -m app.main

# Option 2: Direct uvicorn command
uvicorn app.main:app --port 5000

# Option 3: Update .env
echo "API_PORT=5000" >> .env
```

### 6.4.2 Change Frontend Port

```bash
# Set PORT environment variable
PORT=3001 npm start

# Or create .env in frontend/
echo "PORT=3001" > .env
```

**Don't forget to update CORS settings in backend!**

## 6.5 Monitoring and Logs

### 6.5.1 Backend Logs

**View real-time logs:**
```bash
# If running in terminal, logs appear automatically

# If running as service:
sudo journalctl -u book-recommender -f

# Custom log file:
uvicorn app.main:app --log-config logging.yaml
```

**Log configuration** (`logging.yaml`):
```yaml
version: 1
disable_existing_loggers: false

formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    formatter: default
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    formatter: default
    filename: logs/app.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

root:
  level: INFO
  handlers: [console, file]
```

### 6.5.2 Frontend Logs

Frontend logs appear in:
- Browser console (F12 → Console)
- Terminal where `npm start` is running
- Build logs: `npm run build > build.log 2>&1`

### 6.5.3 Database Activity

Monitor database queries:
```bash
# Enable query logging in backend/.env
LOG_SQL_QUERIES=true

# View database locks
sqlite3 ./data/books.db "SELECT * FROM pragma_database_list;"
```

## 6.6 Health Checks

### 6.6.1 Backend Health

```bash
# Simple health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy"}

# Detailed system info
curl http://localhost:8000/

# Returns version, features, etc.
```

### 6.6.2 Automated Health Monitoring

**Create health check script** (`health-check.sh`):
```bash
#!/bin/bash

# Check backend
BACKEND_STATUS=$(curl -s http://localhost:8000/health | jq -r '.status')

if [ "$BACKEND_STATUS" != "healthy" ]; then
    echo "Backend unhealthy!"
    # Send alert, restart service, etc.
    exit 1
fi

# Check frontend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)

if [ "$FRONTEND_STATUS" != "200" ]; then
    echo "Frontend unhealthy!"
    exit 1
fi

echo "All systems healthy"
exit 0
```

**Run periodically:**
```bash
# Add to crontab
*/5 * * * * /path/to/health-check.sh
```

## 6.7 Stopping the Application

### 6.7.1 Stop Development Servers

```bash
# In each terminal where servers are running:
# Press Ctrl+C

# Or kill by port:
# macOS/Linux:
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### 6.7.2 Stop Production Services

```bash
# Systemd service
sudo systemctl stop book-recommender

# Docker
docker-compose down

# Gunicorn (find PID)
ps aux | grep gunicorn
kill <PID>
```

## 6.8 Restart Procedures

### 6.8.1 Graceful Restart

```bash
# Development: Just Ctrl+C and restart

# Production systemd:
sudo systemctl reload book-recommender

# Or full restart:
sudo systemctl restart book-recommender

# Docker:
docker-compose restart
```

### 6.8.2 After Code Changes

```bash
# Backend changes:
# 1. Stop backend
# 2. Pull/apply changes
# 3. Restart backend

# Frontend changes:
# 1. Rebuild: npm run build
# 2. Restart nginx: sudo systemctl reload nginx

# Database schema changes:
# 1. Backup database first!
# 2. Apply migrations
# 3. Restart backend
```

---

*This is Part 1 of the Complete User Guide. Continuing with Part 2...*

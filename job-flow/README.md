# JobFlow - Job Application Automation Tool

**Transform your job search: Apply to 50+ jobs in 2-3 hours instead of 8-12 hours.**

JobFlow is a comprehensive job application automation system that combines automated job discovery with manual review and submission. It handles repetitive form filling while you maintain full control over which jobs to apply to.

## 🎯 Key Features

### ✅ **Phase 1 - MVP (Ready)**
- ✨ LinkedIn Easy Apply automation
- 📝 Smart form filling with fuzzy question matching
- 💾 User profile and question database management
- 📊 Resume management and auto-selection
- 📈 Basic application tracking
- 🔄 Manual trigger workflow (you review before submitting)

### 🚧 **Phase 2-4 (In Development)**
- 🌐 Multi-platform support (Workday, Greenhouse, Lever, Taleo)
- 🤖 Automated job discovery (finds 50+ relevant jobs daily)
- 🧠 AI-powered form analysis using Claude.ai web interface (FREE with Claude Pro)
- 📊 Advanced analytics and insights
- ⏰ Overnight application preparation
- ⌨️ Keyboard-driven rapid review interface

## 🏗️ Architecture

```
job-flow/
├── job-flow-backend/          # FastAPI backend (Python)
│   ├── app/
│   │   ├── database/          # SQLAlchemy models
│   │   ├── api/routes/        # REST API endpoints
│   │   ├── services/          # Business logic
│   │   ├── core/              # Core utilities
│   │   └── schemas/           # Pydantic schemas
│   ├── data/                  # SQLite database & uploads
│   └── requirements.txt
│
└── job-flow-extension/        # Chrome extension (React/TypeScript)
    ├── src/
    │   ├── background/        # Background service worker
    │   ├── content/           # Content scripts & platform handlers
    │   ├── popup/             # Extension popup UI
    │   └── options/           # Settings page
    └── package.json
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Chrome or Edge browser
- (Optional) Claude Pro subscription for AI features

### Backend Setup

```bash
# 1. Navigate to backend directory
cd job-flow-backend

# 2. Create virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers (for job scanning)
playwright install chromium

# 5. Create .env file
cp .env.example .env

# Edit .env and customize settings
# At minimum, generate a new SECRET_KEY:
# python -c "import secrets; print(secrets.token_hex(32))"

# 6. Run database initialization
python -c "from app.database import init_db; init_db()"

# 7. Seed common questions (optional but recommended)
python scripts/seed_data.py

# 8. Start the server
uvicorn app.main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`

### Extension Setup (Coming Soon)

```bash
# 1. Navigate to extension directory
cd job-flow-extension

# 2. Install dependencies
npm install

# 3. Build extension
npm run build

# 4. Load in Chrome
# - Open chrome://extensions
# - Enable "Developer mode"
# - Click "Load unpacked"
# - Select job-flow-extension/dist folder
```

## 📖 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints

#### Profile Management
- `GET /api/profile/` - Get user profile
- `POST /api/profile/` - Create profile
- `PUT /api/profile/` - Update profile
- `POST /api/profile/tech-skills` - Update tech skills

#### Question Database
- `GET /api/questions/` - List all questions
- `POST /api/questions/` - Add new question
- `GET /api/questions/match/search?question_text=...` - Find matching question
- `POST /api/questions/learn` - Learn new question from application

#### Resume Management
- `GET /api/resumes/` - List all resumes
- `POST /api/resumes/upload` - Upload new resume
- `POST /api/resumes/select` - Auto-select best resume for job
- `GET /api/resumes/download/{resume_id}` - Download resume file

#### Applications
- `GET /api/applications/` - List applications (with filtering)
- `POST /api/applications/` - Create application record
- `PUT /api/applications/{id}` - Update application
- `GET /api/applications/stats/summary` - Get summary statistics

#### Job Discovery
- `GET /api/jobs/` - List discovered jobs
- `POST /api/jobs/scan` - Trigger job scan
- `POST /api/jobs/score` - Score job match quality
- `POST /api/jobs/{id}/prepare` - Prepare application

#### Analytics
- `GET /api/analytics/overview` - Comprehensive analytics
- `GET /api/analytics/response-rate` - Response rate breakdown
- `GET /api/analytics/best-performing` - Best strategies
- `GET /api/analytics/recommendations` - Personalized recommendations

## 🎯 Workflow

### Daily Automated Workflow (Phase 3+)

**2:00 AM - Automated Job Discovery**
1. System searches LinkedIn for new jobs matching your criteria
2. Scores each job (0-100) based on match quality
3. Prepares applications for high-match jobs (85%+)
4. Ready for your review when you wake up

**9:00 AM - Morning Application Session**
1. Open dashboard: "62 applications ready for review"
2. Enter rapid review mode:
   - See job details and match score
   - Review pre-filled data
   - Hit Enter to submit, S to skip, E to edit
3. Complete 20-30 applications in 1 hour

### Manual Browsing Workflow (Phase 1 - Available Now)

1. Browse LinkedIn for jobs manually
2. Click "Easy Apply" on interesting job
3. Extension detects form
4. Click "Fill Form" (or use hotkey)
5. Extension fills form in 2-3 seconds
6. Review pre-filled data (30 seconds)
7. Click "Submit Application"
8. System logs application automatically

## 💾 Database Schema

The system uses SQLite with the following main tables:

- **user_profiles** - Your personal and professional information
- **resumes** - Resume templates with metadata for auto-selection
- **questions** - Question-answer database with fuzzy matching
- **applications** - All submitted applications with tracking
- **application_answers** - Answers used for each application
- **job_listings** - Discovered jobs awaiting review
- **platform_patterns** - Learned patterns for unknown platforms
- **sessions** - Application session tracking for analytics

## 📊 Analytics & Insights

JobFlow tracks comprehensive metrics:

- **Response rates** by match score, company type, platform
- **Time savings** vs manual application
- **Best performing** resumes and strategies
- **Timeline analysis** of applications and responses
- **Question database** growth and usage
- **Personalized recommendations** for optimization

## 🔒 Security & Privacy

- **All data stored locally** - SQLite database on your machine
- **No data leaves your computer** except when:
  - Submitting applications (obviously)
  - Using Claude.ai web interface (optional, uses your Pro subscription)
- **No external API calls** for core functionality
- **No tracking or telemetry**

## 💰 Cost

### With Claude Pro (Recommended)
- **$0/month** for JobFlow functionality
- Uses Claude.ai web interface (FREE with your Pro subscription)
- No API costs

### Without Claude Pro
- **$0/month** for core features (fuzzy matching, resume selection)
- ~$45/month if you add Claude API for advanced features
- Optional - core features work great without AI

## 🎓 Learning System

JobFlow learns from your application process:

1. **Question Learning**: Automatically saves new questions and your answers
2. **Resume Feedback**: Tracks which resumes get better responses
3. **Platform Patterns**: Learns form structures for unknown platforms
4. **Match Score Tuning**: Refines job matching based on your responses

## ⚙️ Configuration

Edit `.env` file in the backend directory:

```env
# Application Settings
APP_NAME=JobFlow API
DEBUG=True

# Database
DATABASE_URL=sqlite:///./data/jobflow.db

# Security
SECRET_KEY=your-secret-key-here

# CORS (for extension)
CORS_ORIGINS=http://localhost:3000,chrome-extension://*

# Job Scanning
JOB_SCAN_INTERVAL_MINUTES=30
JOB_SCAN_ENABLED=False  # Enable after profile setup

# Limits
MAX_UPLOAD_SIZE_MB=10
MAX_RESUMES=10
```

## 🧪 Testing

```bash
# Backend tests
cd job-flow-backend
pytest tests/

# With coverage
pytest --cov=app tests/

# Extension tests
cd job-flow-extension
npm test
```

## 📝 Development Roadmap

- [x] Phase 1: MVP - LinkedIn Easy Apply automation
- [ ] Phase 2: Multi-platform support (Workday, Greenhouse, Lever)
- [ ] Phase 3: Automated job discovery and overnight preparation
- [ ] Phase 4: AI-powered enhancements with Claude.ai

## 🤝 Contributing

This is a personal project built for job searching. Feel free to fork and customize for your needs!

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with FastAPI, React, and Playwright
- Uses FuzzyWuzzy for intelligent question matching
- Optional Claude AI integration for advanced features

## 📞 Support

For issues or questions:
- Check the documentation
- Review API docs at http://localhost:8000/docs
- Check logs in `job-flow-backend/logs/jobflow.log`

## 🎉 Success Stories

**Target**: 50 applications in 2-3 hours

**Current manual process**: 10-15 minutes per application = 8-12 hours for 50 applications

**With JobFlow**: 2-3 minutes per application = 2-3 hours for 50 applications

**Time saved**: 83%+ reduction in application time

---

**Happy job hunting! 🚀**

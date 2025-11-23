# JobFlow Setup Guide

Complete step-by-step instructions for setting up JobFlow on your machine.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Extension Setup](#extension-setup)
4. [Initial Configuration](#initial-configuration)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

1. **Python 3.11 or higher**
   ```bash
   python --version  # Should show 3.11+
   ```

   If not installed:
   - **Windows**: Download from [python.org](https://www.python.org/downloads/)
   - **macOS**: `brew install python@3.11`
   - **Linux**: `sudo apt install python3.11` or equivalent

2. **Node.js 18 or higher**
   ```bash
   node --version  # Should show v18+
   ```

   If not installed:
   - Download from [nodejs.org](https://nodejs.org/)
   - Or use nvm: `nvm install 18`

3. **Chrome or Edge Browser**
   - Must support Chrome extensions

### Optional

- **Claude Pro Subscription** - For AI-powered features (costs $0 extra)
- **Git** - For version control

---

## Backend Setup

### Step 1: Clone or Navigate to Project

```bash
cd /path/to/job-flow
cd job-flow-backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- SQLAlchemy (database ORM)
- Playwright (browser automation)
- FuzzyWuzzy (fuzzy matching)
- And other dependencies

### Step 4: Install Playwright Browsers

```bash
playwright install chromium
```

This downloads the Chromium browser needed for job scanning.

### Step 5: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
# On Windows: notepad .env
# On macOS/Linux: nano .env
```

**Generate a secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it in the `.env` file:
```env
SECRET_KEY=paste-the-generated-key-here
```

### Step 6: Initialize Database

```bash
python -c "from app.database import init_db; init_db()"
```

This creates the SQLite database file at `data/jobflow.db`.

### Step 7: Seed Common Questions

```bash
python scripts/seed_data.py
```

Expected output:
```
============================================================
JobFlow Data Seeding Script
============================================================

1. Initializing database...
✓ Database initialized

2. Seeding common questions...
Seeding common questions...
✓ Added 50 questions

============================================================
✓ Seeding completed successfully!
============================================================

Database Statistics:
  - User Profiles: 1
  - Questions: 50
```

### Step 8: Start the Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 9: Verify Backend is Running

Open your browser and visit:
- http://localhost:8000 - Should show: `{"name": "JobFlow API", "version": "1.0.0", "status": "running"}`
- http://localhost:8000/docs - Interactive API documentation (Swagger UI)
- http://localhost:8000/redoc - Alternative API documentation

✅ **Backend setup complete!**

---

## Extension Setup (Coming in Future Update)

The Chrome extension is currently in development. For now, you can:

1. Use the API directly via http://localhost:8000/docs
2. Build custom scripts that interact with the API
3. Wait for the extension release

**Extension Features (Coming Soon):**
- Automatic form detection
- One-click form filling
- Resume auto-upload
- Review interface
- Platform-specific handlers

---

## Initial Configuration

### Step 1: Create Your Profile

Visit http://localhost:8000/docs and use the interactive API:

1. Expand `POST /api/profile/`
2. Click "Try it out"
3. Fill in your information:

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "555-0100",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "github_url": "https://github.com/johndoe",
  "city": "Seattle",
  "state": "WA",
  "zip_code": "98101",
  "work_authorized": true,
  "requires_sponsorship": false,
  "preferred_roles": ["Senior Software Engineer", "Backend Engineer"],
  "preferred_locations": ["Seattle", "Remote", "Bellevue"],
  "remote_preference": "remote",
  "min_salary": 150000,
  "max_salary": 200000,
  "total_years_experience": 10,
  "current_title": "Senior Software Engineer",
  "tech_skills": {
    "Java": 6,
    "Python": 10,
    "AWS": 4,
    "Distributed Systems": 6,
    "Kubernetes": 3
  },
  "notice_period_weeks": 2
}
```

4. Click "Execute"
5. Verify response shows your profile with ID

### Step 2: Upload Resumes

1. Prepare 1-3 resume versions:
   - **Master Resume** - General purpose
   - **Backend-Focused Resume** - For backend/infrastructure roles
   - **ML-Focused Resume** - For ML/data roles (if applicable)

2. Use `POST /api/resumes/upload`:
   - Select your resume file (.pdf or .docx)
   - Give it a name: e.g., "Backend-Focus"
   - Add focus areas: e.g., "backend,distributed systems,java"
   - Add technologies: e.g., "Java,Python,AWS,Kubernetes"
   - Mark master resume: `true` for your main resume

### Step 3: Review Seeded Questions

Visit `GET /api/questions/` to see the 50 pre-loaded questions.

These include:
- Contact information
- Work authorization
- Experience years
- Skills
- Salary expectations
- And more

### Step 4: Customize Questions

Add company-specific or role-specific questions:

```json
{
  "question_text": "Why do you want to work at Microsoft?",
  "answer": "I'm excited about Microsoft's cloud infrastructure and the opportunity to work on Azure services at scale.",
  "category": "motivation",
  "field_type": "textarea"
}
```

---

## Verification

### Test API Endpoints

1. **Profile**: `GET /api/profile/`
   - Should return your profile

2. **Questions**: `GET /api/questions/`
   - Should return ~50 questions

3. **Question Matching**: `GET /api/questions/match/search?question_text=phone`
   - Should match "Phone number"

4. **Resumes**: `GET /api/resumes/`
   - Should show your uploaded resumes

5. **Resume Selection**: `POST /api/resumes/select`
   ```json
   {
     "job_description": "Looking for a Senior Backend Engineer with Java and distributed systems experience"
   }
   ```
   - Should select your best-matching resume

### Test Question Fuzzy Matching

Try these test queries at `GET /api/questions/match/search`:

1. `question_text=phone` → Should match "Phone number"
2. `question_text=email address` → Should match "Email address"
3. `question_text=years of python` → Should match "Years of experience in Python"
4. `question_text=can you work in US` → Should match "Are you authorized to work..."

---

## Troubleshooting

### Backend Issues

#### "Module not found" error
```bash
# Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### "Database locked" error
```bash
# Stop the server (Ctrl+C)
# Delete the database
rm data/jobflow.db

# Reinitialize
python -c "from app.database import init_db; init_db()"
python scripts/seed_data.py
```

#### Port 8000 already in use
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001

# Or find and kill the process
# Windows: netstat -ano | findstr :8000
# macOS/Linux: lsof -ti:8000 | xargs kill
```

#### CORS errors from extension
Ensure `.env` has:
```env
CORS_ORIGINS=http://localhost:3000,chrome-extension://*
```

### Database Issues

#### Reset database completely
```bash
# Stop server
# Delete database
rm -rf data/

# Recreate
python -c "from app.database import init_db; init_db()"
python scripts/seed_data.py
```

#### View database contents
```bash
# Install sqlite3 (usually pre-installed)
sqlite3 data/jobflow.db

# List tables
.tables

# View questions
SELECT question_text, answer FROM questions LIMIT 10;

# Exit
.exit
```

### Performance Issues

#### Fuzzy matching is slow
- Normal for large question databases (>1000 questions)
- Consider adding database indexes
- Results are cached during single request

#### Backend startup is slow
- Playwright browser download on first run
- Subsequent starts are fast

---

## Next Steps

✅ **Backend is ready!**

Now you can:

1. **Manually use the API** - Test endpoints via Swagger UI
2. **Create applications** - Track your job applications
3. **Build custom scripts** - Automate with Python requests
4. **Wait for extension** - Chrome extension coming soon

### Example: Tracking an Application

```python
import requests

# Create application record
response = requests.post("http://localhost:8000/api/applications/", json={
    "company": "Microsoft",
    "job_title": "Senior Software Engineer",
    "job_url": "https://careers.microsoft.com/job/12345",
    "job_description": "Looking for backend engineer...",
    "platform": "workday",
    "match_score": 85,
    "resume_id": 1,
    "user_id": 1
})

print(response.json())
```

---

## Getting Help

### Logs

Check logs for errors:
```bash
tail -f logs/jobflow.log
```

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Database

Inspect database directly:
```bash
sqlite3 data/jobflow.db
.schema  # Show table structures
```

---

**Setup complete! Happy job hunting! 🚀**

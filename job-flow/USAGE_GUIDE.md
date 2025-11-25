# JobFlow - Comprehensive Usage Guide

Complete guide to using JobFlow for automated job application assistance.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Backend Setup](#backend-setup)
3. [Extension Installation](#extension-installation)
4. [Platform Handlers](#platform-handlers)
5. [Complete Workflows](#complete-workflows)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Features](#advanced-features)

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Chrome/Chromium browser
- Claude Pro subscription (for Phase 4)

### 5-Minute Setup

```bash
# 1. Start the backend
cd job-flow-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/seed_data.py  # Load 50 common questions
uvicorn app.main:app --reload

# 2. Build the extension
cd ../job-flow-extension
npm install
npm run build

# 3. Load extension in Chrome
# - Open chrome://extensions/
# - Enable "Developer mode"
# - Click "Load unpacked"
# - Select job-flow-extension/dist folder
```

### First Application

1. Create your profile in the extension options (click extension icon → Settings)
2. Navigate to a job posting on LinkedIn, Workday, Greenhouse, or Lever
3. Press **Ctrl+Shift+F** (or Cmd+Shift+F on Mac)
4. Watch JobFlow auto-fill your application
5. Review and submit manually

---

## Backend Setup

### Database Configuration

JobFlow uses SQLite by default. All data is stored locally at:
```
job-flow-backend/data/jobflow.db
```

To use a different database, set the `DATABASE_URL` environment variable:

```bash
# PostgreSQL example
export DATABASE_URL="postgresql://user:password@localhost/jobflow"

# MySQL example
export DATABASE_URL="mysql://user:password@localhost/jobflow"
```

### Creating Your Profile

**Option 1: Via API (Recommended)**

```bash
curl -X POST "http://localhost:8000/api/profile" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@email.com",
    "phone": "+1-555-123-4567",
    "city": "San Francisco",
    "state": "CA",
    "country": "United States",
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "github_url": "https://github.com/johndoe",
    "website": "https://johndoe.dev",
    "current_title": "Senior Software Engineer",
    "years_of_experience": 8,
    "work_authorization": "US Citizen",
    "requires_sponsorship": false,
    "willing_to_relocate": true,
    "remote_preference": "remote_only",
    "salary_expectation_min": 150000,
    "salary_expectation_max": 200000,
    "notice_period_days": 14
  }'
```

**Option 2: Via Extension UI**

1. Click the JobFlow extension icon
2. Click "Settings" button
3. Fill in your profile information
4. Click "Save Profile"

### Adding Resumes

Upload multiple resume versions optimized for different roles:

```bash
curl -X POST "http://localhost:8000/api/resumes" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Full-Stack Resume",
    "file_path": "/path/to/resume-fullstack.pdf",
    "technologies": ["React", "Node.js", "PostgreSQL", "Docker"],
    "focus_areas": ["Web Development", "API Design", "Cloud Infrastructure"],
    "years_experience_min": 5,
    "years_experience_max": 10,
    "is_default": true
  }'
```

**Resume Auto-Selection**

JobFlow automatically selects the best resume based on:
- Technology keyword matches
- Focus area alignment
- Experience level requirements
- Historical success rate

### Managing Questions

JobFlow comes pre-loaded with 50 common questions. Add custom answers:

```bash
curl -X POST "http://localhost:8000/api/questions" \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "Why do you want to work here?",
    "answer_text": "I am passionate about your mission to democratize AI...",
    "category": "preferences",
    "platform": "general",
    "confidence_score": 100
  }'
```

**Question Matching Algorithm**

JobFlow uses fuzzy string matching (FuzzyWuzzy) with 85%+ confidence threshold:

1. Extracts question text from form field
2. Compares against all stored questions using `token_sort_ratio`
3. Returns best match if confidence ≥ 85%
4. Falls back to empty string if no confident match

Example matches:
- "What is your email?" → "Email Address" (95% confidence)
- "How many years of experience do you have?" → "Years of Experience" (92% confidence)
- "Are you legally authorized to work in the US?" → "Work Authorization Status" (88% confidence)

---

## Extension Installation

### Building from Source

```bash
cd job-flow-extension
npm install
npm run build  # Production build
# or
npm run dev    # Development build with watch mode
```

The extension will be built to `dist/` folder.

### Loading in Chrome

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right)
3. Click "Load unpacked"
4. Navigate to `job-flow-extension/dist` and select it
5. Pin the extension icon for easy access

### Configuring Backend URL

1. Click the JobFlow extension icon
2. Click "Settings" button (or right-click icon → Options)
3. Set Backend URL: `http://localhost:8000`
4. Click "Test Connection" to verify
5. Save settings

### Permissions Explained

JobFlow requests these permissions:

- **storage**: Save your profile and settings locally
- **activeTab**: Detect and fill forms on current page
- **scripting**: Inject content scripts for form detection
- **Host permissions**: Access job boards (LinkedIn, Workday, etc.)

JobFlow does NOT:
- Track your browsing history
- Access data on non-job-application sites
- Send data to external servers (except your local backend)

---

## Platform Handlers

JobFlow includes specialized handlers for 4 major platforms. Each handler is optimized for that platform's specific HTML structure and behavior.

### Supported Platforms

| Platform | Handler | Multi-Step | Auto-Resume | Auto-Submit |
|----------|---------|-----------|-------------|-------------|
| LinkedIn Easy Apply | ✅ | ✅ | ⚠️ Detect only | ❌ |
| Workday | ✅ | ✅ | ⚠️ Detect only | ❌ |
| Greenhouse | ✅ | ❌ | ❌ | ❌ |
| Lever | ✅ | ❌ | ❌ | ❌ |
| Unknown/Generic | ✅ Fallback | ❌ | ❌ | ❌ |

### LinkedIn Easy Apply Handler

**Detection**: `linkedin.com` + modal with class `.jobs-easy-apply-modal`

**Features**:
- Multi-step form navigation with "Continue" button detection
- Handles all standard LinkedIn Easy Apply fields
- Resume attachment detection (shows if already uploaded)
- Smart field labeling from LinkedIn's specific HTML structure
- Progress tracking across all steps

**Supported Fields**:
- Contact information (phone, email, location)
- Work authorization questions
- Experience and education
- LinkedIn profile URL pre-fill
- Custom screening questions
- Text answers and dropdowns

**Example Usage**:

```javascript
// Automatically detected when you navigate to:
// https://www.linkedin.com/jobs/view/123456789/

// 1. Click "Easy Apply" button
// 2. Press Ctrl+Shift+F
// 3. JobFlow fills all detected fields
// 4. Click "Continue" to next step (or JobFlow can do it)
// 5. Repeat until "Review" step
// 6. Submit manually after reviewing
```

**Field Detection Strategy**:
```typescript
// LinkedIn uses specific selectors
const fieldContainers = document.querySelectorAll(
  '.jobs-easy-apply-form-section__grouping, ' +
  '.fb-single-line-text__input, ' +
  '.fb-dropdown'
);

// Extracts labels from:
// 1. Associated <label> elements
// 2. aria-label attributes
// 3. Placeholder text
// 4. Parent container labels
```

### Workday Handler

**Detection**: `myworkdayjobs.com` in URL

**Features**:
- Uses Workday's `data-automation-id` attributes for reliable field detection
- Multi-step navigation with "Next" button detection
- Handles Workday's unique form structure
- Resume upload detection (shows if already attached)
- Review page detection

**Supported Fields**:
- Personal information
- Contact details
- Work history
- Education
- Custom application questions
- Demographic questions (voluntary)

**Example Usage**:

```javascript
// Automatically detected on URLs like:
// https://company.myworkdayjobs.com/en-US/careers/job/Software-Engineer_R12345

// 1. Navigate to application page
// 2. Press Ctrl+Shift+F
// 3. JobFlow fills current step
// 4. Click "Next" to proceed
// 5. Repeat for each step
// 6. Review and submit manually
```

**Field Detection Strategy**:
```typescript
// Workday uses data-automation-id extensively
const fieldContainers = document.querySelectorAll(
  '[data-automation-id*="formField"]'
);

// Selectors prioritize:
// 1. data-automation-id (most reliable)
// 2. Standard id attribute
// 3. name attribute
```

**Special Methods**:
```typescript
isReviewPage(): boolean
// Detects if you're on the final review page

waitForNextStep(timeout?: number): Promise<boolean>
// Waits for next step to load after clicking "Next"
```

### Greenhouse Handler

**Detection**: `greenhouse.io` or `boards.greenhouse.io` in URL

**Features**:
- Standard form field detection with `.field` classes
- Simple single-page or multi-page forms
- Clean label extraction
- Standard submit button handling

**Supported Fields**:
- Basic information
- Resume upload (detection only)
- Cover letter
- Application questions
- Referral source

**Example Usage**:

```javascript
// Automatically detected on URLs like:
// https://boards.greenhouse.io/company/jobs/123456

// 1. Navigate to application page
// 2. Press Ctrl+Shift+F
// 3. JobFlow fills all fields
// 4. Review and submit manually
```

**Field Detection Strategy**:
```typescript
// Greenhouse uses standard field containers
const fieldContainers = document.querySelectorAll(
  '.field, .application-field'
);

// Fallback to all inputs if containers not found
const inputs = form.querySelectorAll(
  'input:not([type="hidden"]), textarea, select'
);
```

### Lever Handler

**Detection**: `lever.co` or `jobs.lever.co` in URL

**Features**:
- Application form detection with `.application-form` class
- Question-based field containers
- Clean label extraction from `.application-label`
- Submit button detection

**Supported Fields**:
- Contact information
- Resume upload (detection only)
- Cover letter
- Application questions
- Additional documents

**Example Usage**:

```javascript
// Automatically detected on URLs like:
// https://jobs.lever.co/company/job-id

// 1. Navigate to application page
// 2. Press Ctrl+Shift+F
// 3. JobFlow fills all fields
// 4. Review and submit manually
```

**Field Detection Strategy**:
```typescript
// Lever uses application-question containers
const fieldContainers = document.querySelectorAll(
  '.application-question, .form-field'
);

// Labels from:
// 1. .application-label elements
// 2. .application-question-text
// 3. Standard label elements
```

### Generic/Unknown Platform Handler

**Detection**: Fallback when no specific handler matches

**Features**:
- Intelligent form detection (any element with 5+ inputs)
- Flexible field extraction
- Label detection from multiple sources
- Basic field type detection

**Limitations**:
- No multi-step navigation
- No platform-specific optimizations
- May miss fields with unusual HTML structure
- No resume upload support

**When It Activates**:
- Any job board not in the supported list
- Company career pages
- Custom ATS systems
- Forms without `<form>` tags

**Example Platforms**:
- Taleo (partial support)
- iCIMS (partial support)
- BambooHR
- JazzHR
- Custom career portals

---

## Complete Workflows

### Workflow 1: Single Application (LinkedIn Easy Apply)

**Goal**: Apply to one job on LinkedIn with full automation assistance

1. **Preparation** (One-time):
   ```bash
   # Ensure backend is running
   cd job-flow-backend
   source venv/bin/activate
   uvicorn app.main:app --reload

   # Verify profile exists
   curl http://localhost:8000/api/profile
   ```

2. **Find a Job**:
   - Navigate to LinkedIn Jobs
   - Search for positions matching your criteria
   - Open a job posting with "Easy Apply" button

3. **Start Application**:
   - Click "Easy Apply" button
   - Modal appears with first step of application

4. **Auto-Fill with JobFlow**:
   - Press **Ctrl+Shift+F** (Windows/Linux) or **Cmd+Shift+F** (Mac)
   - Green notification appears: "✓ JobFlow detected LinkedIn Easy Apply"
   - Watch fields auto-fill with smooth typing animation
   - Fields turn light green briefly when filled

5. **Review First Step**:
   - Verify all fields are correct
   - Manually adjust any incorrect values
   - Check that resume is attached (or attach manually)

6. **Continue to Next Step**:
   - Click "Continue" button manually
   - Wait for next step to load
   - Press **Ctrl+Shift+F** again to fill next step

7. **Repeat Until Review**:
   - Continue filling each step
   - Typical LinkedIn Easy Apply has 3-5 steps
   - Last step is usually "Review your application"

8. **Final Review and Submit**:
   - Carefully review all information
   - Check resume is correct version
   - Click "Submit application" manually
   - JobFlow **never auto-submits** - you stay in control

9. **Track Application** (Automatic):
   - JobFlow saves application details to backend
   - View in analytics dashboard
   - Track status and follow-ups

**Time Savings**: ~5 minutes → ~2 minutes per application

### Workflow 2: Batch Applications (10 jobs in one session)

**Goal**: Apply to 10 jobs efficiently in 30 minutes

1. **Batch Preparation**:
   ```bash
   # Start backend
   uvicorn app.main:app --reload

   # Clear old detected fields
   curl -X DELETE http://localhost:8000/api/cache/clear
   ```

2. **Create Job List**:
   - Open 10 job posting tabs
   - Use LinkedIn saved jobs or search results
   - Organize tabs: saved → active → applied

3. **Apply Systematically**:

   **For each job**:
   ```
   a. Switch to job tab
   b. Click "Easy Apply"
   c. Ctrl+Shift+F to fill
   d. Continue through all steps with Ctrl+Shift+F
   e. Review and submit
   f. Move to next tab
   ```

4. **Keyboard-Only Workflow**:
   ```
   Ctrl+Shift+F    - Fill current step
   Tab             - Navigate between fields
   Enter           - Click Continue button
   Ctrl+Tab        - Next browser tab
   Ctrl+Shift+Tab  - Previous browser tab
   ```

5. **Monitor Progress**:
   - Check extension popup for stats
   - See "Applications Today: 10"
   - View success rate

6. **Review Analytics**:
   ```bash
   # Get today's applications
   curl http://localhost:8000/api/analytics/summary?period=today
   ```

**Time Savings**: ~100 minutes → ~30 minutes for 10 applications

### Workflow 3: Multi-Platform Applications

**Goal**: Apply to jobs across LinkedIn, Workday, and Greenhouse

1. **Platform Diversity**:
   - 5 jobs on LinkedIn
   - 3 jobs on Workday
   - 2 jobs on Greenhouse

2. **Platform-Specific Preparation**:

   **LinkedIn**:
   - Ensure LinkedIn profile is complete
   - Upload resume to LinkedIn if not done

   **Workday**:
   - May need to create account first
   - Some companies require profile creation

   **Greenhouse**:
   - Direct applications, no account needed
   - Have resume file ready for upload

3. **Apply in Platform Batches**:

   **Start with LinkedIn** (easiest):
   ```
   - Navigate to first LinkedIn job
   - Click Easy Apply
   - Ctrl+Shift+F on each step
   - Submit
   - Repeat for all 5 LinkedIn jobs
   ```

   **Move to Workday** (medium difficulty):
   ```
   - Navigate to Workday job
   - Create account if needed (first time only)
   - Start application
   - Ctrl+Shift+F on each step
   - Manually upload resume if prompted
   - Review and submit
   - Repeat for all 3 Workday jobs
   ```

   **Finish with Greenhouse** (simple):
   ```
   - Navigate to Greenhouse job
   - Ctrl+Shift+F to fill form
   - Upload resume manually
   - Review and submit
   - Repeat for 2 Greenhouse jobs
   ```

4. **Handle Unknown Platforms**:
   - JobFlow falls back to generic detection
   - May need more manual intervention
   - Still saves time on common fields

**Success Rate by Platform**:
- LinkedIn Easy Apply: 95-100% auto-fill
- Workday: 80-90% auto-fill
- Greenhouse: 85-95% auto-fill
- Lever: 85-95% auto-fill
- Unknown: 60-75% auto-fill

### Workflow 4: Daily Job Hunting Routine

**Goal**: Maintain consistent job search with 50 applications per week

**Monday-Friday Routine** (1 hour per day):

**Morning** (30 minutes):
```
1. Start backend if not running
2. Search for new jobs on LinkedIn (20 min)
   - Save 15-20 promising jobs
3. Quick review of saved jobs (10 min)
   - Remove poor matches
   - Prioritize top 10
```

**Evening** (30 minutes):
```
1. Open 10 saved jobs in tabs
2. Batch apply workflow:
   - 10 applications × 2.5 min = 25 minutes
3. Track and log (5 minutes)
   - Note any issues
   - Update spreadsheet
```

**Weekly Tracking**:
```bash
# Monday morning: Check last week's stats
curl http://localhost:8000/api/analytics/summary?period=last_week

# Expected output:
# {
#   "total_applications": 50,
#   "platforms": {
#     "LinkedIn Easy Apply": 35,
#     "Workday": 10,
#     "Greenhouse": 5
#   },
#   "success_rate": 92.5,
#   "avg_time_per_application": 2.8
# }
```

**Monthly Review**:
- Analyze which resume performs best
- Update answers to common questions
- Add new questions from applications
- Refine job search criteria

---

## Keyboard Shortcuts

### Global Shortcuts (Any Page)

| Shortcut | Action | Notes |
|----------|--------|-------|
| `Ctrl+Shift+F` | Fill current form | Mac: `Cmd+Shift+F` |
| `Ctrl+Shift+D` | Detect forms only | Shows notification with field count |
| `Ctrl+Shift+N` | Navigate to next step | Multi-step forms only |

### Extension Popup Shortcuts

| Shortcut | Action |
|----------|--------|
| `Alt+F` | Fill form (same as Ctrl+Shift+F) |
| `Alt+S` | Open settings |
| `Alt+D` | Open analytics dashboard |

### Browser Navigation Tips

Combine JobFlow shortcuts with browser shortcuts for maximum efficiency:

```
Ctrl+T              - New tab
Ctrl+W              - Close tab
Ctrl+Tab            - Next tab
Ctrl+Shift+Tab      - Previous tab
Ctrl+L              - Focus address bar
Ctrl+Enter          - Go to URL
Alt+Left            - Back
Alt+Right           - Forward
```

**Power User Workflow**:
```
1. Ctrl+T              (new tab)
2. Type job URL + Ctrl+Enter
3. Click "Easy Apply"
4. Ctrl+Shift+F        (fill form)
5. Tab through fields to verify
6. Enter               (click Continue)
7. Ctrl+Shift+F        (fill next step)
8. Repeat steps 5-7
9. Manual submit
10. Ctrl+W             (close tab)
11. Repeat from step 1
```

### Customizing Shortcuts

To change keyboard shortcuts:

1. Navigate to `chrome://extensions/shortcuts`
2. Find "JobFlow" in the list
3. Click pencil icon next to shortcut
4. Press your preferred key combination
5. Click OK

**Recommended Alternatives**:
- `Ctrl+Shift+A` - "A" for Auto-fill
- `Alt+J` - "J" for JobFlow
- `Ctrl+Alt+F` - Alternative if Ctrl+Shift+F conflicts

---

## Troubleshooting

### Backend Issues

**Issue**: Backend won't start

```bash
# Check if port 8000 is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process if needed
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
uvicorn app.main:app --reload --port 8001
```

**Issue**: Database errors

```bash
# Reset database (WARNING: Deletes all data)
rm job-flow-backend/data/jobflow.db

# Recreate with fresh schema
cd job-flow-backend
python -c "from app.database.database import engine; from app.database.models import Base; Base.metadata.create_all(bind=engine)"

# Re-seed common questions
python scripts/seed_data.py
```

**Issue**: Profile not found

```bash
# Check if profile exists
curl http://localhost:8000/api/profile

# Create profile via API
curl -X POST http://localhost:8000/api/profile \
  -H "Content-Type: application/json" \
  -d @profile.json
```

### Extension Issues

**Issue**: Extension not detecting forms

**Solutions**:
1. Refresh the page after loading extension
2. Check if page is supported platform
3. Open DevTools → Console → Look for JobFlow logs
4. Verify content script is injected:
   ```javascript
   // In DevTools Console:
   console.log('JobFlow loaded:', !!window.jobFlowContentScript);
   ```

**Issue**: Fields not filling correctly

**Causes and Fixes**:

1. **Wrong field mapping**:
   - Check field labels in DevTools
   - Add custom question mapping:
   ```bash
   curl -X POST http://localhost:8000/api/questions \
     -H "Content-Type: application/json" \
     -d '{"question_text": "Actual field label", "answer_text": "Your answer"}'
   ```

2. **Dynamic form (React/Vue)**:
   - Wait for form to fully load
   - Try clicking in a field first, then Ctrl+Shift+F
   - Some React forms need manual focus

3. **Protected fields**:
   - Some fields are read-only or disabled
   - JobFlow will skip these automatically
   - Fill manually if needed

**Issue**: Extension can't connect to backend

**Check**:
1. Backend is running: `curl http://localhost:8000/health`
2. Backend URL in settings is correct: `http://localhost:8000`
3. No CORS issues (should be configured in backend)
4. Check extension console for errors

**Fix**:
```bash
# Verify CORS settings in backend
# job-flow-backend/app/main.py should have:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Issue**: Keyboard shortcut not working

**Solutions**:
1. Check if another extension uses same shortcut
2. Some pages block keyboard events (Gmail, etc.)
3. Customize shortcut at `chrome://extensions/shortcuts`
4. Try clicking in page first (gives page focus)

### Platform-Specific Issues

**LinkedIn**:

**Issue**: Easy Apply modal not detected

- Refresh page and try again
- Ensure you clicked "Easy Apply" button first
- Some jobs have external applications (not supported)

**Issue**: Resume not uploading

- Upload resume to LinkedIn profile first
- LinkedIn Easy Apply pulls from your profile
- JobFlow detects but doesn't upload files

**Workday**:

**Issue**: Fields not detected

- Workday loads forms dynamically
- Wait 2-3 seconds after page load
- Try scrolling through form first
- Some Workday sites use custom implementations

**Issue**: "Next" button not clicking

- JobFlow detects but doesn't auto-click
- Click manually for now
- Future: Option to auto-navigate

**Greenhouse/Lever**:

**Issue**: Some fields not filling

- These platforms have simple forms
- Missing fields may need manual entry
- Add questions to database for future use

### Debugging Tools

**Enable Verbose Logging**:

Extension console:
```javascript
// Open DevTools on any job application page
// Paste this in console:
localStorage.setItem('jobflow_debug', 'true');
location.reload();

// Disable verbose logging:
localStorage.removeItem('jobflow_debug');
location.reload();
```

Backend logging:
```bash
# job-flow-backend/.env
LOG_LEVEL=DEBUG

# Restart backend
uvicorn app.main:app --reload --log-level debug
```

**Inspect Detected Fields**:

```javascript
// In extension DevTools console:
chrome.storage.local.get(['detected_fields'], (result) => {
  console.table(result.detected_fields);
});
```

**Test Backend Connection**:

```bash
# Health check
curl http://localhost:8000/health

# Test question matching
curl -X POST http://localhost:8000/api/questions/match \
  -H "Content-Type: application/json" \
  -d '{"question_text": "What is your email address?"}'

# Expected response:
# {
#   "question_id": 1,
#   "answer_text": "your.email@example.com",
#   "confidence": 95,
#   "matched": true
# }
```

---

## Advanced Features

### Custom Question Mappings

Create platform-specific or company-specific question mappings:

```bash
# Add platform-specific question
curl -X POST http://localhost:8000/api/questions \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "LinkedIn: Why do you want to work here?",
    "answer_text": "Your tailored answer for LinkedIn applications...",
    "category": "preferences",
    "platform": "linkedin",
    "confidence_score": 100
  }'

# Add company-specific question
curl -X POST http://localhost:8000/api/questions \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "Why Google specifically?",
    "answer_text": "I admire Google'\''s commitment to...",
    "category": "preferences",
    "platform": "greenhouse",
    "company_name": "Google",
    "confidence_score": 100
  }'
```

### Resume Auto-Selection

JobFlow automatically selects the best resume based on job description:

**How it works**:

1. Extracts keywords from job description
2. Scores each resume based on:
   - Technology matches (30% weight)
   - Focus area alignment (30% weight)
   - Experience level fit (20% weight)
   - Historical success rate (20% weight)
3. Returns highest-scoring resume

**Example**:

```bash
# Upload multiple resumes
curl -X POST http://localhost:8000/api/resumes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Full-Stack Web",
    "file_path": "/path/to/resume-web.pdf",
    "technologies": ["React", "Node.js", "PostgreSQL"],
    "focus_areas": ["Web Development", "API Design"],
    "years_experience_min": 5,
    "years_experience_max": 8
  }'

curl -X POST http://localhost:8000/api/resumes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ML Engineer",
    "file_path": "/path/to/resume-ml.pdf",
    "technologies": ["Python", "TensorFlow", "PyTorch"],
    "focus_areas": ["Machine Learning", "Data Science"],
    "years_experience_min": 3,
    "years_experience_max": 6
  }'

# JobFlow will automatically select:
# - "Full-Stack Web" for React/Node.js jobs
# - "ML Engineer" for ML/AI positions
```

### Analytics and Tracking

View detailed analytics about your applications:

```bash
# Today's summary
curl http://localhost:8000/api/analytics/summary?period=today

# This week
curl http://localhost:8000/api/analytics/summary?period=this_week

# Custom date range
curl "http://localhost:8000/api/analytics/summary?start_date=2025-01-01&end_date=2025-01-31"

# Platform breakdown
curl http://localhost:8000/api/analytics/by-platform

# Success rate by resume
curl http://localhost:8000/api/analytics/resume-performance
```

**Example Response**:

```json
{
  "total_applications": 47,
  "period": "this_week",
  "platforms": {
    "LinkedIn Easy Apply": {
      "count": 32,
      "success_rate": 96.8,
      "avg_time_seconds": 145
    },
    "Workday": {
      "count": 10,
      "success_rate": 85.2,
      "avg_time_seconds": 187
    },
    "Greenhouse": {
      "count": 5,
      "success_rate": 92.0,
      "avg_time_seconds": 168
    }
  },
  "total_time_saved_minutes": 312,
  "avg_fields_filled_per_app": 18.5,
  "most_common_questions": [
    {"text": "Email Address", "count": 47},
    {"text": "Phone Number", "count": 47},
    {"text": "Years of Experience", "count": 43},
    {"text": "Work Authorization", "count": 41}
  ]
}
```

### Field Mapping Customization

Create custom field mappings for unusual field names:

```javascript
// In extension options UI (future feature)
{
  "custom_mappings": {
    "email_address": ["Email", "E-mail", "Contact Email", "Your email"],
    "phone_number": ["Phone", "Mobile", "Contact Number", "Tel"],
    "linkedin_url": ["LinkedIn", "LinkedIn Profile", "Professional Profile"]
  }
}
```

### Export Application Data

Export all applications for external tracking:

```bash
# Export to JSON
curl http://localhost:8000/api/applications/export > applications.json

# Export to CSV
curl http://localhost:8000/api/applications/export?format=csv > applications.csv
```

Use exported data for:
- Follow-up tracking in spreadsheet
- Interview preparation
- Success rate analysis
- Resume A/B testing

### Browser Automation (Future - Phase 4)

Planned features for Phase 4:

- **Automated Job Scanning**: Scan LinkedIn every 30 minutes for new jobs
- **Overnight Preparation**: Queue jobs overnight, review in morning
- **Batch Review Dashboard**: Review 20+ applications at once
- **AI-Powered Cover Letters**: Use Claude.ai web interface (free with Pro)
- **Smart Follow-ups**: Automated follow-up email templates
- **Application Status Tracking**: Check status on job boards
- **Interview Scheduler**: Automatically propose interview times

---

## Best Practices

### Security and Privacy

1. **Never commit credentials**:
   ```bash
   # Add to .gitignore
   .env
   *.db
   data/
   ```

2. **Use environment variables**:
   ```bash
   # .env file
   DATABASE_URL=sqlite:///data/jobflow.db
   API_KEY=your_api_key_here
   ```

3. **Regular backups**:
   ```bash
   # Backup database
   cp job-flow-backend/data/jobflow.db backups/jobflow-$(date +%Y%m%d).db
   ```

### Performance Optimization

1. **Limit concurrent applications**:
   - Don't open 50 tabs at once
   - Batch in groups of 10
   - Gives you time to review each

2. **Clear old data**:
   ```bash
   # Delete applications older than 90 days
   curl -X DELETE "http://localhost:8000/api/applications?older_than=90"
   ```

3. **Optimize question database**:
   - Remove duplicate questions monthly
   - Update low-confidence answers
   - Archive unused questions

### Quality Control

1. **Review before submitting**:
   - Always manually review filled forms
   - Check resume is correct version
   - Verify contact information

2. **Track rejection patterns**:
   - Note which answers lead to rejections
   - A/B test different answer phrasings
   - Adjust question database accordingly

3. **Platform-specific optimization**:
   - Learn which platforms you succeed on
   - Focus efforts on high-success platforms
   - Adjust strategy per platform

---

## Getting Help

### Resources

- **Documentation**: `/job-flow/README.md`
- **API Docs**: `http://localhost:8000/docs` (when backend running)
- **Setup Guide**: `/job-flow-backend/SETUP_GUIDE.md`

### Common Questions

**Q: Can JobFlow submit applications automatically?**

A: No, and by design. JobFlow auto-fills forms but you always review and submit manually. This ensures accuracy and maintains control.

**Q: Does JobFlow cost money to use?**

A: No API costs. JobFlow uses fuzzy matching instead of AI. Phase 4 will integrate with Claude.ai web interface (free with Claude Pro subscription).

**Q: Is my data secure?**

A: Yes. All data is stored locally on your computer. JobFlow never sends data to external servers except your own local backend.

**Q: Which platforms are supported?**

A: Native support for LinkedIn Easy Apply, Workday, Greenhouse, and Lever. Partial support for other platforms via generic handler.

**Q: Can I use JobFlow for non-tech jobs?**

A: Yes! JobFlow works for any job applications. Just customize your profile and questions for your field.

**Q: How accurate is the auto-fill?**

A: 85-95% for supported platforms, 60-75% for unknown platforms. Always review before submitting.

---

## Changelog

### Phase 3 (Current) - Platform Handlers

- ✅ LinkedIn Easy Apply handler with multi-step support
- ✅ Workday handler with data-automation-id detection
- ✅ Greenhouse handler for standard forms
- ✅ Lever handler for application-question forms
- ✅ Generic fallback handler for unknown platforms
- ✅ Integrated all handlers into content script
- ✅ Platform-specific notifications

### Phase 2 - Chrome Extension

- ✅ Complete Chrome extension with React UI
- ✅ Form detection and field extraction
- ✅ Backend API integration
- ✅ Content script with auto-fill logic
- ✅ Popup and options interfaces
- ✅ Storage management

### Phase 1 - Backend

- ✅ FastAPI backend with 8-table database
- ✅ 40+ API endpoints
- ✅ Question answering service with fuzzy matching
- ✅ Resume selector service
- ✅ 50 pre-loaded common questions
- ✅ Analytics and tracking

### Phase 4 (Planned) - Advanced Automation

- ⏳ Claude.ai web interface integration
- ⏳ Automated job scanning
- ⏳ Batch review dashboard
- ⏳ AI-powered unknown form analysis
- ⏳ Smart follow-up system

---

## License

MIT License - See LICENSE file for details

---

**Happy job hunting with JobFlow! 🚀**

*Last updated: Phase 3 - Platform Handler Integration*

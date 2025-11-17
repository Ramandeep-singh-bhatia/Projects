# User Guide

Complete guide to using all features of the Interview Preparation Tracker application.

## Table of Contents

- [Getting Started](#getting-started)
- [Dashboard Overview](#dashboard-overview)
- [Topic Management](#topic-management)
- [Practice Sessions](#practice-sessions)
- [Flashcard System](#flashcard-system)
- [Pomodoro Timer](#pomodoro-timer)
- [Mock Interviews](#mock-interviews)
- [Voice Notes](#voice-notes)
- [Analytics](#analytics)
- [Settings & Configuration](#settings--configuration)
- [Backup & Restore](#backup--restore)
- [Tips & Best Practices](#tips--best-practices)

## Getting Started

### First Time Setup

1. **Access the application:** Open `http://localhost:3000` in your browser
2. **Dashboard appears:** You'll see an empty dashboard initially
3. **Add your first topic:** Click "Topics" in the navigation menu
4. **Configure settings:** Visit Settings to set your daily study goals

### Daily Workflow Recommendation

1. Check Dashboard for topics due for review
2. Start a Pomodoro session for focused study
3. Review flashcards using spaced repetition
4. Log practice sessions after studying
5. Use mock interviews to test yourself
6. Review analytics to track progress
7. Backup your data weekly

## Dashboard Overview

The Dashboard is your command center for interview preparation.

### Main Sections

#### 1. Study Streak
- **Current Streak:** Consecutive days you've studied
- **Longest Streak:** Your record streak
- **Today's Status:** Shows if you've studied today

#### 2. Quick Stats
- **Total Topics:** Number of topics in your library
- **Total Study Time:** Cumulative hours studied
- **Sessions This Week:** Practice sessions in current week
- **Topics Due Today:** Flashcards and topics needing review

#### 3. Revision Suggestions
Smart algorithm suggests topics to review based on:
- Confidence level (lower confidence = higher priority)
- Time since last review (older = higher priority)
- Difficulty level (harder topics weighted more)

**Priority Score Formula:**
```
Priority = Difficulty Weight × Confidence Weight × Recency Weight
```

**How to use:**
1. Topics are sorted by priority (highest first)
2. Click "Start Studying" to begin a Pomodoro session
3. Filter by category to focus on specific areas
4. Each suggestion shows:
   - Topic name and category
   - Current confidence level
   - Days since last review
   - Estimated study time

#### 4. Weekly Progress
- Visual representation of study goals per category
- Progress bars show completion percentage
- Color-coded status: Green (>80%), Yellow (50-80%), Red (<50%)

### Navigation

**Top Menu:**
- Dashboard - Home page overview
- Topics - Manage interview topics
- Flashcards - Spaced repetition system
- Pomodoro - Focus timer
- Mock Interviews - Generate practice sets
- Analytics - Detailed progress metrics
- Settings - Configuration and preferences

## Topic Management

Topics are the foundation of your preparation tracking.

### Adding a Topic

1. **Navigate to Topics page**
2. **Click "Add New Topic" button**
3. **Fill in details:**

   **Required Fields:**
   - **Name:** Topic title (e.g., "Binary Search Trees")
   - **Category:** Select from:
     - Data Structures & Algorithms
     - System Design (High-Level)
     - System Design (Low-Level)
     - Behavioral
     - Databases
     - Networking
     - Operating Systems
   - **Difficulty:** Easy, Medium, or Hard
   - **Confidence:** Rate 1-10 (1 = not confident, 10 = very confident)

   **Optional Fields:**
   - **Status:** Not Started, In Progress, Completed
   - **Estimated Time:** How long to study this topic (minutes)
   - **Source URL:** Link to study resource
   - **Notes:** Your understanding, key points
   - **Things to Remember:** Quick reference points
   - **Reminder Date:** When to review this topic

4. **Click "Save Topic"**

### Viewing Topics

**List View:**
- All topics displayed in cards
- Each card shows:
  - Topic name and category badge
  - Difficulty and confidence indicators
  - Last studied date
  - Quick action buttons

**Filtering:**
- **By Category:** Click category tabs at top
- **By Difficulty:** Filter dropdown
- **By Confidence:** Filter low/medium/high confidence
- **By Status:** Not Started / In Progress / Completed
- **Search:** Type topic name in search box

**Sorting:**
- By Date (newest/oldest)
- By Confidence (low to high / high to low)
- By Name (A-Z / Z-A)
- By Last Studied

### Editing a Topic

1. Find the topic in the list
2. Click "Edit" button (pencil icon)
3. Modify any fields
4. Click "Save Changes"

**When to edit:**
- Update confidence after studying
- Change status as you progress
- Add new notes or resources
- Adjust estimated time

### Deleting a Topic

1. Find the topic
2. Click "Delete" button (trash icon)
3. Confirm deletion in popup

**Warning:** This deletes all associated data:
- Practice sessions
- Flashcards
- Voice notes
- Pomodoro sessions

### Uploading Files to Topics

Each topic can have associated files (PDFs, images, notes).

1. **Open topic details**
2. **Click "Upload File" button**
3. **Select file** (max 10MB)
4. **Supported formats:**
   - Documents: PDF, DOC, DOCX, TXT, MD
   - Images: JPG, PNG, GIF
   - Code: HTML, JSON, XML

5. **File actions:**
   - **Preview:** View images and text files
   - **Download:** Save file locally
   - **Delete:** Remove file

## Practice Sessions

Log your study sessions to track progress and update confidence.

### Creating a Practice Session

1. **Find your topic**
2. **Click "Practice" button**
3. **Fill in session details:**

   **Required:**
   - **Duration:** Study time in minutes
   - **Performance Rating:** 1-10 (how well you understood)
   - **Session Type:**
     - First Learning (initial study)
     - Revision (reviewing known material)
     - Mock Interview (practicing interview questions)
     - Quick Review (brief refresher)

   **Optional:**
   - **What Went Well:** Positive notes
   - **Mistakes Made:** Areas to improve
   - **Session Notes:** Detailed observations
   - **New Confidence:** Update confidence level (1-10)

4. **Click "Save Session"**

**Automatic Updates:**
- Topic's "Last Studied" date updates
- If you enter new confidence, topic confidence updates
- Session added to analytics
- Study streak updates

### Viewing Session History

1. **Open topic details**
2. **Scroll to "Practice History" section**
3. **Each session shows:**
   - Date and duration
   - Performance rating
   - Session type
   - Notes
   - Confidence before/after

4. **Actions:**
   - Edit session details
   - Delete session
   - Filter by date range or type

### Session Analytics

In the Analytics page, view:
- Total sessions count
- Average session duration
- Performance trends over time
- Sessions by category distribution
- Most productive times/days

## Flashcard System

Powerful spaced repetition system using the SuperMemo SM-2 algorithm.

### Understanding Spaced Repetition

**Key Concepts:**
- **Interval:** Days until next review
- **Repetitions:** How many times you've reviewed correctly
- **Ease Factor:** Multiplier for interval calculation (higher = longer intervals)
- **Quality Rating:** Your self-assessment (0-5)

**SM-2 Algorithm:**
- Correct answers (quality ≥3) increase interval
- Incorrect answers (quality <3) reset interval to 1 day
- Ease factor adjusts based on difficulty

### Creating Flashcards

1. **Navigate to Flashcards page**
2. **Click "Create Flashcard"**
3. **Fill in:**
   - **Front:** Question or prompt
     - Example: "What is the time complexity of quicksort?"
   - **Back:** Answer or explanation
     - Example: "Average: O(n log n), Worst: O(n²)"
   - **Topic:** Select associated topic
   - **Difficulty:** Easy, Medium, Hard

4. **Click "Create"**

**Flashcard Examples:**

**For Algorithms:**
- Front: "Implement binary search"
- Back: "Use two pointers, calculate mid, compare..."

**For System Design:**
- Front: "How would you design Twitter?"
- Back: "Key components: User service, Tweet service, Timeline service..."

**For Behavioral:**
- Front: "Tell me about a time you resolved conflict"
- Back: "STAR method: Situation - Team disagreed on architecture..."

### Reviewing Flashcards

#### Due Flashcards

1. **Click "Review Due Cards"**
2. **Card shows front side**
3. **Think of the answer**
4. **Click "Show Answer"**
5. **Back side appears**
6. **Rate your recall (0-5):**
   - **5 - Perfect:** Instant and correct recall
   - **4 - Correct:** Recalled after slight hesitation
   - **3 - Correct with difficulty:** Barely remembered
   - **2 - Wrong:** Answer was incorrect but familiar
   - **1 - Wrong:** Completely forgot but recognized answer
   - **0 - Complete blackout:** No idea even after seeing answer

7. **Next card appears automatically**

**What happens after rating:**
- **Rating ≥3:** Interval increases, ease factor may increase
- **Rating <3:** Interval resets to 1 day, needs more practice
- **Next review date calculated automatically**
- **Stats update (success count, failure count)**

#### Review Queue

Shows all cards due today sorted by:
- Priority (overdue cards first)
- Difficulty (harder cards prioritized)
- Topic relevance

**Progress Indicators:**
- Cards reviewed today: X/Y
- New cards: Count of never-reviewed cards
- Due cards: Count of cards scheduled for today
- Total cards: Your entire flashcard collection

### Managing Flashcards

**Editing:**
1. Find flashcard in "All Flashcards" view
2. Click "Edit"
3. Modify front, back, or topic
4. Save changes (statistics preserved)

**Deleting:**
1. Click "Delete" on flashcard
2. Confirm deletion
3. All review history is permanently deleted

**Filtering:**
- By Topic: See flashcards for specific topic
- By Status: Due / Not Due / All
- By Difficulty: Easy / Medium / Hard
- By Success Rate: High performers vs struggling cards

### Flashcard Statistics

**Per Card:**
- Total reviews
- Success count (quality ≥3)
- Failure count (quality <3)
- Success rate percentage
- Current interval
- Next review date
- Current ease factor

**Overall:**
- Total flashcards
- Cards due today
- Cards mastered (high ease factor)
- Average success rate
- Review streak

### Best Practices for Flashcards

1. **Keep cards atomic:** One concept per card
2. **Make them challenging:** Not too easy or you won't retain
3. **Use clear, concise language**
4. **Include examples on back**
5. **Create reverse cards for key concepts**
6. **Review honestly:** Don't cheat ratings
7. **Regular daily reviews:** Don't skip days
8. **Delete outdated cards**

## Pomodoro Timer

Stay focused with structured study sessions based on the Pomodoro Technique.

### Understanding Pomodoro Technique

**Standard Cycle:**
1. **Focus (25 min):** Concentrated study on one topic
2. **Short Break (5 min):** Relax, stretch, rest eyes
3. **Repeat 3 more times**
4. **Long Break (15 min):** After 4 Pomodoros

**Benefits:**
- Maintains focus and concentration
- Prevents burnout
- Trackable productivity metrics
- Regular breaks improve retention

### Starting a Pomodoro Session

1. **Navigate to Pomodoro page**
2. **Select a topic** (optional but recommended)
3. **Choose phase:**
   - Focus (25 min default)
   - Short Break (5 min)
   - Long Break (15 min)
4. **Enter Pomodoro number** (1-4 for focus sessions)
5. **Click "Start"**

**Timer displays:**
- Countdown timer
- Current phase
- Associated topic
- Pomodoro number
- Pause/Resume button
- Stop button

### During a Pomodoro

**Focus Session:**
- Study the selected topic
- Avoid distractions
- Don't check phone/email
- Stay on one task
- Timer shows remaining time

**Break:**
- Step away from desk
- Stretch or walk
- Drink water
- Don't think about the topic
- Prepare for next Pomodoro

### Completing a Pomodoro

When timer reaches 0:
1. **Notification appears** (if browser allows)
2. **Pomodoro auto-saves to history**
3. **Topic's Pomodoro count increments**
4. **Choose next action:**
   - Start next Pomodoro
   - Take a break
   - Switch topics

### Pomodoro History

**View Past Sessions:**
1. Go to "History" tab on Pomodoro page
2. See all completed Pomodoros:
   - Date and time
   - Topic
   - Phase type
   - Duration
   - Interruptions (if any)

**Statistics:**
- Total Pomodoros completed
- Total focus time
- Average per day
- Pomodoros by topic
- Most productive hours
- Completion rate

### Customizing Pomodoro Settings

In Settings page:
```
Focus Duration: 15-60 minutes (default: 25)
Short Break: 3-10 minutes (default: 5)
Long Break: 10-30 minutes (default: 15)
Auto-start next: Enable/disable
Notifications: Enable/disable
Sound: Choose alert sound
```

### Tips for Effective Pomodoros

1. **Plan ahead:** Know what you'll study before starting
2. **Eliminate distractions:** Close unnecessary tabs, silence phone
3. **Complete full sessions:** Don't stop early
4. **Take breaks seriously:** Resting is part of the technique
5. **Track everything:** Link Pomodoros to topics
6. **Adjust durations:** Find what works for your focus span
7. **Use breaks:** Review flashcards during short breaks

## Mock Interviews

Generate realistic interview question sets to test your preparation.

### Understanding Mock Interviews

Mock interviews simulate real technical interviews by:
- Selecting questions from your topics
- Balancing difficulty and categories
- Prioritizing weak areas
- Creating time pressure
- Tracking your performance

### Generating a Mock Interview

1. **Navigate to Mock Interviews page**
2. **Click "Generate New Interview"**
3. **Configure interview:**
   - **Number of questions:** 5-20 (typically 10-15)
   - **Duration:** 30-120 minutes
   - **Categories:** Select which categories to include
     - DSA, System Design, Behavioral, etc.
   - **Difficulty distribution:**
     - Balanced (mix of all)
     - Beginner (mostly Easy/Medium)
     - Advanced (mostly Medium/Hard)
   - **Focus on weak areas:** Toggle ON to prioritize low-confidence topics

4. **Click "Generate"**

**Algorithm Details:**
- Questions selected based on confidence (lower = more likely)
- Categories distributed evenly
- Difficulty matches your selection
- Prevents duplicates from recent interviews
- Limits questions per category for variety

### Taking a Mock Interview

**Interview Page Shows:**
- Timer (counts up or down based on settings)
- Question list numbered
- Category and difficulty for each
- Space for your answers
- Confidence rating per question

**How to proceed:**

1. **Start timer** when ready
2. **Work through questions** in order (or jump around)
3. **Write your answers** in text area
4. **Rate confidence** after answering each
5. **Note struggles** or concepts to review
6. **Complete within time limit** if possible

### Ending a Mock Interview

1. **Click "Complete Interview"**
2. **Review Summary shows:**
   - Total time taken
   - Questions answered
   - Confidence by category
   - Topics to review
   - Performance compared to previous interviews

3. **Actions:**
   - Create flashcards for weak questions
   - Schedule practice sessions
   - Update topic confidence levels

### Mock Interview History

**View Past Interviews:**
- Date and duration
- Question count and categories
- Average confidence rating
- Questions asked
- Your answers and notes
- Performance trends

**Analytics:**
- Total mock interviews completed
- Average score/confidence
- Improvement over time
- Most challenging categories
- Question types struggled with

### Mock Interview Types

**1. Full Technical Interview**
- 10-15 questions
- Mix of DSA, System Design
- 60-90 minutes
- Simulates real coding interview

**2. System Design Focus**
- 5-8 questions
- Only System Design topics
- 45-60 minutes
- Deep dive into architecture

**3. Rapid Fire**
- 20+ questions
- Quick recall
- 30 minutes
- Tests breadth of knowledge

**4. Behavioral Round**
- 8-12 behavioral questions
- 30-45 minutes
- Practice STAR method responses

### Best Practices

1. **Simulate real conditions:** No phone, quiet space, time yourself
2. **Don't look up answers:** Test actual recall
3. **Review immediately after:** While fresh in mind
4. **Create flashcards:** For struggled questions
5. **Track trends:** Are you improving?
6. **Regular schedule:** Weekly mock interviews
7. **Mix difficulties:** Don't only do easy questions

## Voice Notes

Record audio explanations to reinforce learning.

### Why Voice Notes?

**Benefits:**
- Verbalize complex concepts
- Hear your own explanations
- Create audio study materials
- Practice explaining to others
- Review while commuting

### Recording Voice Notes

1. **Navigate to topic details**
2. **Click "Voice Notes" tab**
3. **Click "Record New Note" button**
4. **Allow microphone access** (browser will prompt)
5. **Recording interface appears:**
   - Red recording indicator
   - Timer showing recording duration
   - Pause/Resume button
   - Stop button
   - Audio level indicator

6. **Speak clearly** about the topic:
   - Explain key concepts
   - Walk through examples
   - Mention edge cases
   - Describe approach

7. **Click "Stop Recording"**
8. **Preview your recording:**
   - Play button to listen
   - Re-record if not satisfied
   - Add title/description

9. **Click "Save"**

**Recording Tips:**
- Use good microphone
- Quiet environment
- Speak at moderate pace
- Organize thoughts before starting
- Keep recordings under 5 minutes

### Managing Voice Notes

**Playback:**
1. Go to topic's Voice Notes tab
2. Click play on any recording
3. Controls: Play/Pause, Skip, Volume, Speed

**Listing:**
- All voice notes for topic shown
- Sorted by date (newest first)
- Shows duration and timestamp
- Search by title

**Editing:**
- Update title/description
- Cannot edit audio itself
- Re-record if changes needed

**Deleting:**
- Click delete button
- Confirm deletion
- Audio file permanently removed

**Downloading:**
- Click download button
- Saves as .webm audio file
- Listen offline or on mobile

### Use Cases for Voice Notes

**1. Concept Explanation**
- Record yourself explaining Binary Search Tree
- Listen back to identify gaps in understanding
- Re-record until explanation is clear

**2. Algorithm Walkthrough**
- Talk through algorithm steps
- Explain time/space complexity
- Discuss edge cases

**3. System Design Architecture**
- Describe components
- Explain data flow
- Discuss trade-offs

**4. Interview Preparation**
- Practice explaining aloud
- Record STAR method responses
- Improve communication clarity

**5. Quick Reminders**
- Record quick tips
- Mention common mistakes
- Note what to remember

### Technical Details

**Storage:**
- Audio files stored in `uploads/audio/`
- Metadata in database
- Files named with unique IDs

**Format:**
- WebM audio codec (browser native)
- Compressed for efficiency
- Typical size: 1-2 MB per minute

**Compatibility:**
- Works in Chrome, Firefox, Edge
- Safari requires permissions
- Mobile browsers supported

## Analytics

Comprehensive metrics to track your preparation progress.

### Dashboard Analytics

**Overview Cards:**
- Total Topics
- Total Study Time
- Practice Sessions
- Study Streak
- Flashcards Mastered
- Mock Interviews Completed

### Study Time Analytics

**Total Time:**
- Cumulative hours studied
- Breakdown by:
  - Practice sessions
  - Pomodoro sessions
  - Flashcard reviews
  - Mock interviews

**Time Trends:**
- Last 7 days study time chart
- Last 30 days study time chart
- Time by day of week
- Most productive hours

**Time by Category:**
- Pie chart showing distribution
- Identify over/under-studied areas
- Compare to your goals

### Topic Analytics

**Confidence Distribution:**
- Count of topics by confidence level (1-10)
- Visual histogram
- Identify weak areas

**Topics by Category:**
- Bar chart of topic counts
- Compare coverage across categories

**Topics by Status:**
- Not Started vs In Progress vs Completed
- Completion rate percentage

**Topics by Difficulty:**
- Easy vs Medium vs Hard distribution
- Helps balance difficulty coverage

### Session Analytics

**Session Frequency:**
- Sessions per day/week/month
- Trend line showing consistency
- Identify study gaps

**Performance Trends:**
- Average performance rating over time
- Shows if you're improving
- Performance by category

**Session Type Distribution:**
- First Learning vs Revision vs Mock Interview
- Helps ensure balanced approach

### Flashcard Analytics

**Review Statistics:**
- Cards reviewed per day
- Review streak
- Average quality rating
- Success rate trends

**Card Difficulty:**
- Success rates by difficulty
- Identify challenging categories
- Cards needing more review

**Interval Distribution:**
- How many cards at each interval
- Shows knowledge retention
- Maturity of your deck

### Confidence Decay Analytics

**Decay Events:**
- Count of confidence decays
- Topics affected most
- Decay prevented by timely review

**Stale Topics:**
- Topics not studied recently
- Days since last review
- Recommended action: Review soon

**Confidence History:**
- Timeline of confidence changes
- Reasons for changes (session, decay, manual)
- Trend per topic

### Streak Analytics

**Current Streak:**
- Consecutive days studied
- Shows today's status
- Warning if streak at risk

**Longest Streak:**
- Your personal record
- Date achieved
- Motivation metric

**Streak Calendar:**
- Visual calendar heatmap
- Green for study days
- Gray for missed days
- Patterns in your consistency

### Category Performance

**Detailed per Category:**
- Average confidence
- Total topics
- Total study time
- Completion rate
- Upcoming reviews

**Comparison:**
- Identify strongest categories
- Find weak areas needing focus
- Balance your preparation

### Export Analytics

1. **Click "Export Analytics"**
2. **Choose format:**
   - CSV (for Excel/Sheets)
   - JSON (for data analysis)
   - PDF (for reporting)
3. **Select date range**
4. **Select metrics to include**
5. **Download file**

**Uses:**
- Share with study partners
- Track long-term trends
- Portfolio documentation
- Job search proof of preparation

## Settings & Configuration

Customize the application to match your preferences and goals.

### General Settings

**Profile:**
- Display Name
- Study Goal (hours/day)
- Week Start Day (Monday/Sunday)

**Preferences:**
- Theme: Light / Dark / Auto
- Date Format: MM/DD/YYYY or DD/MM/YYYY
- Time Format: 12-hour or 24-hour
- Timezone

### Study Goals

**Daily Goals:**
- Target study hours per day
- Target sessions per day
- Target flashcard reviews per day

**Weekly Goals by Category:**
- Data Structures & Algorithms: X hours
- System Design: Y hours
- Behavioral: Z hours
- (etc. for all categories)

**Goal Tracking:**
- Progress bars show completion
- Notifications when goals met
- Weekly summary email (optional)

### Notification Settings

**Enable/Disable:**
- Study reminders
- Flashcard due notifications
- Goal achievement alerts
- Streak warnings
- Mock interview reminders

**Reminder Schedule:**
- Daily study reminder time
- Flashcard review reminder time
- Weekend reminders (on/off)

### Pomodoro Settings

- Focus Duration: 15-60 minutes (default: 25)
- Short Break: 3-10 minutes (default: 5)
- Long Break: 10-30 minutes (default: 15)
- Long Break Interval: After X Pomodoros (default: 4)
- Auto-start breaks: Yes/No
- Auto-start Pomodoros: Yes/No
- Sound notifications: Enable/Disable
- Desktop notifications: Enable/Disable

### Confidence Decay Settings

**Decay Rules:**
- Enable automatic decay: Yes/No
- Days inactive before decay: 1-90 days (default: 7)
- Decay percentage: 1-20% (default: 5)
- Apply to all categories: Yes/No
- Category-specific rules (optional)

**Manual Decay:**
- Run decay check immediately
- View decay history
- Exclude specific topics

### Data Management

**Storage Info:**
- Total database size
- Uploaded files size
- Number of audio recordings
- Last backup date

**Data Operations:**
- Export All Data
- Import Data
- Create Backup
- Reset All Data (destructive)

## Backup & Restore

Protect your preparation data with regular backups.

### Creating a Backup

**Automatic Backup:**
1. Go to Settings → Data Management
2. Enable "Auto Backup"
3. Set frequency (daily, weekly, monthly)
4. Backups saved to `uploads/backups/`

**Manual Backup:**
1. Settings → Data Management
2. Click "Create Backup Now"
3. Choose what to include:
   - Topics and sessions (required)
   - Flashcards (recommended)
   - Voice notes metadata (files separate)
   - Settings
   - Pomodoro history
   - Mock interview history

4. Click "Create Backup"
5. File downloads automatically

**Backup File:**
- JSON format
- Filename: `backup_YYYY-MM-DD_HH-MM-SS.json`
- Includes all selected data
- Human-readable (can open in text editor)

### Restoring from Backup

**Before Restoring:**
- Backup your current data first
- Understand restore will overwrite existing data
- Close other browser tabs using the app

**Restore Steps:**
1. Settings → Data Management
2. Click "Import Data"
3. Choose restore mode:
   - **Replace All:** Deletes current data, imports backup
   - **Merge:** Combines backup with current data
   - **Preview:** Shows what would be imported

4. Select backup file (.json)
5. Review import summary:
   - Topics to import: X
   - Flashcards to import: Y
   - Sessions to import: Z
   - Conflicts: A items

6. Click "Confirm Import"
7. Wait for completion (may take 30-60 seconds)
8. Page refreshes with restored data

**Merge Conflicts:**
- Duplicate topics: Renames with (imported)
- Duplicate flashcards: Skips or merges stats
- Settings: Backup values overwrite current

### Backup Best Practices

1. **Backup weekly:** Set reminder or enable auto-backup
2. **Multiple locations:** Store backups in cloud (Dropbox, Google Drive)
3. **Before major changes:** Backup before bulk delete or import
4. **Test restores:** Periodically verify backups work
5. **Version control:** Keep multiple backup versions
6. **Migration:** Use backups to move between devices

### What's Included in Backups

**Always Included:**
- All topics with full details
- Practice sessions
- Settings configuration
- Weekly goal history

**Optionally Included:**
- Flashcards with review history
- Pomodoro sessions
- Mock interview records
- Confidence decay history
- Voice note metadata (not audio files)

**Not Included:**
- Uploaded files (PDFs, documents)
- Voice note audio files
- Database internal IDs (regenerated on import)

### Migrating to New Computer

1. **Old computer:**
   - Create full backup (include everything)
   - Download backup JSON file
   - Copy `uploads/` folder manually

2. **New computer:**
   - Install and setup application
   - Import backup JSON file
   - Copy uploaded files to `uploads/` directory
   - Verify all data present

## Tips & Best Practices

### Study Strategy

1. **Start with weak areas:** Use confidence analytics to identify gaps
2. **Balance breadth and depth:** Cover all categories, but master key topics
3. **Consistent daily practice:** 30 minutes daily beats 5 hours once a week
4. **Use all tools together:** Pomodoro + Flashcards + Sessions = comprehensive tracking
5. **Mock interviews weekly:** Test yourself regularly
6. **Review analytics monthly:** Adjust strategy based on data

### Topic Management

1. **Break down large topics:** Create sub-topics for complex areas
2. **Link related topics:** Use notes to cross-reference
3. **Update confidence honestly:** Overconfidence hurts preparation
4. **Set realistic goals:** Don't overwhelm yourself
5. **Archive completed topics:** Keep database clean

### Flashcard Creation

1. **Create cards immediately:** When you learn something new
2. **Test both directions:** Create reverse cards
3. **Include examples:** Concrete examples help memory
4. **Keep cards focused:** One concept per card
5. **Delete bad cards:** If a card isn't helpful, remove it
6. **Cloze deletion style:** "Quicksort has ___ average time complexity" (O(n log n))

### Time Management

1. **Pomodoros for deep work:** Use for difficult topics
2. **Flashcards during breaks:** Efficient use of time
3. **Track everything:** More data = better insights
4. **Voice notes while fresh:** Record explanations immediately
5. **Schedule mock interviews:** Plan ahead, treat seriously

### Motivation & Consistency

1. **Track your streak:** Gamify daily practice
2. **Set achievable goals:** Build confidence with small wins
3. **Celebrate milestones:** Acknowledge 100 flashcards, 50 topics, etc.
4. **Review progress:** Look back at how far you've come
5. **Join community:** Share goals with study partners

### Data Management

1. **Weekly backups:** Make it a habit
2. **Clean old data:** Archive topics you won't review
3. **Optimize storage:** Delete unused files
4. **Export analytics:** Create portfolio documentation
5. **Regular maintenance:** Check for stale data

### Common Mistakes to Avoid

1. **Only studying easy topics:** Balance difficulty
2. **Ignoring spaced repetition:** Review on schedule
3. **Not tracking sessions:** Can't improve what you don't measure
4. **Skipping mock interviews:** Necessary for test-taking skills
5. **Setting unrealistic goals:** Leads to burnout
6. **Never taking breaks:** Pomodoro breaks are essential
7. **Forgetting to backup:** Lost data is devastating

---

**You're now ready to use all features of the Interview Preparation Tracker!**

For technical details, see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

For API reference, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

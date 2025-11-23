# Complete Guide - AI-Powered English Learning Application

**Version 2.0.0 | Complete User & Developer Guide**

This comprehensive guide covers everything you need to know about the AI-Powered English Learning Application - from initial setup to advanced usage, deployment, and development.

---

## Table of Contents

### Part 1: Getting Started
1. [Introduction](#1-introduction)
2. [Quick Start Guide](#2-quick-start-guide)
3. [System Requirements](#3-system-requirements)
4. [Installation](#4-installation)
5. [Initial Configuration](#5-initial-configuration)

### Part 2: Using the Application
6. [First-Time Setup](#6-first-time-setup)
7. [Understanding the Dashboard](#7-understanding-the-dashboard)
8. [Core Learning Modules](#8-core-learning-modules)
9. [Advanced Features Guide](#9-advanced-features-guide)
10. [Daily Practice Workflows](#10-daily-practice-workflows)

### Part 3: Technical Details
11. [Architecture Overview](#11-architecture-overview)
12. [Data Storage & Management](#12-data-storage--management)
13. [AI Integration](#13-ai-integration)
14. [Services Documentation](#14-services-documentation)
15. [State Management](#15-state-management)

### Part 4: Deployment
16. [Local Development](#16-local-development)
17. [Production Build](#17-production-build)
18. [Deployment Options](#18-deployment-options)
19. [Environment Variables](#19-environment-variables)
20. [Security Considerations](#20-security-considerations)

### Part 5: Advanced Topics
21. [Customization Guide](#21-customization-guide)
22. [Extending Features](#22-extending-features)
23. [Performance Optimization](#23-performance-optimization)
24. [Troubleshooting](#24-troubleshooting)
25. [FAQs](#25-faqs)

---

## Part 1: Getting Started

### 1. Introduction

#### What is this Application?

The AI-Powered English Learning Application is a comprehensive, intelligent language learning platform designed specifically for non-native English speakers who want to improve their speaking and writing skills through contextual, real-world practice.

#### Key Differentiators

Unlike traditional language learning apps, this application:
- **Learns from YOU**: Builds personal context around your life, work, and interests
- **Identifies Patterns**: Automatically detects recurring mistakes and provides targeted correction
- **Adapts Intelligently**: Adjusts difficulty, recommendations, and content based on your performance
- **Focuses on Context**: Teaches words and phrases in realistic situations, not isolated vocabulary lists
- **Comprehensive Coverage**: 10 advanced services covering every aspect of language learning

#### Who Should Use This App?

- **Non-native English speakers** at any level (beginner to advanced)
- **Job seekers** preparing for interviews in English
- **Students** preparing for IELTS, TOEFL, or academic English
- **Professionals** needing business English skills
- **Travelers** wanting essential travel English
- **Anyone** who wants to improve conversational fluency

#### What You'll Learn

- Natural conversation skills
- Professional communication (emails, meetings, presentations)
- Pronunciation and accent reduction
- Vocabulary in context with proper usage
- Grammar through practical application
- Cultural awareness and appropriate language use
- How to learn effectively (meta-learning)

---

### 2. Quick Start Guide

**Get up and running in 5 minutes:**

#### Step 1: Clone or Download
```bash
# If you have git installed
git clone <repository-url>
cd ai-english-learning-app

# Or download and extract the ZIP file
```

#### Step 2: Install Dependencies
```bash
npm install
```

#### Step 3: Start the Application
```bash
npm run dev
```

#### Step 4: Open in Browser
Navigate to `http://localhost:3000`

#### Step 5: Configure AI (Optional but Recommended)
1. Click Settings (gear icon)
2. Choose one:
   - **Option A**: Enter Anthropic API key for Claude
   - **Option B**: Enable "Use Local Model" for Ollama (requires Ollama installed)

#### Step 6: Complete Baseline Assessment
Answer 8 questions to set your initial proficiency level.

#### Step 7: Start Learning!
Choose any module from the dashboard and begin practicing.

---

### 3. System Requirements

#### Minimum Requirements

**Hardware:**
- Processor: Dual-core 1.6 GHz or faster
- RAM: 4 GB
- Storage: 500 MB free space
- Internet: Stable connection for AI features

**Software:**
- Operating System: Windows 10+, macOS 10.14+, or Linux
- Node.js: Version 16.0.0 or higher
- npm: Version 7.0.0 or higher
- Modern Web Browser: Chrome 90+, Firefox 88+, Edge 90+, Safari 14+

#### Recommended Requirements

**Hardware:**
- Processor: Quad-core 2.0 GHz or faster
- RAM: 8 GB or more
- Storage: 2 GB free space
- Internet: High-speed broadband

**Software:**
- Node.js: Latest LTS version (20.x)
- Browser: Latest Chrome or Edge (for full speech recognition support)

#### Optional Requirements

**For Local AI (Ollama):**
- Additional RAM: 8 GB (16 GB recommended)
- Storage: 5-10 GB for AI models
- Ollama installed and running

**For Speech Recognition:**
- Microphone
- Chrome or Edge browser
- HTTPS connection (or localhost)

---

### 4. Installation

#### Option A: Standard Installation (Recommended)

**Step 1: Install Node.js**

1. Visit [nodejs.org](https://nodejs.org)
2. Download the LTS version for your operating system
3. Run the installer and follow the prompts
4. Verify installation:
   ```bash
   node --version  # Should show v16.0.0 or higher
   npm --version   # Should show 7.0.0 or higher
   ```

**Step 2: Get the Application**

```bash
# Option 1: Clone with Git
git clone <repository-url>
cd ai-english-learning-app

# Option 2: Download ZIP
# 1. Download from GitHub
# 2. Extract to your desired location
# 3. Open terminal/command prompt in that folder
```

**Step 3: Install Dependencies**

```bash
npm install
```

This will install:
- React and React Router
- Zustand (state management)
- Recharts (data visualization)
- Lucide React (icons)
- Vite (build tool)
- Better-SQLite3 (database)

**Expected Output:**
```
added 243 packages in 45s
```

**Step 4: Initialize Database (Optional)**

For Node.js environment with SQLite:
```bash
npm run init-db
```

For Phase 1 advanced features:
```bash
npm run init-db-advanced
```

**Step 5: Verify Installation**

```bash
npm run dev
```

If successful, you'll see:
```
  VITE v5.0.x ready in 523 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

#### Option B: Quick Installation (One Command)

```bash
npm install && npm run init-db && npm run init-db-advanced && npm run dev
```

#### Troubleshooting Installation

**Issue: "Node.js not found"**
- Install Node.js from nodejs.org
- Restart terminal after installation

**Issue: "npm install fails"**
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

**Issue: "Port 3000 already in use"**
- Change port in `vite.config.js`:
  ```javascript
  export default defineConfig({
    server: {
      port: 3001  // Change to any available port
    }
  })
  ```

**Issue: "Permission denied"**
- On Linux/Mac, don't use `sudo` with npm
- Fix npm permissions: [docs.npmjs.com/resolving-eacces-permissions-errors](https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally)

---

### 5. Initial Configuration

#### AI Service Configuration

The application supports two AI backends:

**Option 1: Claude API (Cloud-based, Best Quality)**

1. **Get API Key:**
   - Visit [console.anthropic.com](https://console.anthropic.com)
   - Sign up for an account
   - Navigate to API Keys
   - Create a new key
   - Copy the key (starts with `sk-ant-`)

2. **Configure in App:**
   - Open the app at `http://localhost:3000`
   - Click Settings icon (gear) in top right
   - Paste your API key in "Anthropic API Key" field
   - Click "Save Settings"

3. **Alternative: Environment Variable:**
   - Create `.env` file in project root:
     ```env
     VITE_ANTHROPIC_API_KEY=sk-ant-your-key-here
     ```
   - Restart the dev server

**Option 2: Ollama (Local, Free, Private)**

1. **Install Ollama:**
   - Visit [ollama.ai](https://ollama.ai)
   - Download for your OS
   - Run the installer

2. **Download a Model:**
   ```bash
   ollama pull llama3
   # Or other models:
   # ollama pull mistral
   # ollama pull codellama
   ```

3. **Start Ollama Service:**
   ```bash
   ollama serve
   ```

4. **Configure in App:**
   - Open Settings in the app
   - Toggle "Use Local Model" to ON
   - Model name defaults to "llama3"
   - Ensure Ollama is running

**Which Should You Choose?**

| Feature | Claude API | Ollama |
|---------|-----------|--------|
| **Cost** | Paid (pay per use) | Free |
| **Quality** | Excellent | Good |
| **Speed** | Fast (with internet) | Very fast (local) |
| **Privacy** | Data sent to Anthropic | Completely private |
| **Setup** | Easy (just API key) | Moderate (install required) |
| **Offline** | ❌ No | ✅ Yes |

**Recommendation:**
- **Start with Claude API** for best quality
- **Switch to Ollama** if you want privacy or offline access

#### Database Configuration

The app automatically detects the environment:

**Browser Environment (Default):**
- Uses localStorage
- No configuration needed
- Data stored in browser
- Maximum ~5-10 MB storage

**Node.js Environment (Optional):**
- Uses SQLite database
- Run `npm run init-db` to create database
- Data stored in `database/learning.db`
- Unlimited storage capacity

**To use SQLite in development:**
```bash
# Initialize base database
npm run init-db

# Initialize advanced features
npm run init-db-advanced
```

#### Browser Configuration

**Recommended Browser: Chrome or Edge**
- Full support for all features
- Speech recognition included
- Best performance

**Firefox/Safari:**
- Most features work
- No speech recognition
- Slightly slower AI calls

**Mobile Browsers:**
- Responsive design works
- Limited speech support
- Smaller screens may affect UX

---

## Part 2: Using the Application

### 6. First-Time Setup

When you first open the application, you'll go through a one-time setup process.

#### Step 1: Welcome Screen

You'll see a welcome message explaining the app's purpose.

**What to do:**
- Read the introduction
- Click "Get Started" or "Begin Assessment"

#### Step 2: Baseline Assessment

The app will ask you 8 questions to gauge your current English level.

**Question Types:**
1. **Grammar Questions** (2-3 questions)
   - Sentence correction
   - Choose the right word
   - Example: "She ___ to work every day." (go/goes/going)

2. **Vocabulary Questions** (2-3 questions)
   - Word meaning
   - Usage in context
   - Example: "What does 'ambitious' mean?"

3. **Conversation Questions** (2-3 questions)
   - How would you respond in a situation
   - Appropriate phrasing
   - Example: "How would you politely decline an invitation?"

**Tips for Assessment:**
- Answer honestly - this helps the app customize to YOUR level
- Don't look up answers - it's not a test, it's a calibration
- If unsure, choose your best guess
- Takes 5-10 minutes to complete

#### Step 3: Results & Profile Creation

After completing the assessment, you'll see:

**Your Proficiency Score (0-100):**
- 0-20: Beginner (A1)
- 20-40: Elementary (A2)
- 40-60: Intermediate (B1)
- 60-75: Upper Intermediate (B2)
- 75-90: Advanced (C1)
- 90-100: Proficient (C2)

**Skill Breakdown:**
- Vocabulary: X/100
- Grammar: X/100
- Fluency: X/100
- Context Usage: X/100
- Writing: X/100

**Personalized Recommendations:**
Based on your scores, the app will suggest:
- Which modules to start with
- Recommended difficulty level
- Focus areas for improvement

**What to do:**
- Review your results
- Set your learning goal (optional)
- Click "Go to Dashboard"

#### Step 4: Dashboard Tour

On your first visit to the dashboard, you'll see:

1. **Welcome Message** with your name
2. **Current Proficiency Score** in the center
3. **Skills Overview** chart showing your strengths/weaknesses
4. **Learning Modules** cards for each practice type
5. **Recent Activity** (empty at first)
6. **Daily Streak** counter

**Take a moment to:**
- Explore each section
- Click on a module card to see what's inside
- Check Settings to configure preferences

#### Step 5: Choose Your First Module

**Recommended Starting Points by Level:**

**Beginner (0-40):**
1. Start with **Vocabulary Practice** - Learn essential words in context
2. Then try **Small Talk Mastery** - Basic conversational phrases
3. Build up to **Conversation Practice** - Simple dialogues

**Intermediate (40-60):**
1. Start with **Conversation Practice** - Role-play scenarios
2. Try **Grammar Practice** - Solidify your foundations
3. Move to **Writing Practice** - Express yourself in writing

**Advanced (60-100):**
1. Jump into **Conversation Practice** - Complex scenarios
2. Try **Weekly Challenges** - Test your skills
3. Explore **Writing Practice** - Advanced composition

**Click on your chosen module and start learning!**

---

### 7. Understanding the Dashboard

The dashboard is your home base. Let's understand each section.

#### Top Bar

**Left Side:**
- **App Logo/Name**: Click to return to dashboard from any page
- **Navigation Links**: Quick access to all modules

**Right Side:**
- **Streak Counter**: Shows current daily streak (🔥 7 days)
- **Settings Icon**: Access configuration panel
- **Profile Icon**: (Future feature) Your profile

#### Main Dashboard Sections

**1. Welcome Banner**
```
┌─────────────────────────────────────────┐
│  Welcome back, [Your Name]!             │
│  Keep up the great work! 🎯             │
└─────────────────────────────────────────┘
```

**2. Proficiency Score Widget**
```
┌─────────────────────────────────────────┐
│        Current Proficiency              │
│              68/100                      │
│         [Progress Bar]                   │
│     Upper Intermediate (B2)              │
└─────────────────────────────────────────┘
```

Shows your overall score and CEFR level.

**3. Skills Overview Chart**
```
┌─────────────────────────────────────────┐
│         Your Skills Radar               │
│                                          │
│      Vocabulary ●                        │
│               70                         │
│    Grammar ●────●  Fluency              │
│         65      68                       │
│         ●────●────●                      │
│    Writing  Context                      │
│      72      66                          │
└─────────────────────────────────────────┘
```

Visual representation of your 5 core skills.

**4. Learning Modules Grid**
```
┌──────────┐ ┌──────────┐ ┌──────────┐
│💬 Conver │ │📚 Vocabu │ │✍️ Writin│
│  sation  │ │  lary    │ │  g       │
│          │ │          │ │          │
│[Practice]│ │[Practice]│ │[Practice]│
└──────────┘ └──────────┘ └──────────┘

┌──────────┐ ┌──────────┐ ┌──────────┐
│📖 Gramma │ │💭 Small  │ │🏆 Weekly │
│  r       │ │  Talk    │ │ Challenge│
│          │ │          │ │          │
│[Practice]│ │[Practice]│ │[Start]   │
└──────────┘ └──────────┘ └──────────┘
```

Click any card to enter that module.

**5. Progress Chart**
```
┌─────────────────────────────────────────┐
│      Your Progress (Last 7 Days)        │
│                                          │
│  75┤                            ●        │
│  70┤                    ●               │
│  65┤            ●                       │
│  60┤    ●                               │
│  55┤●                                   │
│    └────────────────────────────────    │
│    Mon  Tue  Wed  Thu  Fri  Sat  Sun   │
└─────────────────────────────────────────┘
```

Shows your daily proficiency score over the last week.

**6. Recent Activity Feed**
```
┌─────────────────────────────────────────┐
│         Recent Activity                  │
│                                          │
│ 🎯 Completed Conversation Practice      │
│    Score: 85/100 • 15 min ago          │
│                                          │
│ 📚 Learned 10 new words                │
│    Vocabulary Practice • 1 hour ago     │
│                                          │
│ ✍️ Submitted writing task               │
│    Score: 78/100 • 2 hours ago         │
└─────────────────────────────────────────┘
```

Shows your last 5-10 activities.

**7. Recommendations Panel**
```
┌─────────────────────────────────────────┐
│       Recommended For You               │
│                                          │
│ ⚠️ HIGH: Practice grammar              │
│    You've made repeated article errors  │
│                                          │
│ 💡 MEDIUM: Review vocabulary           │
│    15 words due for review today        │
│                                          │
│ ✨ TIP: Try conversation practice      │
│    Your fluency is improving!           │
└─────────────────────────────────────────┘
```

AI-powered suggestions on what to practice next.

#### Dashboard Actions

**What You Can Do:**
- Click any module to start practicing
- View detailed progress by clicking the chart
- Click recommendations to take action
- Access Settings to configure AI, goals, preferences
- View your streak and achievements

---

### 8. Core Learning Modules

#### Module 1: Conversation Practice

**Purpose:** Practice real-world conversations in realistic scenarios.

**How It Works:**

1. **Choose a Scenario:**
   - Restaurant (ordering food, complaints, special requests)
   - Job Interview (questions, answers, professional talk)
   - Coffee Shop (small talk, ordering, casual conversation)
   - Business Meeting (proposals, discussions, negotiations)
   - Shopping (asking for sizes, prices, returns)
   - Doctor's Office (describing symptoms, understanding advice)
   - And more...

2. **Start the Conversation:**
   - AI plays the other person (waiter, interviewer, colleague, etc.)
   - You respond to their prompts
   - Type your response OR use speech-to-text (microphone button)

3. **Get Feedback:**
   After each response, AI evaluates:
   - **Appropriateness** (0-10): Is it suitable for the context?
   - **Grammar** (0-10): Correct sentence structure?
   - **Vocabulary** (0-10): Good word choice?
   - **Overall Score** (0-100): Combined assessment

4. **See Suggestions:**
   - Alternative ways to phrase your response
   - Better vocabulary choices
   - Grammar corrections
   - Cultural tips

**Example Walkthrough:**

```
Scenario: Restaurant - Ordering Food
Difficulty: Intermediate

AI (Waiter): "Good evening! Welcome to Mario's.
              Have you dined with us before?"

You type: "No, this is my first time. What do
          you recommend?"

AI Feedback:
✅ Appropriateness: 9/10 (Perfect for the context)
✅ Grammar: 10/10 (Correct structure)
✅ Vocabulary: 8/10 (Good, could be more specific)

💡 Alternative: "No, this is my first time here.
                 Do you have any specialties?"

AI (Waiter): "Our special tonight is grilled
              salmon with vegetables. Very popular!"

You type: "That sounds great. I'll take it."

AI Feedback:
✅ Appropriateness: 10/10
✅ Grammar: 10/10
✅ Vocabulary: 7/10

💡 Tip: In restaurants, you can say "I'll have..."
        which sounds more natural than "I'll take..."

[Conversation continues for 5-8 exchanges]

Final Score: 87/100 ⭐⭐⭐⭐
```

**Features:**
- ✅ 15+ realistic scenarios
- ✅ Adaptive difficulty (easy/medium/hard)
- ✅ Speech-to-text input support
- ✅ Real-time feedback
- ✅ Alternative phrasings
- ✅ Progress tracking

**Tips for Success:**
- Write naturally - don't overthink grammar
- Use speech-to-text for pronunciation practice
- Read the alternative suggestions
- Repeat scenarios at higher difficulty levels
- Pay attention to cultural tips

---

#### Module 2: Vocabulary Practice

**Purpose:** Learn words through actual usage scenarios, not isolated lists.

**How It Works:**

1. **Scenario-Based Learning:**
   Instead of random words, you learn vocabulary in context:
   - **At Work**: deadline, colleague, meeting, presentation
   - **Travel**: itinerary, boarding pass, luggage, reservation
   - **Daily Life**: groceries, errands, appointment, schedule

2. **Exercise Types:**

   **A. Fill in the Blank:**
   ```
   Context: Business Email

   "I wanted to _____ on our conversation from yesterday's meeting."

   Options:
   a) follow up
   b) follow through
   c) follow down
   d) follow around

   [Your answer: a]

   ✅ Correct! "Follow up" means to revisit a previous topic.

   Usage: "I'll follow up with you next week."
   ```

   **B. Match Words to Definitions:**
   ```
   Match these business words:

   1. Agenda        a) Work that must be done
   2. Deliverable   b) List of meeting topics
   3. Stakeholder   c) Person affected by project
   4. Deadline      d) Due date for completion

   [Drag and drop to match]
   ```

   **C. Usage in Context:**
   ```
   Word: "Ambitious"

   Which sentence uses "ambitious" correctly?

   a) The meeting was very ambitious. ❌
   b) She has ambitious goals for her career. ✅
   c) I feel ambitious today. ❌
   d) That's an ambitious color. ❌

   Explanation: "Ambitious" describes goals, plans, or
   people who have big aspirations.
   ```

3. **Mastery Tracking:**
   Each word has a mastery level:
   - 🔴 New (0-25%): Just learned
   - 🟡 Learning (25-50%): Seen a few times
   - 🟢 Familiar (50-75%): Can use in exercises
   - ⭐ Mastered (75-100%): Consistently correct

4. **Spaced Repetition:**
   Words automatically return for review:
   - Correct answer → Review in 3 days
   - Incorrect → Review tomorrow
   - Mastered → Review in 1 week

**Example Session:**

```
Session: Business Vocabulary (Intermediate)

Word 1/10: "Leverage"
Definition: To use something to maximum advantage

Example: "We can leverage our expertise to win clients."

Exercise: Choose the correct usage:
a) Can you leverage me your pen?
b) Let's leverage this opportunity.  ✅
c) I leverage at the gym.

[You select: b]
Correct! +10 points

---

Word 2/10: "Stakeholder"
[Exercise continues...]

---

Session Complete!
- Words Practiced: 10
- Correct: 8/10 (80%)
- New Words Learned: 3
- Words Due for Review: 5

Next Review: Tomorrow (5 words)
```

**Features:**
- ✅ 1000+ words organized by context
- ✅ Spaced repetition system
- ✅ Multiple exercise types
- ✅ Real usage examples
- ✅ Mastery tracking
- ✅ Daily review reminders

**Tips for Success:**
- Practice vocabulary daily (even 5 minutes helps)
- Create your own sentences with new words
- Use the "Context Cards" feature (Phase 1) to add personal examples
- Review mastered words periodically
- Focus on high-frequency words first

---

#### Module 3: Grammar Practice

**Purpose:** Master English grammar through practical exercises and immediate feedback.

**How It Works:**

1. **Topic Selection:**
   Choose a grammar topic:
   - **Articles**: a, an, the
   - **Tenses**: present, past, future, perfect
   - **Prepositions**: in, on, at, by, for
   - **Modal Verbs**: can, should, must, would
   - **Conditionals**: if clauses
   - **Word Order**: sentence structure
   - **Subject-Verb Agreement**
   - And more...

2. **Exercise Format:**

   **Sentence Correction:**
   ```
   Find and correct the error:

   "She don't like coffee."

   [Click on the error]

   Correction: "She doesn't like coffee."

   Explanation: Use "doesn't" (does not) with
   third-person singular (he, she, it).

   Rule: Subject-verb agreement with "do/does"
   ```

   **Multiple Choice:**
   ```
   Complete the sentence:

   "I ___ to Paris last year."

   a) go
   b) went    ✅
   c) gone
   d) going

   Explanation: "Last year" indicates past time,
   so we use past simple "went".
   ```

   **Transformation:**
   ```
   Rewrite in passive voice:

   Active: "The team completed the project."

   Your answer: "The project was completed by the team."

   ✅ Correct!

   Pattern: Subject + was/were + past participle + by + agent
   ```

3. **Difficulty Progression:**
   - **Easy**: Basic rules, common mistakes
   - **Medium**: Complex sentences, exceptions
   - **Hard**: Nuanced usage, advanced structures

4. **Mistake Patterns:**
   The app tracks your errors and identifies patterns:
   ```
   Your Common Mistakes:

   ⚠️ Articles (12 errors)
      - Missing "the" before specific nouns
      - Using "a" instead of "an"

   ⚠️ Prepositions (8 errors)
      - "in" vs "on" for time
      - "at" vs "in" for locations
   ```

**Example Session:**

```
Topic: Present Perfect vs Past Simple
Difficulty: Intermediate
Questions: 10

Question 1:
"I ___ (see) that movie before."

Your answer: have seen  ✅
Correct! Use present perfect for experiences
without a specific time.

Question 2:
"I ___ (see) that movie last week."

Your answer: have seen  ❌
Correction: saw
Explanation: Use past simple with specific past
time ("last week").

[Session continues...]

Results:
- Score: 8/10 (80%)
- Time: 8 minutes
- Accuracy: Good
- Recommendation: Review present perfect time markers
```

**Features:**
- ✅ 50+ grammar topics
- ✅ 1000+ practice questions
- ✅ Immediate feedback with explanations
- ✅ Pattern recognition for common errors
- ✅ Adaptive difficulty
- ✅ Grammar rules reference

**Tips for Success:**
- Focus on one topic at a time
- Read the explanations, not just the answer
- When you make a mistake, do 5 more exercises on that topic
- Use the Mistakes Journal to review errors
- Practice grammar you use incorrectly in conversation

---

#### Module 4: Writing Practice

**Purpose:** Improve writing skills through various prompts with detailed AI feedback.

**How It Works:**

1. **Choose a Prompt Category:**
   - **Personal**: About your life, experiences, opinions
   - **Professional**: Emails, reports, proposals
   - **Academic**: Essays, analyses, arguments
   - **Creative**: Stories, descriptions, imaginative writing

2. **Select a Prompt:**
   ```
   Category: Professional

   Prompts:
   1. Write an email requesting a meeting
   2. Describe a project you completed
   3. Explain why you deserve a promotion
   4. Request feedback from your manager
   5. Propose a new idea to your team
   ```

3. **Write Your Response:**
   - Text editor with word count
   - Suggested length: 150-300 words
   - No time limit - take your time
   - Save draft option

4. **Submit for AI Review:**
   AI analyzes your writing on 4 dimensions:

   **Grammar (0-10):**
   - Sentence structure
   - Verb tenses
   - Agreement
   - Punctuation

   **Vocabulary (0-10):**
   - Word choice appropriateness
   - Variety and sophistication
   - Collocations

   **Clarity (0-10):**
   - Clear expression of ideas
   - Logical flow
   - Paragraph structure

   **Flow (0-10):**
   - Transitions between ideas
   - Cohesion
   - Natural progression

5. **Receive Detailed Feedback:**
   ```
   Your Writing: (Original text shown)

   Scores:
   - Grammar: 8/10 ⭐⭐⭐⭐
   - Vocabulary: 7/10 ⭐⭐⭐
   - Clarity: 9/10 ⭐⭐⭐⭐
   - Flow: 8/10 ⭐⭐⭐⭐

   Overall: 80/100

   Strengths:
   ✅ Clear structure with good paragraphs
   ✅ Professional tone throughout
   ✅ Good use of transitions

   Areas for Improvement:
   ⚠️ Some repetitive vocabulary (3 instances of "very")
   ⚠️ One run-on sentence in paragraph 2

   Corrected Version: (Shows improvements)

   Specific Suggestions:
   1. Replace "very important" with "crucial" or "essential"
   2. Break the long sentence in paragraph 2 into two
   3. Consider using "Moreover" instead of "Also"
   ```

**Example Walkthrough:**

```
Prompt: Write an email to your manager requesting
        a meeting to discuss your career development.

Your Writing:
"Dear Sarah,

I hope this email finds you well. I wanted to reach
out because I would like to discuss my career
development with you. I think it would be very helpful
to get your guidance on my professional growth.

Would you have time for a meeting next week? I am
free on Tuesday or Thursday afternoon. Please let me
know what works best for you.

Thank you for your time and consideration.

Best regards,
[Your Name]"

AI Feedback:
Grammar: 9/10 - Excellent sentence structure
Vocabulary: 7/10 - Clear but could be more specific
Clarity: 10/10 - Very clear request
Flow: 8/10 - Good transitions

Suggestions:
1. "I hope this email finds you well" is formal but
   somewhat clichéd. Consider: "I hope you're doing well"

2. "I wanted to reach out because" can be more direct:
   "I'm writing to request..."

3. "would be very helpful" → "would be valuable"

4. Be more specific about what you want to discuss:
   "discuss potential growth opportunities and next
   steps in my career"

Improved Version: [Shows enhanced version]
```

**Features:**
- ✅ 100+ writing prompts
- ✅ Multiple categories
- ✅ Detailed AI analysis
- ✅ Before/after comparison
- ✅ Progress tracking over time
- ✅ Save and revise drafts

**Tips for Success:**
- Write naturally first, don't self-censor
- Aim for 200-300 words for best feedback
- Read the corrected version carefully
- Implement one suggestion per writing session
- Track improvement by comparing scores over time
- Rewrite the same prompt after a week to see growth

---

#### Module 5: Small Talk Mastery

**Purpose:** Master casual conversation for social situations.

**How It Works:**

1. **Social Situations:**
   - Meeting someone new
   - Coffee shop chitchat
   - Elevator conversation
   - Networking events
   - Waiting in line
   - Casual workplace conversation

2. **Learn Key Skills:**

   **Conversation Starters:**
   ```
   Situation: Meeting a neighbor

   Good openers:
   ✅ "Hi! I don't think we've met. I'm [name]."
   ✅ "Beautiful weather today, isn't it?"
   ✅ "I love your garden! How do you keep it so nice?"

   Avoid:
   ❌ "How much do you make?"
   ❌ "Are you married?"
   ❌ Controversial topics (politics, religion)
   ```

   **Keeping Conversation Going:**
   ```
   Them: "I just got back from vacation."

   Good responses:
   ✅ "Oh, where did you go?" (Open question)
   ✅ "That sounds nice! How was it?" (Show interest)
   ✅ "I love traveling! What was your favorite part?"

   Poor responses:
   ❌ "Okay." (Conversation killer)
   ❌ "I hate traveling." (Negative)
   ❌ [Immediate change of topic]
   ```

   **Polite Endings:**
   ```
   How to end a conversation gracefully:

   ✅ "It was great talking with you! I should get going."
   ✅ "I don't want to take up all your time. Let's
       catch up again soon!"
   ✅ "Nice chatting! Have a great day!"

   Plus:
   - Smile
   - Make brief eye contact
   - Step away gently
   ```

3. **Practice Exercises:**
   ```
   Scenario: Coffee Shop

   A stranger in line says: "This line is taking forever!"

   Your response: [Type here]

   AI evaluates:
   - Is it friendly and appropriate?
   - Does it continue the conversation?
   - Is the tone right?

   Suggestion: "I know, right? But their coffee is
               worth the wait!"
   ```

**Features:**
- ✅ 50+ social scenarios
- ✅ Cultural tips for English-speaking countries
- ✅ Conversation starters database
- ✅ What to say and what NOT to say
- ✅ Practice dialogues
- ✅ Idioms and common expressions

**Tips for Success:**
- Practice with real people (even brief chats)
- Observe native speakers' small talk patterns
- Start with easy topics (weather, food, hobbies)
- Ask open-ended questions (who, what, where, how)
- Show genuine interest in responses

---

#### Module 6: Weekly Challenges

**Purpose:** Fun, gamified challenges to test and improve your skills.

**How It Works:**

1. **New Challenge Every Week:**
   Unlocks Monday at midnight

2. **Challenge Types:**

   **Creative Writing:**
   ```
   Challenge: Write a short story (200 words) that
             includes these 3 words:
             - serendipity
             - umbrella
             - mysterious

   Time limit: 30 minutes
   Points: Up to 100
   ```

   **Debate:**
   ```
   Topic: "Social media does more harm than good"

   Task: Write 3 arguments FOR this statement

   Each argument should be:
   - 2-3 sentences
   - Supported by reasons
   - Clearly expressed

   Points: 30 per argument (max 90) + 10 for clarity
   ```

   **Vocabulary Challenge:**
   ```
   Use each of these 10 advanced words in a sentence:
   - ambiguous
   - contemplate
   - eloquent
   - scrutinize
   - advocate
   [... 5 more]

   Criteria:
   - Correct usage
   - Meaningful context
   - Grammar accuracy
   ```

   **Speed Challenge:**
   ```
   Answer 20 questions in 10 minutes!

   Mix of:
   - Vocabulary
   - Grammar
   - Quick conversation responses

   Bonus: +5 points for each minute under 10
   ```

3. **Scoring & Leaderboard:**
   ```
   Your Score: 87/100 ⭐⭐⭐⭐

   Breakdown:
   - Content: 30/30
   - Grammar: 27/30
   - Creativity: 30/40

   Your Rank: #234 out of 1,847

   Top 3:
   1. user123 - 98/100
   2. english_pro - 96/100
   3. learner_99 - 94/100
   ```

4. **Rewards:**
   - 🏆 Achievement badges
   - ⭐ Streak bonuses
   - 📊 Leaderboard ranking
   - 🎯 Unlock special content

**Features:**
- ✅ New challenge weekly
- ✅ Various challenge types
- ✅ Time-limited competition
- ✅ Leaderboard (optional)
- ✅ Achievement system
- ✅ Progressive difficulty

**Tips for Success:**
- Set a reminder for Monday
- Read instructions carefully
- Use the full time limit
- Proofread before submitting
- Learn from top submissions (shown after completion)

---

### 9. Advanced Features Guide

Now let's explore the powerful Phase 1, 2, and 3 features that make this app truly intelligent.

#### Phase 1 Advanced Features

**A. Contextual Memory System**

**What it does:** Organizes your vocabulary around YOUR life.

**How to use:**

1. **Create Personal Contexts:**
   ```
   Settings → Contexts → Add New Context

   Examples:
   - "My Job - Software Developer"
   - "Cooking & Recipes"
   - "Gym & Fitness"
   - "Family Time"
   ```

2. **Associate Vocabulary:**
   When learning a word, tag it with relevant contexts:
   ```
   Word: "Deadline"
   Contexts: [My Job] [Project Management]

   Your Example: "I have a tight deadline for the new feature."
   ```

3. **Create Context Cards:**
   Rich cards for each word with:
   - Your personal example
   - Usage contexts
   - Common mistakes you make
   - Related words

**Benefits:**
- Remember words better (connected to your life)
- Find words by context when needed
- Review job vocabulary before meetings
- Practice hobby vocabulary before events

**B. Pattern Recognition & Error Correction**

**What it does:** Automatically identifies your recurring mistakes.

**How to use:**

1. **Practice normally** - The system tracks all mistakes

2. **View Pattern Analysis:**
   ```
   Mistakes Journal → Pattern Analysis

   Your Top Patterns:

   ⚠️ Articles (15 times)
      Problem: Missing "the" before specific nouns
      Example: "I went to store" → "I went to the store"
      Strategy: Ask "Is this noun specific?" If yes, use "the"

   ⚠️ Prepositions (12 times)
      Problem: Using "in" instead of "on" for days
      Example: "in Monday" → "on Monday"
      Rule: Use "on" for days, "in" for months/years
   ```

3. **Get Correction Strategies:**
   ```
   For each pattern, you get:
   - Clear explanation of the rule
   - Memory tricks
   - Practice exercises focused on this error
   - Progress tracking
   ```

**Benefits:**
- Stop making the same mistakes repeatedly
- Focus practice on YOUR weak areas
- See measurable improvement
- Build confidence

**C. Smart Practice Recommendations**

**What it does:** AI coach tells you what to practice next.

**How to use:**

1. **Check Daily Recommendations:**
   ```
   Dashboard → Recommendations Panel

   Today's Recommendations:

   🔴 CRITICAL (Do Now):
      Practice: Grammar - Articles
      Why: 15 errors in last 3 days
      Time: 15 minutes
      [Start Practice]

   🟡 HIGH (Today):
      Review: 12 vocabulary words
      Why: Due for spaced repetition
      Time: 10 minutes
      [Start Review]

   🟢 MEDIUM (This Week):
      Focus: Speaking practice
      Why: You're improving fast here!
      Time: 20 minutes
      [Start Session]
   ```

2. **Act on Recommendations:**
   - Click [Start] button for instant practice
   - Dismiss if not relevant
   - See new recommendations after each session

**Benefits:**
- No decision fatigue - always know what to practice
- Optimal learning path
- Balance all skills
- Adapt to your progress

**D. Flexible Streak System**

**What it does:** Maintain streaks even when life gets busy.

**How to use:**

1. **Build Your Streak:**
   - Practice daily to increase streak
   - Streak shown in top bar: 🔥 7 days

2. **Use Freeze Days:**
   ```
   Missed a day? Don't panic!

   You have 2 freeze days per month.

   To use:
   1. App detects you missed a day
   2. Automatically uses a freeze day
   3. Your streak continues!

   Current month:
   Freeze days: 1 remaining
   Reset: in 12 days
   ```

3. **Rules:**
   - 2 freeze days per month
   - Auto-reset on 1st of each month
   - Can only freeze 1 missed day (not multiple in a row)
   - Shows warning when you've used both

**Benefits:**
- Maintain motivation
- Build sustainable habits
- No guilt from occasional miss
- Realistic approach to learning

**E. Micro-Learning Features**

**What it does:** Quick lessons for busy moments.

**How to use:**

1. **3-Minute Power Lessons:**
   ```
   Dashboard → Quick Practice → Power Lesson

   Choose focus:
   - Word of the Day
   - Synonym Challenge
   - Grammar Quick Fix
   - Quick Response Practice
   - Sentence Builder

   [Generates a complete mini-lesson in 3 minutes]
   ```

2. **Voice Journal:**
   ```
   Quick Practice → Voice Journal

   Today's Prompt:
   "Describe your morning routine"

   [🎤 Record for 1-2 minutes]

   Gets feedback on:
   - Fluency
   - Vocabulary used
   - Grammar (from transcription)
   ```

3. **Waiting Room Practice:**
   ```
   Super quick exercises (1-2 minutes):
   - Spot the error in a sentence
   - Choose the right word
   - Quick translation (think in English)
   - Memory recall (vocabulary flashcard)
   ```

**Benefits:**
- Practice anywhere, anytime
- No excuse to skip when busy
- Build consistency
- Accumulates to significant progress

---

#### Phase 2 & 3 Advanced Features

For detailed documentation on all 10 advanced services, see [PHASE2-3-FEATURES.md](./PHASE2-3-FEATURES.md).

Here are quick guides for the most popular features:

**Active Listening & Shadowing**

**Quick Start:**
1. Go to Advanced Features → Active Listening
2. Choose difficulty (beginner/intermediate/advanced)
3. Listen to the audio clip
4. Pause and repeat out loud
5. Record yourself
6. Get analysis on pace, clarity, pronunciation

**Best for:** Improving pronunciation and speaking rhythm

---

**Personalized Learning Paths**

**Quick Start:**
1. Go to Learning Paths
2. Choose your goal:
   - Job Interview Prep
   - IELTS/TOEFL
   - Business English
   - Travel English
   - Casual Conversation
3. Set time commitment (hours per week)
4. Get customized weekly plan
5. Track progress week by week

**Best for:** Structured learning with a specific goal

---

**Immersion Simulation**

**Quick Start:**
1. Go to Immersion → Daily Scenarios
2. Pick a situation (grocery shopping, doctor visit, etc.)
3. Go through multi-turn conversation
4. Handle realistic challenges
5. Get scored on performance

**Best for:** Preparing for real-world situations

---

**Meta-Learning Skills**

**Quick Start:**
1. Go to Meta-Learning → Learning Strategies
2. Read about effective techniques:
   - Spaced Repetition
   - Active Recall
   - Pomodoro Method
3. Take weekly reflection
4. Track study habits
5. Optimize your learning process

**Best for:** Learning how to learn more effectively

---

### 10. Daily Practice Workflows

Here are recommended daily routines for different time commitments:

#### 10-Minute Daily Routine (Minimum)

**Morning (5 minutes):**
```
1. Check recommendations (1 min)
2. Do a micro-lesson (3 min)
3. Review 5 vocabulary words (1 min)
```

**Evening (5 minutes):**
```
1. One quick conversation practice (3 min)
2. Daily reflection - what did I learn? (2 min)
```

**Weekly result:** 70 minutes = Significant progress

---

#### 30-Minute Daily Routine (Recommended)

**Session Structure:**
```
1. Warm-up (5 min):
   - Review yesterday's vocabulary
   - Check recommendations

2. Main Practice (20 min):
   - Day 1: Conversation Practice
   - Day 2: Writing Task
   - Day 3: Grammar Focus
   - Day 4: Vocabulary Building
   - Day 5: Conversation Practice
   - Day 6: Small Talk + Shadowing
   - Day 7: Weekly Challenge

3. Cool-down (5 min):
   - Review any mistakes
   - Note 2-3 key learnings
   - Set tomorrow's focus
```

**Weekly result:** 3.5 hours = Excellent progress

---

#### 60-Minute Daily Routine (Intensive)

**Comprehensive Session:**
```
1. Check-in (5 min):
   - Review analytics (velocity, retention)
   - Check recommendations
   - Set session goals

2. Skills Practice (40 min):
   - Skill 1 (15 min): Main focus
   - Skill 2 (15 min): Secondary focus
   - Skill 3 (10 min): Weak area practice

3. Advanced Features (10 min):
   - Shadowing exercise
   - OR Immersion scenario
   - OR Debate practice

4. Review & Reflect (5 min):
   - Log mistakes
   - Update progress
   - Weekly reflection (on Sundays)
```

**Weekly result:** 7 hours = Rapid improvement

---

## Part 3: Technical Details

### 11. Architecture Overview

#### High-Level Architecture

```
┌─────────────────────────────────────────┐
│           React Frontend (Vite)          │
│  ┌─────────────────────────────────┐   │
│  │   Components (UI)                │   │
│  │  - Dashboard                     │   │
│  │  - Learning Modules              │   │
│  │  - Advanced Features             │   │
│  └─────────────────────────────────┘   │
│              ↕                           │
│  ┌─────────────────────────────────┐   │
│  │   State Management (Zustand)     │   │
│  │  - User Profile                  │   │
│  │  - Learning Progress             │   │
│  │  - Settings                      │   │
│  └─────────────────────────────────┘   │
│              ↕                           │
│  ┌─────────────────────────────────┐   │
│  │   Services Layer                 │   │
│  │  - AI Service                    │   │
│  │  - Database Service              │   │
│  │  - Advanced Services (10)        │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
              ↕                ↕
    ┌─────────────┐   ┌────────────────┐
    │  AI Backend  │   │ Local Storage  │
    │ (Claude/Ollama)│   │ (localStorage/ │
    │              │   │  SQLite)       │
    └─────────────┘   └────────────────┘
```

#### Component Structure

```
src/
├── components/
│   ├── Assessment/          # Baseline assessment
│   │   └── Assessment.jsx
│   ├── Common/             # Shared components
│   │   ├── Navigation.jsx
│   │   └── Settings.jsx
│   ├── Dashboard/          # Main dashboard
│   │   └── Dashboard.jsx
│   ├── Learning/           # Core modules
│   │   ├── ConversationPractice.jsx
│   │   ├── VocabularyPractice.jsx
│   │   ├── GrammarPractice.jsx
│   │   ├── WritingPractice.jsx
│   │   ├── SmallTalkPractice.jsx
│   │   └── WeeklyChallenge.jsx
│   └── Review/             # Review features
│       ├── Review.jsx
│       └── MistakesJournal.jsx
│
├── services/               # Business logic
│   ├── aiService.js       # AI integration
│   ├── database.js        # Data persistence
│   ├── patternRecognition.js
│   ├── recommendationEngine.js
│   ├── contextualMemory.js
│   ├── microLearning.js
│   ├── motivationTracker.js
│   ├── activeListening.js
│   ├── enhancedVocabulary.js
│   ├── speakingConfidence.js
│   ├── advancedAnalytics.js
│   ├── practicalTools.js
│   ├── socialLearning.js
│   ├── immersionSimulation.js
│   ├── advancedConversation.js
│   ├── learningPaths.js
│   └── metaLearning.js
│
├── stores/                # State management
│   └── appStore.js       # Zustand store
│
├── styles/               # Global styles
│   └── global.css
│
├── App.jsx              # Main app component
└── main.jsx            # Entry point
```

#### Data Flow

**1. User Interaction:**
```
User clicks button
    ↓
Component handler
    ↓
Update Zustand store
    ↓
Re-render affected components
```

**2. AI Interaction:**
```
User submits response
    ↓
Component calls aiService
    ↓
aiService sends to Claude/Ollama
    ↓
Receives AI evaluation
    ↓
Store in database
    ↓
Update UI with feedback
```

**3. Data Persistence:**
```
Action (exercise complete, mistake logged, etc.)
    ↓
Call database service
    ↓
Database checks environment:
    - Browser: Save to localStorage
    - Node: Save to SQLite
    ↓
Return confirmation
    ↓
Update UI state
```

---

### 12. Data Storage & Management

#### Storage Architecture

**Browser Environment (Default):**
```javascript
localStorage structure:

{
  "user_profile": {
    "id": 1,
    "name": "John Doe",
    "proficiency_score": 68,
    "created_at": "2025-01-15T10:30:00Z"
  },

  "learning_progress": [
    {
      "skill_type": "vocabulary",
      "score": 70,
      "last_practiced": "2025-01-20T14:22:00Z"
    },
    // ... more skills
  ],

  "exercise_history": [
    {
      "exercise_type": "conversation",
      "score": 85,
      "completed_at": "2025-01-20T14:00:00Z"
    },
    // ... more exercises
  ],

  "vocabulary": [
    {
      "word": "ambitious",
      "mastery_level": 75,
      "next_review": "2025-01-23"
    },
    // ... more words
  ]
}
```

**Node.js Environment (Optional):**
```sql
-- SQLite Database Structure

CREATE TABLE user_profile (
  id INTEGER PRIMARY KEY,
  name TEXT,
  proficiency_score INTEGER,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE learning_progress (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  skill_type TEXT,
  score INTEGER,
  last_practiced DATETIME,
  FOREIGN KEY (user_id) REFERENCES user_profile(id)
);

-- ... more tables
```

#### Data Operations

**Saving Data:**
```javascript
// Example: Save exercise result
import database from './services/database.js';

const result = {
  exerciseType: 'conversation',
  score: 85,
  duration: 15,
  details: { /* ... */ }
};

await database.saveExerciseHistory(result);
```

**Retrieving Data:**
```javascript
// Get user profile
const profile = await database.getUserProfile();

// Get learning progress
const progress = await database.getLearningProgress();

// Get vocabulary list
const vocab = await database.getUserVocabulary();
```

**Updating Data:**
```javascript
// Update proficiency score
await database.updateUserProfile({
  proficiency_score: 75
});

// Update vocabulary mastery
await database.updateVocabularyMastery('ambitious', 80);
```

#### Data Export/Import

**Export All Data:**
```javascript
const exportData = {
  profile: await database.getUserProfile(),
  progress: await database.getLearningProgress(),
  vocabulary: await database.getUserVocabulary(),
  exerciseHistory: await database.getExerciseHistory(),
  mistakes: await database.getAllMistakes(),
  // ... all data
};

const json = JSON.stringify(exportData, null, 2);
// Download as file
```

**Import Data:**
```javascript
// Read imported JSON
const importedData = JSON.parse(jsonString);

// Restore each data type
await database.importUserProfile(importedData.profile);
await database.importLearningProgress(importedData.progress);
// ... restore all data
```

#### Storage Limits

**localStorage (Browser):**
- Limit: ~5-10 MB per domain
- Our usage: ~2-5 MB typical
- Recommendation: Export data monthly

**SQLite (Node.js):**
- Limit: Effectively unlimited
- Our usage: 10-50 MB typical
- Recommendation: Backup database file regularly

---

### 13. AI Integration

#### Supported AI Backends

**1. Claude API (Anthropic)**

**Setup:**
```javascript
// In .env file
VITE_ANTHROPIC_API_KEY=sk-ant-your-key-here

// Or in Settings UI
Settings → Anthropic API Key → [Paste key] → Save
```

**Usage:**
```javascript
import aiService from './services/aiService.js';

const response = await aiService.chat([
  {
    role: 'user',
    content: 'Evaluate this sentence: "She go to work every day."'
  }
]);

// Response includes evaluation and corrections
```

**Models Used:**
- Default: `claude-3-sonnet-20240229`
- Advanced: `claude-3-opus-20240229` (optional)

**Pricing:**
- Sonnet: $3 per million input tokens, $15 per million output tokens
- Typical exercise evaluation: ~500 tokens (~$0.01)
- Heavy user (100 exercises/month): ~$1-2/month

**2. Ollama (Local)**

**Setup:**
```bash
# Install Ollama
# Visit ollama.ai and download

# Pull a model
ollama pull llama3

# Start service
ollama serve

# Configure in app
Settings → Use Local Model → ON
```

**Usage:**
```javascript
// Same interface as Claude
const response = await aiService.chat([
  {
    role: 'user',
    content: 'Evaluate this sentence: "She go to work every day."'
  }
]);
```

**Supported Models:**
- llama3 (8B, 70B)
- mistral (7B)
- mixtral (8x7B)
- codellama (various sizes)

**Performance:**
- 8B models: Fast on modern CPUs
- 70B models: Require GPU (NVIDIA recommended)
- Quality: Good for most exercises, excellent with 70B

#### AI Service Interface

**Core Methods:**

```javascript
// 1. Chat (general purpose)
await aiService.chat(messages, options);

// 2. Evaluate baseline assessment
await aiService.evaluateBaselineAssessment(responses);

// 3. Evaluate conversation
await aiService.evaluateConversationResponse(
  scenario,
  userResponse,
  context
);

// 4. Evaluate writing
await aiService.evaluateWriting(text, promptCategory);

// 5. Generate vocabulary exercise
await aiService.generateVocabularyExercise(level, context);

// 6. Generate grammar exercise
await aiService.generateGrammarExercise(topic, level);

// 7. Generate weekly challenge
await aiService.generateWeeklyChallenge(type, difficulty);
```

**Error Handling:**

```javascript
try {
  const response = await aiService.chat(messages);
  // Use response
} catch (error) {
  if (error.message.includes('API key')) {
    // Prompt user to add API key
  } else if (error.message.includes('rate limit')) {
    // Show rate limit message
  } else {
    // Use fallback response
    const fallback = aiService.getFallbackResponse();
  }
}
```

**Fallback System:**

When AI is unavailable, the app provides default responses:

```javascript
// Default evaluation response
{
  score: 70,
  feedback: "Good effort! Keep practicing.",
  suggestions: [
    "Pay attention to verb forms",
    "Try to use more varied vocabulary"
  ],
  corrected: "[Generic correction]"
}
```

---

### 14. Services Documentation

#### Core Services

**aiService.js**

Purpose: Handle all AI interactions

```javascript
import aiService from './services/aiService.js';

// Configure
aiService.setApiKey('sk-ant-...');
aiService.setProvider('claude'); // or 'ollama'
aiService.setModel('llama3'); // for Ollama

// Use
const result = await aiService.chat([
  { role: 'user', content: 'Hello' }
]);
```

**database.js**

Purpose: Data persistence abstraction

```javascript
import database from './services/database.js';

// User profile
const profile = await database.getUserProfile();
await database.updateUserProfile({ name: 'John' });

// Learning progress
const progress = await database.getLearningProgress();
await database.updateSkillScore('vocabulary', 75);

// Exercise history
await database.saveExerciseHistory({
  type: 'conversation',
  score: 85
});

// Vocabulary
await database.addVocabulary('ambitious', 'definition');
await database.updateVocabularyMastery('ambitious', 80);

// Mistakes
await database.addMistake({
  original: 'She go',
  corrected: 'She goes',
  explanation: 'Third person singular'
});
```

#### Advanced Services (Phase 1)

**patternRecognition.js**

```javascript
import patternRecognition from './services/patternRecognition.js';

// Analyze a mistake
const analysis = patternRecognition.analyzeMistake(
  'She go to work',
  'She goes to work',
  'Third person singular verb agreement'
);
// Returns: { category, severity, pattern, ... }

// Aggregate patterns
const patterns = patternRecognition.aggregatePatterns(mistakes);

// Identify recurring patterns
const recurring = patternRecognition.identifyRecurringPatterns(
  patterns,
  5 // threshold
);

// Generate correction strategy
const strategy = patternRecognition.generateCorrectionStrategy(pattern);
```

**recommendationEngine.js**

```javascript
import recommendationEngine from './services/recommendationEngine.js';

// Generate recommendations
const recommendations = recommendationEngine.generateRecommendations({
  userProfile,
  learningProgress,
  exerciseHistory,
  vocabularyMastery,
  mistakes
});

// Returns array of recommendations:
[
  {
    id: 'rec_123',
    type: 'practice_focus',
    priority: 5, // CRITICAL
    title: 'Practice Grammar - Articles',
    description: 'You\'ve made 15 article errors',
    action: { type: 'grammar', topic: 'articles' },
    estimatedTime: 15
  },
  // ... more recommendations
]
```

**contextualMemory.js**

```javascript
import contextualMemory from './services/contextualMemory.js';

// Create personal context
await contextualMemory.createContext(
  'My Job - Developer',
  'work',
  'Software development terms',
  '#3498db',
  'code'
);

// Associate vocabulary
await contextualMemory.associateVocabularyWithContext(
  vocabularyId,
  contextId,
  8 // relevance score
);

// Create context card
await contextualMemory.createContextCard(
  vocabularyId,
  'I have a tight deadline for the feature.',
  ['work', 'projects'],
  ['Missing "the" before "feature"'],
  ['timeline', 'schedule', 'due date']
);

// Get word relationships
const relationships = await contextualMemory.buildWordRelationshipMap('happy');
// Returns: { synonyms, antonyms, related, wordFamily }
```

**microLearning.js**

```javascript
import microLearning from './services/microLearning.js';

// Generate 3-minute lesson
const lesson = await microLearning.generateMicroLesson(
  'vocabulary',
  'intermediate',
  aiService
);

// Get quick exercises
const exercises = microLearning.getQuickPracticeExercises();

// Generate voice journal prompt
const prompt = microLearning.generateVoiceJournalPrompt();

// Waiting room practice
const quickEx = microLearning.generateWaitingRoomPractice();
```

**motivationTracker.js**

```javascript
import motivationTracker from './services/motivationTracker.js';

// Update streak
const streak = await motivationTracker.updateFlexibleStreak(userId);
// Returns: { currentStreak, freezeDaysUsed, freezeDaysRemaining }

// Add daily win
await motivationTracker.addDailyWin(
  'Completed 20 minutes of conversation practice',
  'practice',
  8 // emotional value 1-10
);

// Check achievements
const newAchievements = await motivationTracker.checkAchievements(userData);

// Get milestone progress
const milestones = await motivationTracker.getMilestoneProgress(userData);

// Generate progress story
const story = await motivationTracker.generateProgressStory(userData, 30);
// Compares now vs 30 days ago
```

#### Advanced Services (Phase 2 & 3)

For complete documentation on all 10 Phase 2 & 3 services, see [PHASE2-3-FEATURES.md](./PHASE2-3-FEATURES.md).

Quick reference:

```javascript
// Active Listening
import activeListening from './services/activeListening.js';
const exercise = activeListening.generateShadowingExercise('intermediate', 120);

// Enhanced Vocabulary
import enhancedVocabulary from './services/enhancedVocabulary.js';
const map = enhancedVocabulary.buildWordRelationshipMap('happy');

// Speaking Confidence
import speakingConfidence from './services/speakingConfidence.js';
const exercise = speakingConfidence.generateFillerReductionExercise();

// Advanced Analytics
import advancedAnalytics from './services/advancedAnalytics.js';
const velocity = advancedAnalytics.calculateLearningVelocity(history, 30);

// Practical Tools
import practicalTools from './services/practicalTools.js';
const lookup = practicalTools.quickLookup('restaurant', 'ordering');

// Social Learning
import socialLearning from './services/socialLearning.js';
const debate = socialLearning.generateDebateExercise('technology');

// Immersion Simulation
import immersionSimulation from './services/immersionSimulation.js';
const scenario = immersionSimulation.generateDailyLifeScenario('airport');

// Advanced Conversation
import advancedConversation from './services/advancedConversation.js';
const story = advancedConversation.generateStorytellingExercise('star_method');

// Learning Paths
import learningPaths from './services/learningPaths.js';
const path = learningPaths.generatePersonalizedPath('job_interview_prep');

// Meta-Learning
import metaLearning from './services/metaLearning.js';
const reflection = metaLearning.generateWeeklyReflection();
```

---

### 15. State Management

The app uses Zustand for state management.

**Store Structure:**

```javascript
// src/stores/appStore.js

const useAppStore = create((set) => ({
  // User state
  user: null,
  setUser: (user) => set({ user }),

  // Settings
  settings: {
    apiKey: '',
    useLocalModel: false,
    modelName: 'llama3',
    theme: 'light'
  },
  updateSettings: (newSettings) => set((state) => ({
    settings: { ...state.settings, ...newSettings }
  })),

  // Learning state
  proficiencyScore: 0,
  setProficiencyScore: (score) => set({ proficiencyScore: score }),

  learningProgress: [],
  setLearningProgress: (progress) => set({ learningProgress: progress }),

  // UI state
  isLoading: false,
  setLoading: (loading) => set({ isLoading: loading }),

  currentModule: null,
  setCurrentModule: (module) => set({ currentModule: module }),

  // Notifications
  notifications: [],
  addNotification: (notification) => set((state) => ({
    notifications: [...state.notifications, notification]
  })),
  clearNotification: (id) => set((state) => ({
    notifications: state.notifications.filter(n => n.id !== id)
  }))
}));

export default useAppStore;
```

**Using the Store:**

```javascript
import useAppStore from './stores/appStore';

function Dashboard() {
  // Subscribe to state
  const user = useAppStore((state) => state.user);
  const proficiencyScore = useAppStore((state) => state.proficiencyScore);
  const setLoading = useAppStore((state) => state.setLoading);

  // Use in component
  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    const profile = await database.getUserProfile();
    useAppStore.setState({ user: profile });
    setLoading(false);
  }

  return (
    <div>
      <h1>Welcome, {user?.name}!</h1>
      <p>Score: {proficiencyScore}</p>
    </div>
  );
}
```

---

## Part 4: Deployment

### 16. Local Development

**Standard Development Server:**

```bash
# Start development server
npm run dev

# Features:
# - Hot module replacement (HMR)
# - Fast refresh
# - Source maps
# - Auto-open browser

# Access at: http://localhost:3000
```

**Development with Custom Port:**

```javascript
// vite.config.js
export default defineConfig({
  server: {
    port: 3001,
    host: true, // Expose to network
    open: true  // Auto-open browser
  }
})
```

**Development with HTTPS:**

```bash
# Install mkcert
npm install -g mkcert

# Create certificate
mkcert create-ca
mkcert create-cert

# Update vite.config.js
export default defineConfig({
  server: {
    https: {
      key: './cert-key.pem',
      cert: './cert.pem'
    }
  }
})

# Access at: https://localhost:3000
```

**Why HTTPS?**
- Required for Web Speech API
- Secure API key transmission
- Test PWA features

---

### 17. Production Build

**Create Production Build:**

```bash
# Build for production
npm run build

# Output:
# dist/
# ├── index.html
# ├── assets/
# │   ├── index-[hash].js  (minified, optimized)
# │   └── index-[hash].css
# └── ... (other assets)
```

**Preview Production Build:**

```bash
# Test production build locally
npm run preview

# Access at: http://localhost:4173
```

**Build Configuration:**

```javascript
// vite.config.js
export default defineConfig({
  build: {
    outDir: 'dist',
    sourcemap: false, // Don't generate source maps for production
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          charts: ['recharts'],
          store: ['zustand']
        }
      }
    }
  }
})
```

**Optimizations Applied:**
- ✅ Code minification
- ✅ Tree shaking (removes unused code)
- ✅ Code splitting (lazy loading)
- ✅ Asset optimization (images, fonts)
- ✅ CSS extraction and minification
- ✅ Compression ready

**Build Size:**
- Typical build: 800KB - 1.2MB (gzipped)
- Vendor chunk: ~400KB
- App chunk: ~300-500KB
- Charts: ~100KB

---

### 18. Deployment Options

#### Option 1: Vercel (Recommended - Easiest)

**Step 1: Install Vercel CLI**
```bash
npm install -g vercel
```

**Step 2: Deploy**
```bash
# From project directory
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? ai-english-learning-app
# - Directory? ./
# - Override settings? No

# Vercel automatically:
# - Detects Vite
# - Runs npm run build
# - Deploys to production
# - Gives you a URL
```

**Step 3: Configure Environment Variables**
```bash
# Add API key
vercel env add VITE_ANTHROPIC_API_KEY

# Or via dashboard:
# 1. Go to vercel.com/dashboard
# 2. Select your project
# 3. Settings → Environment Variables
# 4. Add VITE_ANTHROPIC_API_KEY
```

**Step 4: Custom Domain (Optional)**
```bash
# Add custom domain
vercel domains add yourdomain.com

# Vercel provides DNS instructions
```

**Features:**
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Automatic deployments (Git push)
- ✅ Preview deployments (PRs)
- ✅ Free tier available

---

#### Option 2: Netlify

**Step 1: Install Netlify CLI**
```bash
npm install -g netlify-cli
```

**Step 2: Build**
```bash
npm run build
```

**Step 3: Deploy**
```bash
# Login
netlify login

# Deploy
netlify deploy --prod

# Choose:
# - Create new site
# - Publish directory: dist

# Get deployment URL
```

**Or via Git:**
```bash
# Connect Git repository
# Netlify auto-deploys on push

# Build settings:
# - Build command: npm run build
# - Publish directory: dist
```

**Step 4: Environment Variables**
```bash
# Via CLI
netlify env:set VITE_ANTHROPIC_API_KEY sk-ant-your-key

# Or via dashboard:
# Site settings → Environment variables
```

**Features:**
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Form handling
- ✅ Serverless functions
- ✅ Free tier available

---

#### Option 3: GitHub Pages

**Step 1: Configure vite.config.js**
```javascript
export default defineConfig({
  base: '/ai-english-learning-app/', // Your repo name
  // ... other config
})
```

**Step 2: Build**
```bash
npm run build
```

**Step 3: Deploy Script**

Create `deploy.sh`:
```bash
#!/usr/bin/env sh

# Build
npm run build

# Navigate to build output
cd dist

# Initialize git (if needed)
git init
git add -A
git commit -m 'deploy'

# Deploy
git push -f git@github.com:username/ai-english-learning-app.git main:gh-pages

cd -
```

**Step 4: Enable GitHub Pages**
- Go to repository settings
- Pages → Source → gh-pages branch
- Save

**Access at:** `https://username.github.io/ai-english-learning-app/`

**Limitations:**
- ⚠️ No environment variables (API key in code)
- ⚠️ No serverless functions
- ⚠️ Static only

**Recommendation:** Use for demo only, not for production with API keys

---

#### Option 4: Self-Hosted (VPS/Server)

**Requirements:**
- Linux server (Ubuntu 20.04+ recommended)
- Nginx or Apache
- Node.js installed (for build)
- Domain name (optional)

**Step 1: Prepare Server**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Nginx
sudo apt install nginx -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y
```

**Step 2: Build Application**
```bash
# On your local machine
npm run build

# Copy to server
scp -r dist/* user@your-server:/var/www/english-app/
```

**Step 3: Configure Nginx**
```nginx
# /etc/nginx/sites-available/english-app

server {
    listen 80;
    server_name your-domain.com;

    root /var/www/english-app;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Enable gzip compression
    gzip on;
    gzip_types text/css application/javascript application/json;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Step 4: Enable Site**
```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/english-app /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

**Step 5: SSL with Let's Encrypt**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (already set up by Certbot)
```

**Features:**
- ✅ Full control
- ✅ No vendor lock-in
- ✅ Can customize server
- ❌ Manual updates required
- ❌ More complex setup

---

#### Option 5: Docker Container

**Dockerfile:**
```dockerfile
# Build stage
FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy build
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**nginx.conf:**
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

**Build and Run:**
```bash
# Build image
docker build -t english-learning-app .

# Run container
docker run -d -p 8080:80 --name english-app english-learning-app

# Access at: http://localhost:8080
```

**Docker Compose:**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:80"
    environment:
      - VITE_ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    restart: unless-stopped
```

**Run with Compose:**
```bash
# Create .env file
echo "ANTHROPIC_API_KEY=sk-ant-your-key" > .env

# Start
docker-compose up -d

# Stop
docker-compose down
```

---

### 19. Environment Variables

**Available Variables:**

```env
# .env file (in project root)

# AI Configuration
VITE_ANTHROPIC_API_KEY=sk-ant-your-key-here
VITE_DEFAULT_AI_PROVIDER=claude          # 'claude' or 'ollama'
VITE_DEFAULT_MODEL=llama3                # For Ollama

# Ollama Configuration
VITE_OLLAMA_BASE_URL=http://localhost:11434

# App Configuration
VITE_APP_NAME="AI English Learning"
VITE_APP_VERSION=2.0.0

# Feature Flags
VITE_ENABLE_SPEECH_RECOGNITION=true
VITE_ENABLE_ADVANCED_FEATURES=true
VITE_ENABLE_ANALYTICS=false

# Database (for Node.js environment)
DATABASE_PATH=./database/learning.db

# Deployment
VITE_BASE_URL=/                          # For GitHub Pages: /repo-name/
```

**Using Environment Variables:**

```javascript
// In code
const apiKey = import.meta.env.VITE_ANTHROPIC_API_KEY;
const provider = import.meta.env.VITE_DEFAULT_AI_PROVIDER;

// Check if variable exists
if (!import.meta.env.VITE_ANTHROPIC_API_KEY) {
  console.warn('API key not configured');
}
```

**Best Practices:**

1. **Never commit .env to Git:**
```gitignore
# .gitignore
.env
.env.local
.env.production
```

2. **Provide .env.example:**
```env
# .env.example
VITE_ANTHROPIC_API_KEY=your_key_here
VITE_DEFAULT_AI_PROVIDER=claude
VITE_DEFAULT_MODEL=llama3
```

3. **Use different files for different environments:**
- `.env.local` - Local development (ignored by Git)
- `.env.development` - Development build
- `.env.production` - Production build

4. **In deployment platforms:**
- Vercel: Dashboard → Environment Variables
- Netlify: Site settings → Environment
- GitHub Actions: Repository → Secrets

---

### 20. Security Considerations

#### API Key Security

**❌ DON'T:**
```javascript
// DON'T hardcode API keys
const apiKey = 'sk-ant-1234567890';

// DON'T commit .env files
// Make sure .env is in .gitignore
```

**✅ DO:**
```javascript
// Use environment variables
const apiKey = import.meta.env.VITE_ANTHROPIC_API_KEY;

// Validate before use
if (!apiKey) {
  throw new Error('API key not configured');
}

// Store in localStorage only if user enters it
localStorage.setItem('apiKey', userProvidedKey);
```

**Best Practice:**
- User enters API key in Settings
- Stored encrypted in localStorage
- Never exposed in client-side code
- Consider backend proxy for production

#### Data Privacy

**User Data Storage:**
```javascript
// All data is local
// - localStorage (browser)
// - SQLite (Node.js)
// No external database
// No tracking/analytics by default
```

**Data Export:**
```javascript
// Allow users to export their data
const exportAllData = () => {
  const data = {
    profile: localStorage.getItem('user_profile'),
    progress: localStorage.getItem('learning_progress'),
    // ... all data
  };
  return JSON.stringify(data);
};
```

**Data Deletion:**
```javascript
// Allow complete data deletion
const deleteAllData = () => {
  localStorage.clear();
  // Or delete specific keys
  const keys = [
    'user_profile',
    'learning_progress',
    // ... all keys
  ];
  keys.forEach(key => localStorage.removeItem(key));
};
```

#### Input Validation

**Validate User Input:**
```javascript
// Example: Validate conversation response
const validateResponse = (text) => {
  // Check length
  if (text.length < 3) {
    return { valid: false, error: 'Response too short' };
  }

  if (text.length > 500) {
    return { valid: false, error: 'Response too long' };
  }

  // Check for malicious content (basic)
  if (text.includes('<script>')) {
    return { valid: false, error: 'Invalid characters' };
  }

  return { valid: true };
};
```

#### XSS Prevention

**Sanitize Display:**
```javascript
import DOMPurify from 'dompurify';

// When displaying user-generated content
const sanitized = DOMPurify.sanitize(userContent);

// In React
<div dangerouslySetInnerHTML={{ __html: sanitized }} />

// Or use text nodes (automatic escaping)
<div>{userContent}</div>
```

#### HTTPS Enforcement

**For Production:**
```nginx
# Nginx - Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # ... rest of config
}
```

#### Rate Limiting

**Protect AI API:**
```javascript
class RateLimiter {
  constructor(maxRequests, timeWindow) {
    this.maxRequests = maxRequests;
    this.timeWindow = timeWindow;
    this.requests = [];
  }

  canMakeRequest() {
    const now = Date.now();
    // Remove old requests
    this.requests = this.requests.filter(
      time => now - time < this.timeWindow
    );

    if (this.requests.length < this.maxRequests) {
      this.requests.push(now);
      return true;
    }

    return false;
  }
}

// Usage
const limiter = new RateLimiter(10, 60000); // 10 requests per minute

if (limiter.canMakeRequest()) {
  // Make AI request
} else {
  // Show error: "Too many requests. Please wait."
}
```

---

## Part 5: Advanced Topics

### 21. Customization Guide

#### Changing Colors/Theme

**Global CSS Variables:**

```css
/* src/styles/global.css */

:root {
  /* Primary Colors */
  --color-primary: #3498db;      /* Change to your brand color */
  --color-primary-dark: #2980b9;
  --color-primary-light: #5dade2;

  /* Secondary Colors */
  --color-secondary: #2ecc71;
  --color-accent: #e74c3c;

  /* Neutral Colors */
  --color-background: #ffffff;
  --color-surface: #f8f9fa;
  --color-text: #2c3e50;
  --color-text-secondary: #7f8c8d;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Typography */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;

  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
```

**Dark Mode:**

```css
/* Add dark mode support */
[data-theme='dark'] {
  --color-background: #1a1a1a;
  --color-surface: #2d2d2d;
  --color-text: #f8f9fa;
  --color-text-secondary: #adb5bd;
  --color-primary: #5dade2;
}
```

```javascript
// Toggle dark mode
const toggleDarkMode = () => {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
};

// Load saved preference
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
```

#### Adding Custom Scenarios

**Add Conversation Scenario:**

```javascript
// src/data/scenarios.js

export const customScenarios = [
  {
    id: 'custom_1',
    title: 'Booking a Flight',
    category: 'travel',
    difficulty: 'intermediate',
    description: 'Call an airline to book a flight',
    initialMessage: 'Good afternoon, Airline customer service. How can I help you today?',
    context: {
      situation: 'You need to book a round-trip flight',
      yourRole: 'Customer',
      theirRole: 'Airline representative'
    },
    objectives: [
      'State your destination',
      'Provide travel dates',
      'Ask about prices',
      'Complete booking'
    ],
    vocabulary: ['departure', 'arrival', 'round-trip', 'layover', 'confirmation number']
  },
  // Add more scenarios...
];

// Import in ConversationPractice component
import { customScenarios } from '../data/scenarios';
```

#### Adding Custom Vocabulary Lists

```javascript
// src/data/vocabulary.js

export const customVocabularyLists = {
  'medical_terminology': [
    {
      word: 'prescription',
      definition: 'A doctor\'s written order for medicine',
      example: 'The doctor gave me a prescription for antibiotics.',
      difficulty: 'intermediate',
      category: 'healthcare'
    },
    {
      word: 'symptoms',
      definition: 'Physical signs of illness',
      example: 'What symptoms are you experiencing?',
      difficulty: 'beginner',
      category: 'healthcare'
    },
    // Add more words...
  ],

  'cooking_terms': [
    // ... cooking vocabulary
  ]
};

// Add to database on first load
import database from './services/database';
import { customVocabularyLists } from './data/vocabulary';

const initializeCustomVocabulary = async () => {
  for (const [listName, words] of Object.entries(customVocabularyLists)) {
    for (const word of words) {
      await database.addVocabulary(
        word.word,
        word.definition,
        word.example,
        word.difficulty
      );
    }
  }
};
```

#### Custom Prompts for Writing

```javascript
// src/data/writingPrompts.js

export const customWritingPrompts = {
  'technical_writing': [
    {
      id: 'tech_1',
      prompt: 'Explain how to use a smartphone to someone who has never used one',
      category: 'technical',
      difficulty: 'intermediate',
      suggestedLength: 200,
      tips: [
        'Use simple, clear language',
        'Break into steps',
        'Avoid jargon'
      ]
    },
    // More prompts...
  ],

  'business_email': [
    {
      id: 'biz_1',
      prompt: 'Write an email apologizing for a delayed project delivery',
      category: 'business',
      difficulty: 'advanced',
      suggestedLength: 150,
      tips: [
        'Be professional and courteous',
        'Explain the reason briefly',
        'Offer a solution',
        'Set new timeline'
      ]
    },
    // More prompts...
  ]
};
```

---

### 22. Extending Features

#### Adding a New Learning Module

**Step 1: Create Component**

```javascript
// src/components/Learning/PronunciationPractice.jsx

import { useState } from 'react';
import './PronunciationPractice.css';

function PronunciationPractice() {
  const [currentWord, setCurrentWord] = useState('');
  const [isRecording, setIsRecording] = useState(false);

  // Your module logic here

  return (
    <div className="pronunciation-practice">
      <h1>Pronunciation Practice</h1>
      {/* Your UI here */}
    </div>
  );
}

export default PronunciationPractice;
```

**Step 2: Add Route**

```javascript
// src/App.jsx

import PronunciationPractice from './components/Learning/PronunciationPractice';

function App() {
  return (
    <Router>
      <Routes>
        {/* Existing routes... */}
        <Route path="/pronunciation" element={<PronunciationPractice />} />
      </Routes>
    </Router>
  );
}
```

**Step 3: Add to Navigation**

```javascript
// src/components/Common/Navigation.jsx

const navItems = [
  // ... existing items
  {
    path: '/pronunciation',
    label: 'Pronunciation',
    icon: '🎤'
  }
];
```

**Step 4: Add to Dashboard**

```javascript
// src/components/Dashboard/Dashboard.jsx

const modules = [
  // ... existing modules
  {
    id: 'pronunciation',
    title: 'Pronunciation Practice',
    icon: '🎤',
    description: 'Improve your pronunciation',
    path: '/pronunciation'
  }
];
```

#### Creating a Custom Service

**Example: Idioms Service**

```javascript
// src/services/idioms.js

class IdiomsService {
  constructor() {
    this.idioms = this.loadIdioms();
  }

  loadIdioms() {
    return [
      {
        idiom: 'break the ice',
        meaning: 'Make people feel more comfortable',
        example: 'He told a joke to break the ice at the meeting.',
        difficulty: 'intermediate'
      },
      // More idioms...
    ];
  }

  getRandomIdiom(difficulty = null) {
    let filtered = this.idioms;

    if (difficulty) {
      filtered = this.idioms.filter(i => i.difficulty === difficulty);
    }

    return filtered[Math.floor(Math.random() * filtered.length)];
  }

  searchIdioms(query) {
    const lowerQuery = query.toLowerCase();
    return this.idioms.filter(i =>
      i.idiom.toLowerCase().includes(lowerQuery) ||
      i.meaning.toLowerCase().includes(lowerQuery)
    );
  }

  getIdiomsExercise(count = 5, difficulty = 'intermediate') {
    const filtered = this.idioms.filter(i => i.difficulty === difficulty);
    const selected = [];

    for (let i = 0; i < count && filtered.length > 0; i++) {
      const index = Math.floor(Math.random() * filtered.length);
      selected.push(filtered.splice(index, 1)[0]);
    }

    return {
      type: 'matching',
      instructions: 'Match each idiom with its meaning',
      idioms: selected
    };
  }
}

export default new IdiomsService();
```

**Using the Service:**

```javascript
import idiomsService from './services/idioms';

// Get random idiom
const idiom = idiomsService.getRandomIdiom('intermediate');

// Search idioms
const results = idiomsService.searchIdioms('time');

// Generate exercise
const exercise = idiomsService.getIdiomsExercise(5, 'advanced');
```

#### Adding Analytics Tracking

**Create Analytics Service:**

```javascript
// src/services/analytics.js

class AnalyticsService {
  constructor() {
    this.events = [];
  }

  track(eventName, properties = {}) {
    const event = {
      name: eventName,
      properties,
      timestamp: new Date().toISOString()
    };

    this.events.push(event);

    // Store in localStorage
    this.saveEvents();

    // Optional: Send to analytics service
    // this.sendToServer(event);
  }

  saveEvents() {
    localStorage.setItem('analytics_events', JSON.stringify(this.events));
  }

  loadEvents() {
    const stored = localStorage.getItem('analytics_events');
    return stored ? JSON.parse(stored) : [];
  }

  getEventsByType(eventName) {
    return this.events.filter(e => e.name === eventName);
  }

  getEventStats() {
    const stats = {};

    this.events.forEach(event => {
      if (!stats[event.name]) {
        stats[event.name] = 0;
      }
      stats[event.name]++;
    });

    return stats;
  }

  // Usage tracking
  trackModuleUsage(moduleName, duration) {
    this.track('module_used', {
      module: moduleName,
      duration: duration // in seconds
    });
  }

  trackExerciseCompleted(exerciseType, score) {
    this.track('exercise_completed', {
      type: exerciseType,
      score: score
    });
  }

  trackError(errorMessage, context) {
    this.track('error', {
      message: errorMessage,
      context: context
    });
  }
}

export default new AnalyticsService();
```

**Usage:**

```javascript
import analytics from './services/analytics';

// Track module usage
analytics.trackModuleUsage('conversation', 300); // 5 minutes

// Track exercise completion
analytics.trackExerciseCompleted('grammar', 85);

// Track errors
analytics.trackError('AI service unavailable', { module: 'conversation' });

// View stats
const stats = analytics.getEventStats();
console.log(stats);
// { module_used: 45, exercise_completed: 120, error: 3 }
```

---

### 23. Performance Optimization

#### Code Splitting

**Lazy Load Routes:**

```javascript
// src/App.jsx

import { lazy, Suspense } from 'react';

// Lazy load components
const Dashboard = lazy(() => import('./components/Dashboard/Dashboard'));
const ConversationPractice = lazy(() => import('./components/Learning/ConversationPractice'));
const VocabularyPractice = lazy(() => import('./components/Learning/VocabularyPractice'));
// ... more components

function App() {
  return (
    <Router>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/conversation" element={<ConversationPractice />} />
          <Route path="/vocabulary" element={<VocabularyPractice />} />
          {/* ... more routes */}
        </Routes>
      </Suspense>
    </Router>
  );
}
```

**Benefits:**
- Initial bundle size reduced
- Faster page load
- Components loaded only when needed

#### Memoization

**React.memo for Components:**

```javascript
import { memo } from 'react';

const SkillCard = memo(({ skill, score, onUpdate }) => {
  console.log(`Rendering ${skill}`);

  return (
    <div className="skill-card">
      <h3>{skill}</h3>
      <p>Score: {score}</p>
      <button onClick={() => onUpdate(skill)}>Practice</button>
    </div>
  );
});

export default SkillCard;
```

**useMemo for Expensive Calculations:**

```javascript
import { useMemo } from 'react';

function ProgressChart({ exerciseHistory }) {
  // Only recalculate when exerciseHistory changes
  const chartData = useMemo(() => {
    return exerciseHistory.map(ex => ({
      date: ex.date,
      score: ex.score
    }));
  }, [exerciseHistory]);

  return <LineChart data={chartData} />;
}
```

**useCallback for Functions:**

```javascript
import { useCallback } from 'react';

function VocabularyList({ words, onWordClick }) {
  const handleClick = useCallback((wordId) => {
    onWordClick(wordId);
  }, [onWordClick]);

  return words.map(word => (
    <WordCard
      key={word.id}
      word={word}
      onClick={() => handleClick(word.id)}
    />
  ));
}
```

#### Database Optimization

**Index Frequently Queried Fields:**

```sql
-- In init-db.js

-- Index for user lookup
CREATE INDEX idx_user_id ON exercise_history(user_id);

-- Index for date range queries
CREATE INDEX idx_completed_at ON exercise_history(completed_at);

-- Compound index for common queries
CREATE INDEX idx_user_type ON exercise_history(user_id, exercise_type);
```

**Batch Database Operations:**

```javascript
// Instead of:
for (const word of words) {
  await database.addVocabulary(word);
}

// Do this:
await database.addVocabularyBatch(words);

// Implementation:
async addVocabularyBatch(words) {
  const stmt = this.db.prepare(`
    INSERT INTO vocabulary (word, definition, example)
    VALUES (?, ?, ?)
  `);

  const transaction = this.db.transaction((words) => {
    for (const word of words) {
      stmt.run(word.word, word.definition, word.example);
    }
  });

  transaction(words);
}
```

#### API Request Optimization

**Debounce AI Requests:**

```javascript
import { useCallback } from 'react';
import { debounce } from 'lodash';

function WritingEditor() {
  const [text, setText] = useState('');

  // Debounce AI evaluation - wait 1 second after user stops typing
  const evaluateText = useCallback(
    debounce(async (text) => {
      const result = await aiService.evaluateWriting(text);
      setFeedback(result);
    }, 1000),
    []
  );

  const handleChange = (e) => {
    const newText = e.target.value;
    setText(newText);
    evaluateText(newText);
  };

  return <textarea value={text} onChange={handleChange} />;
}
```

**Cache AI Responses:**

```javascript
// Simple cache implementation
const cache = new Map();

async function getCachedAIResponse(prompt) {
  // Check cache first
  if (cache.has(prompt)) {
    return cache.get(prompt);
  }

  // Make AI request
  const response = await aiService.chat([{
    role: 'user',
    content: prompt
  }]);

  // Store in cache
  cache.set(prompt, response);

  return response;
}

// Clear old cache entries periodically
setInterval(() => {
  if (cache.size > 100) {
    cache.clear();
  }
}, 60000); // Every minute
```

#### Bundle Size Optimization

**Analyze Bundle:**

```bash
# Install bundle analyzer
npm install --save-dev vite-plugin-visualizer

# Update vite.config.js
import { visualizer } from 'vite-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    visualizer({ open: true })
  ]
});

# Build and view report
npm run build
```

**Tree Shaking:**

```javascript
// Instead of:
import _ from 'lodash';

// Do this:
import debounce from 'lodash/debounce';
import throttle from 'lodash/throttle';
// Only imports specific functions
```

**Remove Unused Dependencies:**

```bash
# Audit dependencies
npm install -g depcheck
depcheck

# Remove unused packages
npm uninstall <package-name>
```

---

### 24. Troubleshooting

#### Common Issues and Solutions

**Issue 1: "Cannot find module" errors**

**Symptoms:**
```
Error: Cannot find module './services/aiService'
```

**Solution:**
```bash
# Check file exists
ls src/services/aiService.js

# Check import path
# Incorrect:
import aiService from './aiService';

# Correct (from component):
import aiService from '../../services/aiService';

# Or use absolute imports (configure in vite.config.js):
import aiService from '@/services/aiService';
```

---

**Issue 2: localStorage quota exceeded**

**Symptoms:**
```
QuotaExceededError: Failed to execute 'setItem' on 'Storage'
```

**Solution:**
```javascript
// Check storage usage
const getStorageSize = () => {
  let total = 0;
  for (let key in localStorage) {
    if (localStorage.hasOwnProperty(key)) {
      total += localStorage[key].length + key.length;
    }
  }
  return (total / 1024).toFixed(2) + ' KB';
};

console.log('Storage used:', getStorageSize());

// Clear old data
const clearOldExercises = () => {
  const history = JSON.parse(localStorage.getItem('exercise_history') || '[]');

  // Keep only last 100 exercises
  if (history.length > 100) {
    const recent = history.slice(-100);
    localStorage.setItem('exercise_history', JSON.stringify(recent));
  }
};

// Implement automatic cleanup
setInterval(clearOldExercises, 86400000); // Daily
```

---

**Issue 3: AI service not responding**

**Symptoms:**
- Requests timeout
- No feedback on exercises

**Solution:**
```javascript
// Check API key
const apiKey = import.meta.env.VITE_ANTHROPIC_API_KEY;
if (!apiKey) {
  console.error('API key not configured');
  // Prompt user to add key
}

// Check Ollama service (if using local)
try {
  const response = await fetch('http://localhost:11434/api/tags');
  if (!response.ok) {
    console.error('Ollama not running');
    // Show error message
  }
} catch (error) {
  console.error('Cannot connect to Ollama');
}

// Add timeout to AI requests
const timeoutPromise = new Promise((_, reject) =>
  setTimeout(() => reject(new Error('Request timeout')), 30000)
);

const aiPromise = aiService.chat(messages);

try {
  const result = await Promise.race([aiPromise, timeoutPromise]);
} catch (error) {
  console.error('AI request failed:', error.message);
  // Use fallback response
  const fallback = aiService.getFallbackResponse();
}
```

---

**Issue 4: Speech recognition not working**

**Symptoms:**
- Microphone button does nothing
- No transcription appearing

**Solution:**
```javascript
// Check browser support
if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
  alert('Speech recognition not supported in this browser. Use Chrome or Edge.');
}

// Check HTTPS (required for speech API)
if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
  alert('Speech recognition requires HTTPS or localhost');
}

// Check microphone permission
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(() => {
    console.log('Microphone access granted');
  })
  .catch((error) => {
    console.error('Microphone access denied:', error);
    alert('Please allow microphone access in browser settings');
  });

// Add error handling to recognition
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

recognition.onerror = (event) => {
  console.error('Speech recognition error:', event.error);

  switch(event.error) {
    case 'no-speech':
      alert('No speech detected. Please try again.');
      break;
    case 'audio-capture':
      alert('No microphone detected.');
      break;
    case 'not-allowed':
      alert('Microphone access denied.');
      break;
    default:
      alert('Speech recognition error: ' + event.error);
  }
};
```

---

**Issue 5: Slow performance**

**Symptoms:**
- UI feels sluggish
- Long load times
- Delayed responses

**Solution:**
```javascript
// 1. Check component re-renders
import { useEffect } from 'react';

function Dashboard() {
  useEffect(() => {
    console.log('Dashboard rendered');
  });

  // If this logs too often, optimize with memo/useMemo
}

// 2. Profile with React DevTools
// Install React DevTools browser extension
// Open DevTools → Profiler → Record
// Identify slow components

// 3. Reduce AI requests
// Cache responses
const responseCache = new Map();

const getCachedResponse = async (prompt) => {
  const key = JSON.stringify(prompt);
  if (responseCache.has(key)) {
    return responseCache.get(key);
  }

  const response = await aiService.chat(prompt);
  responseCache.set(key, response);
  return response;
};

// 4. Optimize database queries
// Add indexes (see init-db.js)
// Limit query results
const recentExercises = await database.getExerciseHistory(20); // Only last 20

// 5. Clear browser data
// Settings → Clear browsing data → Cached images and files
```

---

**Issue 6: Build fails**

**Symptoms:**
```
Error: Build failed with errors
```

**Solutions:**

```bash
# 1. Clear build cache
rm -rf node_modules
rm -rf dist
rm package-lock.json
npm install

# 2. Check Node.js version
node --version
# Should be 16.0.0 or higher

# 3. Update dependencies
npm update

# 4. Check for TypeScript errors (if applicable)
npm run lint

# 5. Build with verbose logging
npm run build -- --debug

# 6. Check vite.config.js syntax
# Ensure proper export
export default defineConfig({
  // config
});
```

---

**Issue 7: Data not persisting**

**Symptoms:**
- Progress resets after refresh
- Settings don't save

**Solution:**
```javascript
// 1. Check localStorage is enabled
try {
  localStorage.setItem('test', 'test');
  localStorage.removeItem('test');
  console.log('localStorage is working');
} catch (e) {
  console.error('localStorage is disabled', e);
  alert('Please enable cookies/storage in browser settings');
}

// 2. Check browser private/incognito mode
// localStorage may be disabled in private mode

// 3. Verify save operation
const saveSettings = (settings) => {
  try {
    localStorage.setItem('settings', JSON.stringify(settings));
    console.log('Settings saved successfully');
  } catch (error) {
    console.error('Failed to save settings:', error);
    // Try export/download as file instead
  }
};

// 4. Add save confirmation
const [saveStatus, setSaveStatus] = useState('');

const handleSave = () => {
  saveSettings(settings);
  setSaveStatus('Saved!');
  setTimeout(() => setSaveStatus(''), 2000);
};

return (
  <div>
    <button onClick={handleSave}>Save</button>
    {saveStatus && <p>{saveStatus}</p>}
  </div>
);
```

---

### 25. FAQs

#### General Questions

**Q: Do I need an internet connection?**

A: Partially.
- **With Internet**: Full AI features, Claude API, online exercises
- **Without Internet**: Core features work, Ollama (if installed), stored data access
- **Recommendation**: Use Ollama for offline-capable AI features

---

**Q: How much does it cost to use?**

A: The app itself is free and open-source.
- **Claude API**: Pay-per-use (~$1-2/month for typical usage)
- **Ollama**: Completely free (local AI)
- **Hosting**: Free tier available on Vercel, Netlify

---

**Q: Is my data private?**

A: Yes.
- All data stored locally (localStorage or SQLite)
- No external database
- No tracking/analytics by default
- AI requests contain only your exercise responses
- Can export/delete all data anytime

---

**Q: Can I use this on mobile?**

A: Yes, but with limitations.
- Responsive design works on mobile browsers
- Speech recognition limited on iOS
- Better experience on tablet/desktop
- Consider installing as PWA for app-like experience

---

**Q: How long until I see improvement?**

A: Depends on practice frequency:
- **Daily practice (30 min)**: Noticeable improvement in 2-3 weeks
- **3x per week (30 min)**: Improvement in 4-6 weeks
- **Intensive (60+ min daily)**: Significant progress in 2-3 weeks
- **Key**: Consistency matters more than length

---

#### Technical Questions

**Q: What's the difference between Claude and Ollama?**

A:
- **Claude** (Anthropic): Cloud AI, excellent quality, requires API key, costs money
- **Ollama**: Local AI, good quality, free, requires installation, runs on your computer

Both work with the same app interface.

---

**Q: Can I backup my progress?**

A: Yes, multiple ways:
```javascript
// 1. Export to JSON file (built-in feature)
Settings → Export Data → Download JSON

// 2. Manual backup (browser)
// Open browser DevTools → Application → Local Storage → Copy all

// 3. Database backup (Node.js)
// Copy database/learning.db file
```

---

**Q: Can I use custom AI models?**

A: Yes, for Ollama:
```bash
# Any model supported by Ollama works
ollama pull mistral
ollama pull codellama
ollama pull dolphin-phi

# Configure in Settings → Model Name
```

For Claude, only official Anthropic models are supported.

---

**Q: How do I reset my progress?**

A:
```javascript
// Option 1: In app
Settings → Reset All Data → Confirm

// Option 2: Manual (browser)
// DevTools → Application → Local Storage → Clear

// Option 3: Code
localStorage.clear();
```

---

**Q: Can multiple people use the same installation?**

A: Not ideal for browser version (shared localStorage).

**Solutions:**
- Different browser profiles
- Different devices
- Deploy separate instances
- Use Node.js version with separate database files

---

**Q: How do I update to the latest version?**

A:
```bash
# Pull latest code
git pull origin main

# Install any new dependencies
npm install

# Rebuild
npm run build

# Restart dev server
npm run dev
```

---

#### Learning Questions

**Q: What level should I start at?**

A: Take the baseline assessment - it will set your level automatically.
- Don't worry about getting it perfect
- Difficulty adjusts based on your performance
- You can manually adjust in Settings if needed

---

**Q: How often should I practice?**

A: **Recommendation:**
- Minimum: 10-15 minutes daily (7 days/week)
- Optimal: 30 minutes daily (5-7 days/week)
- Intensive: 60+ minutes daily (if you have a deadline)

Consistency beats length - 15 min every day > 2 hours once a week.

---

**Q: What if I make a lot of mistakes?**

A: Great! Mistakes are how you learn.
- The app tracks patterns in your mistakes
- Provides targeted correction strategies
- Don't be afraid to make mistakes
- Focus on learning from them, not avoiding them

---

**Q: Should I focus on one skill or practice everything?**

A: **Balanced approach:**
- Follow the app's recommendations
- Practice all skills regularly
- Spend extra time on weakest skill
- Don't neglect your strongest skills

The app's skill radar shows if you're unbalanced.

---

**Q: How do I prepare for IELTS/TOEFL?**

A: Use the **Learning Paths** feature:
1. Go to Learning Paths
2. Select "IELTS/TOEFL Preparation"
3. Follow the 8-12 week structured plan
4. Practice all 4 sections (Speaking, Writing, Reading, Listening)
5. Take practice tests (external resources)

---

**Q: Can this replace a human teacher?**

A: No, but it's an excellent supplement.

**Best used for:**
- Daily practice between lessons
- Vocabulary building
- Grammar exercises
- Writing practice
- Self-paced learning

**Not a replacement for:**
- Real conversations with humans
- Pronunciation correction (nuanced)
- Cultural immersion
- Personalized curriculum design

**Recommendation:** Use this app + practice with native speakers + (optionally) take classes.

---

## Conclusion

**Congratulations!** You now have a complete understanding of the AI-Powered English Learning Application.

### Quick Reference

**To run the app:**
```bash
npm install
npm run dev
```

**To deploy:**
```bash
npm run build
# Deploy dist/ folder to your hosting platform
```

**For help:**
- Review this guide
- Check README.md
- See PHASE2-3-FEATURES.md for advanced features
- See ADVANCED_FEATURES.md for Phase 1 features

### Best Practices

1. **Practice Daily** - Even 10 minutes counts
2. **Follow Recommendations** - Let the AI guide you
3. **Review Mistakes** - Learn from errors
4. **Use Multiple Features** - Balance all skills
5. **Track Progress** - Watch yourself improve
6. **Export Data** - Backup monthly
7. **Experiment** - Try all modules and features

### Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Review troubleshooting section
- Check FAQs

---

**Happy Learning! 🎓✨**

Remember: Language learning is a journey, not a destination. With consistent practice and the intelligent features in this app, you'll see steady improvement in your English skills.

**Version 2.0.0** | Last Updated: 2025

# Interview Preparation Tracker

A comprehensive full-stack application designed to help developers prepare systematically for technical interviews. Track your progress, manage topics, use spaced repetition flashcards, conduct mock interviews, implement Pomodoro study sessions, and analyze your preparation with advanced analytics.

## Table of Contents

- [Features Overview](#features-overview)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [Database Information](#database-information)
- [Troubleshooting](#troubleshooting)

## Features Overview

### Phase 1: Core Topic Management & Progress Tracking
- **Topic Management**: Add, edit, delete, and categorize interview topics (Data Structures, Algorithms, System Design, Behavioral, etc.)
- **Difficulty Levels**: Classify topics as Easy, Medium, or Hard
- **Progress Tracking**: Track completion status and confidence levels (1-10 scale)
- **Practice Sessions**: Log study sessions with duration, notes, performance ratings, and confidence updates
- **Topic Search & Filter**: Search by name, filter by category, difficulty, status, or confidence
- **Visual Dashboard**: View progress charts, confidence trends, and category distribution
- **File Management**: Upload and organize study materials (PDFs, images, notes) by topic
- **Weekly Goal Tracking**: Set and track weekly study goals per category
- **Smart Revision Suggestions**: AI-powered priority algorithm for optimal review scheduling

### Phase 2: Enhanced Productivity & Analytics
- **Pomodoro Timer**:
  - Focus sessions (25 min), Short breaks (5 min), Long breaks (15 min)
  - Track Pomodoro count per topic
  - Historical Pomodoro statistics and session history

- **Mock Interview Generator**:
  - Generate balanced interview question sets
  - Smart category distribution based on your weak areas
  - Difficulty-based question selection
  - Mock interview history tracking with timestamps

- **Confidence Decay System**:
  - Automatic confidence decay for stale topics (prevents overconfidence)
  - Configurable decay rules (days inactive threshold, decay percentage)
  - Manual and automatic decay triggers
  - Confidence history tracking with audit trail

- **Enhanced Analytics**:
  - Streak tracking (current and longest study streaks)
  - Time-based metrics (daily, weekly, monthly study time)
  - Category-wise performance analysis
  - Confidence distribution heatmaps
  - Topic aging insights and stale topic detection

### Phase 3: Advanced Learning Tools
- **Flashcard System (SM-2 Spaced Repetition)**:
  - Create flashcards for any topic (front/back cards)
  - Spaced repetition scheduling using SuperMemo SM-2 algorithm
  - Quality ratings (0-5) that adjust review intervals dynamically
  - Ease factor adaptation per card
  - Due date tracking and review queue management
  - Success/failure statistics per card
  - Repetition count tracking

- **Voice Notes**:
  - Record audio explanations for topics (browser-based recording)
  - Playback and management interface
  - Topic-specific voice note library
  - Timestamp tracking for each recording
  - No external dependencies required

- **Backup & Restore**:
  - Export all data (topics, sessions, flashcards, settings, voice notes metadata)
  - Import from backup files with validation
  - Automatic file metadata tracking
  - Storage usage monitoring
  - Backup history with timestamps
  - Safe data migration

## Technology Stack

### Backend
- **Framework**: Spring Boot 3.2.0
- **Language**: Java 17
- **Database**: H2 (file-based, persistent)
- **Build Tool**: Maven 3.9+
- **ORM**: Spring Data JPA / Hibernate
- **Libraries**:
  - Lombok 1.18.30 (code generation)
  - Jackson (JSON processing)
  - Jakarta Validation

### Frontend
- **Framework**: React 18
- **Language**: TypeScript 5.2+
- **Build Tool**: Vite 5.0
- **Routing**: React Router v6
- **Styling**: Tailwind CSS 3.4
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Charts**: Recharts 2.10

### Development Tools
- **Version Control**: Git
- **Package Manager**: npm
- **Code Quality**: ESLint, TypeScript strict mode

## Quick Start

### Prerequisites
- Java 17 or higher ([Download JDK](https://adoptium.net/))
- Maven 3.9+ ([Installation Guide](https://maven.apache.org/install.html))
- Node.js 18+ and npm ([Download Node.js](https://nodejs.org/))
- Git ([Download Git](https://git-scm.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd interview-tracker
   ```

2. **Build and start the backend**
   ```bash
   cd backend
   mvn clean install -DskipTests
   mvn spring-boot:run
   ```

   Backend will start at `http://localhost:8080`

3. **Install and start the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Frontend will start at `http://localhost:3000`

4. **Access the application**

   Open your browser and navigate to `http://localhost:3000`

### One-Liner Setup (After Prerequisites)
```bash
# Terminal 1 (Backend)
cd backend && mvn spring-boot:run

# Terminal 2 (Frontend)
cd frontend && npm install && npm run dev
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[SETUP.md](docs/SETUP.md)** - Detailed installation and configuration guide
- **[USER_GUIDE.md](docs/USER_GUIDE.md)** - Complete feature walkthrough with examples
- **[DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)** - Technical implementation details
- **[API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)** - Complete REST API reference
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and design decisions
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Production deployment instructions

## Project Structure

```
interview-tracker/
├── backend/                      # Spring Boot backend application
│   ├── src/main/java/
│   │   └── com/interviewtracker/
│   │       ├── config/          # Configuration classes
│   │       ├── controller/      # REST API controllers (18 controllers)
│   │       ├── dto/             # Data Transfer Objects
│   │       ├── exception/       # Custom exceptions
│   │       ├── model/           # JPA entities (12 entities)
│   │       ├── repository/      # Spring Data repositories (12 repos)
│   │       └── service/         # Business logic (18 services)
│   ├── src/main/resources/
│   │   └── application.properties
│   └── pom.xml                 # Maven dependencies
│
├── frontend/                    # React TypeScript frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── analytics/      # Analytics visualizations
│   │   │   ├── flashcards/     # Flashcard system UI
│   │   │   ├── topics/         # Topic management UI
│   │   │   ├── pomodoro/       # Pomodoro timer UI
│   │   │   ├── voicenotes/     # Voice recording UI
│   │   │   └── dashboard/      # Dashboard components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── services/           # API service layer
│   │   ├── types/              # TypeScript type definitions
│   │   ├── utils/              # Utility functions
│   │   ├── App.tsx             # Root component
│   │   └── main.tsx            # Application entry point
│   ├── package.json            # npm dependencies
│   ├── tsconfig.json           # TypeScript configuration
│   ├── vite.config.ts          # Vite configuration
│   └── tailwind.config.js      # Tailwind CSS configuration
│
├── uploads/                     # File storage (created at runtime)
│   ├── audio/                  # Voice note recordings
│   └── backups/                # Data backups
│
├── database/                    # H2 database files (created at runtime)
│
└── docs/                        # Comprehensive documentation
    ├── SETUP.md
    ├── USER_GUIDE.md
    ├── DEVELOPER_GUIDE.md
    ├── API_DOCUMENTATION.md
    ├── ARCHITECTURE.md
    └── DEPLOYMENT.md
```

## Database Information

The application uses H2 database with file-based persistence:

- **Database Location**: `./database/interviewtracker.mv.db`
- **Console Access**: `http://localhost:8080/h2-console`
- **JDBC URL**: `jdbc:h2:file:./database/interviewtracker`
- **Username**: `sa`
- **Password**: (leave blank)

The database persists data between restarts. To reset the database, stop the backend and delete the `database/` directory.

## Default Configuration

### Backend (application.properties)
- **Server Port**: 8080
- **Upload Directory**: `./uploads`
- **Backup Directory**: `./uploads/backups`
- **Max File Size**: 10MB
- **Allowed Origins**: `http://localhost:3000`, `http://localhost:5173`

### Frontend (vite.config.ts)
- **Dev Server Port**: 3000
- **API Proxy**: `/api` → `http://localhost:8080`

## Daily Workflow

1. **Start your day**: Open the app and check the dashboard for topics due for review
2. **Select a topic**: Choose from topics with low confidence or approaching reminders
3. **Start Pomodoro**: Begin a focused 25-minute study session
4. **Review flashcards**: Go through due flashcards for the topic using spaced repetition
5. **Add notes**: Record voice notes for complex explanations
6. **Log session**: Record your practice session with updated confidence
7. **Mock interview**: Test yourself with a generated mock interview set
8. **Review analytics**: Check your streaks, study time, and progress metrics
9. **Backup data**: Periodically export your data for safekeeping

## Key Features in Detail

### Spaced Repetition (SM-2 Algorithm)
The flashcard system implements the SuperMemo SM-2 algorithm:
- Initial interval: 1 day
- Second interval: 6 days
- Subsequent intervals: previous interval × ease factor
- Ease factor adjusts based on your quality ratings (0-5)
- Minimum ease factor: 1.3 (prevents too-frequent reviews)
- Formula: `new_ease = old_ease + (280 - (5 - quality) * 280)`

### Confidence Decay
Topics automatically decay in confidence if not reviewed:
- Default: 5% decay every 7 days of inactivity
- Configurable decay amount (1-20%) and interval (1-90 days)
- Helps you identify topics that need refreshing
- View decay history for audit trail
- Prevents overconfidence on stale topics

### Smart Mock Interviews
The generator creates balanced question sets:
- Distributes questions across categories
- Weighs selection by difficulty and confidence (prioritizes weak areas)
- Limits questions per category for variety
- Saves mock interview history for tracking
- Configurable set size

## Troubleshooting

### Backend won't start
- Ensure Java 17+ is installed: `java -version`
- Check port 8080 is not in use: `lsof -i :8080` (Mac/Linux) or `netstat -ano | findstr :8080` (Windows)
- Verify Maven build succeeded: `mvn clean install`
- Check `backend.log` for errors

### Frontend won't start
- Ensure Node.js 18+ is installed: `node -v`
- Check port 3000 is not in use
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

### "Cannot connect to backend" error
- Verify backend is running on port 8080
- Check browser console for CORS errors
- Ensure API proxy is configured in `vite.config.ts`
- Verify `http://localhost:8080/api/topics` returns data

### Database errors
- Delete the `database/` directory to reset
- Check file permissions on the database directory
- Ensure no other instance is accessing the database

### Lombok compilation errors
If you see "cannot find symbol" errors for getters/setters:
- Verify `maven-compiler-plugin` is configured in `pom.xml`
- Run `mvn clean install` to trigger annotation processing
- Check that Lombok version 1.18.30 is in dependencies

## API Overview

The application exposes **130+ REST endpoints** organized into:

- **Topics** (9 endpoints) - CRUD operations for topics
- **Practice Sessions** (7 endpoints) - Session logging and retrieval
- **Files** (8 endpoints) - File upload/download/preview
- **Dashboard** (5 endpoints) - Revision suggestions and progress
- **Analytics** (12 endpoints) - Comprehensive metrics and insights
- **Settings** (4 endpoints) - Configuration management
- **Pomodoro** (11 endpoints) - Timer and session management
- **Mock Interviews** (9 endpoints) - Generate and track mock interviews
- **Confidence Decay** (7 endpoints) - Decay rules and history
- **Flashcards** (18 endpoints) - Spaced repetition flashcard system
- **Voice Notes** (9 endpoints) - Audio recording management
- **Backup & Restore** (6 endpoints) - Data export/import

See [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for complete details.

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues, questions, or suggestions:
- Check the documentation in the `docs/` folder
- Review the troubleshooting section above
- Open an issue on GitHub

## License

This project is licensed under the MIT License.

## Acknowledgments

- SuperMemo SM-2 Algorithm for spaced repetition
- Spring Boot framework and community
- React and TypeScript communities
- Tailwind CSS for styling utilities
- All open-source contributors

---

**Built with ❤️ for interview preparation success**

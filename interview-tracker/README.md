# Interview Preparation Tracker

A comprehensive full-stack application to track your interview preparation progress across Data Structures & Algorithms (DSA), High-Level Design (HLD), Low-Level Design (LLD), and Behavioral interview topics.

## Features

### 🎯 Core Features (Phase 1)

1. **Topic Management**
   - Manage topics across 4 categories: DSA, HLD, LLD, Behavioral
   - Track confidence levels (1-10 scale)
   - Record time spent, notes, and things to remember
   - Category-specific fields (difficulty for DSA, pages read for HLD, etc.)

2. **Practice Session Logging**
   - Log practice sessions with duration and performance ratings
   - Track what went well and mistakes made
   - Session types: First Learning, Revision, Mock Interview, Quick Review
   - Automatic confidence updates based on latest performance

3. **File Upload & Management**
   - Upload files (PDF, Word, Text, Markdown, HTML, Images)
   - Organized by topic
   - Preview images and text files
   - Download files for offline access

4. **Smart Dashboard**
   - Intelligent revision suggestions based on weighted priority algorithm
   - Considers difficulty, confidence, and recency
   - Weekly progress tracking with color-coded status
   - Filter suggestions by category

5. **Weekly Goal Tracking**
   - Set weekly goals for each category
   - Track progress with visual indicators
   - View historical weekly progress (last 8 weeks)
   - Configurable week start day

6. **Analytics Dashboard**
   - Total time studied and session counts
   - Study streak tracking (current and longest)
   - Topics breakdown by category and confidence level
   - Time distribution charts
   - Recent activity log

7. **Settings & Data Management**
   - Configure daily study hours and weekly goals
   - Export/Import all data as JSON
   - Create backups
   - Reset all data with confirmation
   - Storage usage information

## Technology Stack

### Backend
- **Java 17** with **Spring Boot 3.2.0**
- **H2 Database** (embedded, file-based for persistence)
- **Spring Data JPA** for data persistence
- **Maven** for dependency management

### Frontend
- **React 18** with **TypeScript**
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Recharts** for analytics visualizations
- **Axios** for API communication
- **React Router** for navigation

## Prerequisites

Before running the application, make sure you have the following installed:

- **Java 17 or higher** - [Download](https://adoptium.net/)
- **Maven 3.6+** - [Download](https://maven.apache.org/download.cgi)
- **Node.js 18+** and **npm** - [Download](https://nodejs.org/)

## Installation & Setup

### Quick Start (Recommended)

1. **Clone or navigate to the project directory:**
   ```bash
   cd interview-tracker
   ```

2. **Start both backend and frontend:**
   ```bash
   ./start-all.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8080
   - H2 Console: http://localhost:8080/h2-console

### Manual Setup

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Build and run the Spring Boot application:
   ```bash
   mvn spring-boot:run
   ```

   Or use the startup script:
   ```bash
   cd ..
   ./start-backend.sh
   ```

3. The backend will start on `http://localhost:8080`

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   Or use the startup script:
   ```bash
   cd ..
   ./start-frontend.sh
   ```

4. The frontend will start on `http://localhost:3000`

## Project Structure

```
interview-tracker/
├── backend/                    # Spring Boot backend
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/interviewtracker/
│   │   │   │   ├── controller/       # REST API controllers
│   │   │   │   ├── service/          # Business logic services
│   │   │   │   ├── repository/       # Data access layer
│   │   │   │   ├── model/            # JPA entities
│   │   │   │   ├── dto/              # Data Transfer Objects
│   │   │   │   ├── exception/        # Exception handlers
│   │   │   │   └── config/           # Configuration classes
│   │   │   └── resources/
│   │   │       └── application.properties
│   │   └── test/
│   └── pom.xml
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/          # Reusable components
│   │   │   ├── layout/          # Layout components
│   │   │   ├── common/          # Common UI components
│   │   │   ├── topics/          # Topic-related components
│   │   │   ├── sessions/        # Session components
│   │   │   ├── files/           # File management
│   │   │   ├── dashboard/       # Dashboard components
│   │   │   ├── analytics/       # Analytics charts
│   │   │   └── settings/        # Settings components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API services
│   │   ├── types/               # TypeScript type definitions
│   │   ├── hooks/               # Custom React hooks
│   │   ├── context/             # React contexts
│   │   ├── utils/               # Utility functions
│   │   ├── App.tsx              # Main App component
│   │   ├── main.tsx             # Entry point
│   │   └── index.css            # Global styles
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── start-backend.sh            # Backend startup script
├── start-frontend.sh           # Frontend startup script
├── start-all.sh                # Combined startup script
└── README.md                   # This file
```

## API Endpoints

### Topics
- `GET /api/topics/{category}` - Get all topics by category
- `GET /api/topics/{category}/{id}` - Get topic by ID
- `POST /api/topics/{category}` - Create new topic
- `PUT /api/topics/{category}/{id}` - Update topic
- `DELETE /api/topics/{category}/{id}` - Delete topic

### Practice Sessions
- `GET /api/sessions/topic/{topicId}` - Get sessions for a topic
- `POST /api/sessions/topic/{topicId}` - Create new session
- `PUT /api/sessions/{id}` - Update session
- `DELETE /api/sessions/{id}` - Delete session
- `GET /api/sessions/recent?limit=10` - Get recent sessions

### Files
- `POST /api/files/upload/{topicId}` - Upload file
- `GET /api/files/topic/{topicId}` - Get files for topic
- `GET /api/files/{id}` - Download file
- `GET /api/files/{id}/preview` - Preview file (images/text)
- `DELETE /api/files/{id}` - Delete file

### Dashboard
- `GET /api/dashboard/suggestions` - Get revision suggestions
- `GET /api/dashboard/weekly/progress` - Get current week progress
- `GET /api/dashboard/weekly/history?weeks=8` - Get weekly history

### Analytics
- `GET /api/analytics/summary` - Get analytics summary
- `GET /api/analytics/recent-activity?limit=10` - Get recent activity

### Settings
- `GET /api/settings` - Get settings
- `PUT /api/settings` - Update settings

### Data Management
- `GET /api/data/export` - Export all data
- `POST /api/data/import` - Import data
- `DELETE /api/data/reset` - Reset all data
- `POST /api/data/backup` - Create backup
- `GET /api/data/storage-info` - Get storage information

## Database

The application uses H2 database with file-based persistence:

- **Location:** `~/interview-tracker/data/tracker.mv.db`
- **Console:** http://localhost:8080/h2-console
  - JDBC URL: `jdbc:h2:file:~/interview-tracker/data/tracker`
  - Username: `sa`
  - Password: (leave empty)

## File Storage

Uploaded files are stored at:
- **Upload Directory:** `~/interview-tracker/uploads/`
- **Backup Directory:** `~/interview-tracker/backups/`

## Usage Guide

### Adding a Topic

1. Navigate to the appropriate category page (DSA, HLD, LLD, or Behavioral)
2. Click "Add New Topic"
3. Fill in the required fields:
   - Topic name (or Question for Behavioral)
   - Confidence level (1-10)
   - Category-specific fields (difficulty for DSA, etc.)
   - Optional: notes, source URL, things to remember
4. Click "Save"

### Logging a Practice Session

1. Find your topic in the list
2. Click "Practice" button
3. Fill in the session details:
   - Duration (minutes)
   - Performance rating (1-10)
   - Session type
   - Optional: what went well, mistakes made, notes
4. Click "Save Session"

### Using the Dashboard

The dashboard provides:
- **Weekly Progress Cards:** Visual progress for each category
- **Revision Suggestions:** Prioritized list of topics to review
  - Higher priority = needs more attention
  - Filter by category
  - Shows confidence, last studied date, and estimated time

### Viewing Analytics

The Analytics page shows:
- Total topics, sessions, and time spent
- Study streak information
- Distribution charts by category
- Topics grouped by confidence level
- Recent practice activity

### Managing Settings

In Settings, you can:
- Set daily study hours limit
- Configure weekly goals per category
- Choose week start day (Monday or Sunday)
- Export/Import data
- Create backups
- Reset all data (with confirmation)

## Revision Suggestion Algorithm

Topics are prioritized using a weighted scoring system:

```
Priority Score = (Difficulty Weight) × (Confidence Weight) × (Recency Weight)
```

Where:
- **Difficulty Weight:** Easy = 1.0, Medium = 1.5, Hard = 2.0
- **Confidence Weight:** (11 - confidence) / 10
- **Recency Weight:**
  - 0-1 days: 0.3
  - 2-3 days: 0.6
  - 4-7 days: 1.0
  - 8-14 days: 1.5
  - 15-30 days: 2.0
  - 31+ days: 2.5

Higher scores indicate topics that need more attention.

## Troubleshooting

### Backend won't start
- Ensure Java 17+ is installed: `java -version`
- Check if port 8080 is available
- Verify Maven is installed: `mvn -version`
- Check backend.log for errors

### Frontend won't start
- Ensure Node.js is installed: `node -version`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Check if port 3000 is available
- Check frontend.log for errors

### Database issues
- Check if ~/interview-tracker/data directory exists
- Verify H2 database file permissions
- Access H2 console to inspect database

### File upload issues
- Check ~/interview-tracker/uploads directory permissions
- Verify file size is under 50MB
- Ensure file type is allowed

## Development

### Building for Production

#### Backend
```bash
cd backend
mvn clean package
java -jar target/interview-tracker-backend-1.0.0.jar
```

#### Frontend
```bash
cd frontend
npm run build
npm run preview
```

### Running Tests

#### Backend
```bash
cd backend
mvn test
```

#### Frontend
```bash
cd frontend
npm run test
```

## Future Enhancements (Phase 2 & 3)

- Spaced repetition algorithm integration
- Company-specific interview tracking
- Collaborative features (share topics with peers)
- Mobile responsive design improvements
- Export analytics as PDF
- Custom tags and filters
- Search functionality
- Interview scheduling and reminders

## Contributing

This is a personal project, but suggestions and feedback are welcome!

## License

This project is for personal use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review application logs (backend.log, frontend.log)
3. Check H2 console for database issues
4. Verify all prerequisites are correctly installed

---

**Built with ❤️ for interview preparation success!**

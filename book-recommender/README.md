# 📚 Intelligent Personal Book Recommender System

A sophisticated, AI-powered book recommendation application that runs locally and evolves with your reading journey. Built with React, FastAPI, and Claude AI.

## 🌟 Features

### Smart Book Recommendations
- **AI-Powered**: Uses Claude API to generate personalized recommendations based on your reading history
- **Genre-Based**: Browse recommendations across 12+ genres (Fiction, Non-Fiction, etc.)
- **Intelligent Matching**: Analyzes themes, writing style, pacing, and complexity
- **Adaptive Learning**: Adjusts recommendations based on your ratings and reading patterns

### Library Integration
- **Sno-Isle Libraries**: Automatically checks book availability at Sno-Isle Libraries
- **Format Detection**: Shows available formats (Physical, Digital/PDF, Audiobook)
- **Direct Catalog Links**: One-click access to library catalog

### Reading Tracking
- Track books with statuses: To Read, Currently Reading, Completed, Did Not Finish
- Log reading duration, format used, and personal notes
- Rate books (1-5 stars)
- AI-generated summaries for completed books

### Analytics Dashboard
- Reading statistics (books per year, pages read, reading speed)
- Reading streak tracking
- Genre distribution with visualizations
- Monthly reading trends
- Top-rated books
- Reading pattern analysis

## 🛠️ Technology Stack

### Backend
- **Python 3.8+**
- **FastAPI** - Modern web framework
- **SQLite** - Lightweight local database
- **Anthropic Claude API** - AI-powered recommendations
- **httpx** - Async HTTP client
- **BeautifulSoup4** - Web scraping for library integration

### Frontend
- **React** with **TypeScript**
- **React Router** - Navigation
- **Axios** - API client
- **Recharts** - Data visualization

### APIs Used
- **Open Library API** - Free book data
- **Google Books API** - Free book data
- **Sno-Isle Libraries** - Library catalog integration

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 14+ and npm
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd book-recommender/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

5. **Run the backend**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   API documentation at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd book-recommender/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env if needed (default: http://localhost:8000/api)
   ```

4. **Run the frontend**
   ```bash
   npm start
   ```

   The app will open at `http://localhost:3000`

## 🚀 Usage

### Getting Started

1. **Launch both backend and frontend** (in separate terminals)

   Backend:
   ```bash
   cd backend
   source venv/bin/activate
   python -m uvicorn app.main:app --reload
   ```

   Frontend:
   ```bash
   cd frontend
   npm start
   ```

2. **Visit** `http://localhost:3000` in your browser

### Workflow

1. **Browse Recommendations**
   - Click on any genre on the homepage to see personalized recommendations
   - Each recommendation includes AI-generated reasoning
   - Check Sno-Isle library availability instantly

2. **Start Reading**
   - Click "Start Reading" on any book to add it to your reading list
   - Track your progress in "My Books"

3. **Mark as Completed**
   - When finished, mark the book as completed
   - Rate it and add personal notes
   - AI will generate a summary automatically

4. **View Analytics**
   - Visit the Dashboard to see your reading statistics
   - Analyze reading patterns and trends
   - Get AI-powered insights

## 📁 Project Structure

```
book-recommender/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py          # API endpoints
│   │   ├── database/
│   │   │   ├── database.py        # DB connection
│   │   │   └── schema.sql         # Database schema
│   │   ├── models/
│   │   │   ├── book.py            # Book models
│   │   │   └── stats.py           # Statistics models
│   │   ├── services/
│   │   │   ├── book_api.py        # External book APIs
│   │   │   ├── book_service.py    # Book CRUD operations
│   │   │   ├── recommendation_engine.py  # AI recommendations
│   │   │   ├── library_checker.py # Library integration
│   │   │   └── analytics_service.py # Analytics
│   │   └── main.py                # FastAPI app
│   ├── data/                      # SQLite database (auto-created)
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── BookCard.tsx       # Book display component
│   │   │   └── GenreSection.tsx   # Genre section component
│   │   ├── pages/
│   │   │   ├── HomePage.tsx       # Main page with recommendations
│   │   │   ├── MyBooksPage.tsx    # Reading tracking
│   │   │   └── DashboardPage.tsx  # Analytics dashboard
│   │   ├── services/
│   │   │   └── api.ts             # API client
│   │   ├── styles/
│   │   │   ├── HomePage.css
│   │   │   ├── DashboardPage.css
│   │   │   └── MyBooksPage.css
│   │   ├── App.tsx                # Main app with routing
│   │   └── App.css                # Global styles
│   ├── package.json
│   └── .env.example
│
└── README.md
```

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```env
ANTHROPIC_API_KEY=your_api_key_here  # Required for AI features
SNOISLE_LIBRARY_CARD=your_card       # Optional
```

**Frontend (.env)**
```env
REACT_APP_API_URL=http://localhost:8000/api
```

### Database

The SQLite database is automatically created on first run at:
```
backend/data/book_recommender.db
```

To reset the database, simply delete this file and restart the backend.

## 📊 API Endpoints

### Books
- `GET /api/books` - List all books
- `GET /api/books/{id}` - Get book details
- `POST /api/books` - Create book
- `GET /api/books/external/search?q=query` - Search external APIs
- `GET /api/books/{id}/library-availability` - Check library availability

### Reading Logs
- `GET /api/reading-logs?status=reading` - Get reading logs
- `POST /api/reading-logs` - Create reading log
- `PATCH /api/reading-logs/{id}` - Update reading log
- `POST /api/books/{id}/start-reading` - Start reading book
- `POST /api/reading-logs/{id}/complete` - Mark book completed

### Recommendations
- `GET /api/recommendations/{genre}?count=3` - Get AI recommendations

### Analytics
- `GET /api/analytics/dashboard` - Dashboard statistics
- `GET /api/analytics/genre-stats` - Genre statistics
- `GET /api/analytics/reading-patterns` - Reading patterns
- `GET /api/analytics/ai-insights` - AI-powered insights

## 🎯 Development Phases

### Phase 1 (MVP) ✅
- [x] Basic homepage with genre recommendations
- [x] Book tracking (CRUD operations)
- [x] Simple dashboard with basic stats
- [x] Sno-Isle availability check

### Phase 2 ✅
- [x] AI-powered recommendations (rating-based)
- [x] Advanced analytics dashboard
- [x] Reading speed tracking

### Phase 3 (Future)
- [ ] Surprise/discovery section
- [ ] Trending books integration (Goodreads, Reddit)
- [ ] Advanced filtering
- [ ] Export features (CSV, PDF reports)
- [ ] Reading goals and challenges
- [ ] Book club integration

## 🤝 Contributing

This is a personal project, but suggestions are welcome! Feel free to open issues for:
- Bug reports
- Feature requests
- Improvement suggestions

## 📝 License

MIT License - feel free to use this for your own reading journey!

## 🙏 Acknowledgments

- **Claude AI** by Anthropic for intelligent recommendations
- **Open Library** and **Google Books** for free book data
- **Sno-Isle Libraries** for community access to books

## 💡 Tips for Best Experience

1. **Start with ratings**: Rate a few books you've already read to improve recommendations
2. **Be honest**: The AI learns from your ratings - honest feedback = better recommendations
3. **Explore genres**: Try recommendations from different genres to expand your reading
4. **Use library integration**: Save money by checking library availability first
5. **Track consistently**: Regular tracking helps build meaningful statistics

## 🐛 Troubleshooting

### Backend won't start
- Ensure Python 3.8+ is installed
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify ANTHROPIC_API_KEY is set in `.env`

### Frontend won't start
- Ensure Node.js 14+ is installed
- Delete `node_modules` and `package-lock.json`, then run `npm install` again
- Check that backend is running at `http://localhost:8000`

### AI features not working
- Verify your ANTHROPIC_API_KEY is valid
- Check backend logs for API errors
- Ensure you have API credits available

### Library availability always shows unavailable
- This is expected if the book isn't at Sno-Isle Libraries
- Web scraping may occasionally fail - this is normal

---

**Happy Reading! 📚✨**

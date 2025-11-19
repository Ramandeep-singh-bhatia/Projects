# AI-Powered English Learning Application

A comprehensive, AI-powered English learning application designed to help non-native speakers improve their speaking and writing skills through interactive, contextual learning.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![React](https://img.shields.io/badge/React-18.2.0-61dafb.svg)
![Node](https://img.shields.io/badge/node-%3E%3D16.0.0-green.svg)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Application Structure](#application-structure)
- [Learning Modules](#learning-modules)
- [AI Integration](#ai-integration)
- [Data Storage](#data-storage)
- [Usage Guide](#usage-guide)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

This application addresses the common challenges faced by non-native English speakers:
- Forgetting vocabulary in specific contexts
- Struggling to find the right words
- Lack of practice with real conversational situations
- Need for personalized, adaptive learning

### Core Philosophy

- **Contextual Learning**: Learn words and phrases in realistic situations
- **Adaptive Difficulty**: Content adjusts to your proficiency level
- **Immediate Feedback**: AI-powered evaluation and suggestions
- **Spaced Repetition**: Smart review system for long-term retention
- **Practical Focus**: Real-world scenarios over theoretical grammar

## Features

### 🎯 Adaptive Learning System
- Baseline assessment to gauge current level
- Intelligently adapts difficulty based on performance
- Tracks weak areas and creates targeted exercises
- Spaced repetition for vocabulary retention

### 💬 Interactive Learning Modules

#### 1. Conversation Practice
- Role-play scenarios (ordering food, job interviews, business meetings)
- Real-time AI conversation partner
- Contextual feedback on vocabulary and phrasing
- Speech-to-text support for pronunciation practice

#### 2. Vocabulary Builder
- Learn words through actual usage scenarios
- Context-based exercises
- Progressive difficulty levels
- Mastery tracking with review scheduling

#### 3. Grammar Practice
- Interactive grammar exercises
- Immediate feedback with explanations
- Common mistake pattern detection
- Practical usage examples

#### 4. Writing Tasks
- Daily/weekly writing prompts
- AI analysis for grammar, vocabulary, clarity, and flow
- Detailed improvement suggestions
- Track writing quality over time

#### 5. Small Talk Mastery
- Casual conversation scenarios
- Conversation starters and responses
- Idiomatic expressions
- Cultural tips for natural conversation

#### 6. Weekly Challenges
- Gamified learning challenges
- Creative writing and debate topics
- Achievement system
- Streak tracking for motivation

### 📊 Intelligent Dashboard
- Overall proficiency score (0-100)
- Skill breakdown: Vocabulary, Grammar, Fluency, Context Usage, Writing
- Week-over-week improvement graphs
- Recent activity tracking
- Streak counter

### 📈 Progress Tracking
- Detailed performance analytics
- Visual progress indicators
- Common mistakes journal
- Recommended focus areas

### 🔄 Smart Review System
- Automatic review scheduling based on mastery
- Spaced repetition algorithm
- Quick 5-minute review sessions
- Mistakes journal with explanations

## Technology Stack

### Frontend
- **React 18.2.0** - UI framework
- **React Router 6.20** - Navigation
- **Zustand 4.4.7** - State management
- **Recharts 2.10** - Data visualization
- **Lucide React** - Icons
- **Vite 5.0** - Build tool

### AI Integration
- **Claude API** (Anthropic) - Cloud AI service
- **Ollama** - Local AI models support (llama3, mistral, etc.)
- **Web Speech API** - Browser-based speech recognition

### Data Storage
- **Better-SQLite3** - Local database (Node.js environment)
- **LocalStorage** - Browser-based persistence (web environment)

## Prerequisites

- **Node.js** >= 16.0.0
- **npm** or **yarn**
- (Optional) **Ollama** for local AI models
- (Optional) **Anthropic API Key** for Claude API

## Installation

1. **Clone or navigate to the repository**
   ```bash
   cd ai-english-learning-app
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Initialize the database** (optional, for Node.js environment)
   ```bash
   npm run init-db
   ```

## Configuration

### AI Service Setup

You have two options for AI integration:

#### Option 1: Claude API (Recommended for best quality)

1. Get an API key from [Anthropic Console](https://console.anthropic.com)
2. Create a `.env` file in the root directory:
   ```env
   VITE_ANTHROPIC_API_KEY=your_api_key_here
   ```
3. Alternatively, enter the API key in the Settings panel within the app

#### Option 2: Local AI with Ollama (Free, runs locally)

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull a model:
   ```bash
   ollama pull llama3
   ```
3. Start Ollama service:
   ```bash
   ollama serve
   ```
4. In the app Settings, enable "Use Local Model"

## Running the Application

### Development Mode

```bash
npm run dev
```

The application will open at `http://localhost:3000`

### Production Build

```bash
npm run build
npm run preview
```

## Application Structure

```
ai-english-learning-app/
├── public/                 # Static assets
├── src/
│   ├── components/
│   │   ├── Assessment/    # Baseline assessment
│   │   ├── Common/        # Navigation, Settings
│   │   ├── Dashboard/     # Main dashboard
│   │   ├── Learning/      # All learning modules
│   │   └── Review/        # Review and mistakes journal
│   ├── services/
│   │   ├── aiService.js   # AI integration
│   │   └── database.js    # Data persistence
│   ├── stores/
│   │   └── appStore.js    # Zustand state management
│   ├── styles/
│   │   └── global.css     # Global styles
│   ├── App.jsx            # Main application component
│   └── main.jsx           # Entry point
├── database/
│   └── init-db.js         # Database initialization
├── package.json
└── vite.config.js
```

## Learning Modules

### Conversation Practice
Practice real-world conversations with scenarios like:
- Ordering at a restaurant
- Job interviews
- Small talk at coffee shops
- Business meetings
- Shopping
- Doctor's office visits

**Features:**
- AI conversation partner responds naturally
- Speech-to-text input support
- Contextual feedback on appropriateness and vocabulary
- Alternative phrasing suggestions

### Vocabulary Practice
Learn vocabulary through context:
- Situation-based exercises
- Word definitions with examples
- Usage in realistic scenarios
- Progressive difficulty

### Grammar Practice
Master English grammar:
- Interactive exercises
- Sentence correction
- Rule explanations
- Immediate feedback

### Writing Practice
Improve writing skills:
- Various prompt categories (personal, professional, academic, creative)
- Detailed AI analysis
- Grammar and vocabulary feedback
- Style and clarity suggestions
- Corrected versions with explanations

### Small Talk Mastery
Master casual conversation:
- Common social situations
- Conversation starters
- Appropriate responses
- Useful phrases and expressions
- Cultural tips

### Weekly Challenges
Fun, gamified challenges:
- Creative writing prompts
- Debate topics
- Vocabulary challenges
- Achievement tracking

## AI Integration

### How AI Evaluation Works

The application uses AI to:
1. **Assess your level** - Analyze baseline assessment responses
2. **Evaluate responses** - Score appropriateness, grammar, vocabulary
3. **Provide feedback** - Offer specific, actionable suggestions
4. **Generate exercises** - Create personalized practice content
5. **Track patterns** - Identify common mistakes and weak areas

### AI Service Configuration

The `aiService.js` handles all AI interactions:
- Automatic fallback to default responses if AI is unavailable
- Caching for improved performance
- Error handling and retry logic
- Support for both cloud and local models

## Data Storage

### Browser Environment
All data is stored in **localStorage**:
- User profile and settings
- Learning progress
- Exercise history
- Vocabulary mastery
- Mistakes journal

### Node.js Environment
Data is stored in **SQLite database**:
- Structured relational data
- Better performance for large datasets
- Query capabilities
- Data integrity

### Data Persistence
- Progress is automatically saved
- Export/import functionality for backups
- Reset option to start fresh

## Usage Guide

### First Time Setup

1. **Launch the application**
2. **Configure AI service** in Settings (Claude API or Ollama)
3. **Complete baseline assessment** (8 questions)
4. **Review your results** and personalized learning path
5. **Start practicing** with any module

### Daily Practice Routine

1. **Check dashboard** for progress overview
2. **Choose a module** based on recommended focus areas
3. **Complete exercises** (aim for your daily goal)
4. **Review feedback** and learn from mistakes
5. **Track your streak** and celebrate improvements

### Weekly Workflow

1. **Attempt weekly challenge** for a fun test
2. **Review mistakes journal** to learn from errors
3. **Check progress analytics** to see improvement
4. **Adjust focus areas** based on performance

## Development

### Project Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Lint code
npm run init-db      # Initialize database
```

### Adding New Features

1. Create component in appropriate directory
2. Add routing in `App.jsx` if needed
3. Update state management in `appStore.js`
4. Integrate with AI service if needed
5. Add styles following existing patterns

### Code Style

- Use functional components with hooks
- Follow existing component structure
- Use CSS custom properties for theming
- Keep components focused and reusable
- Add comments for complex logic

## Troubleshooting

### Common Issues

**Issue: AI service not working**
- Check API key is correctly set
- For Ollama, ensure service is running: `ollama serve`
- Check browser console for errors
- Try using default/fallback responses

**Issue: Speech recognition not working**
- Speech API only works in Chrome/Edge
- Requires HTTPS (or localhost)
- Check microphone permissions
- Browser must support Web Speech API

**Issue: Data not persisting**
- Check browser localStorage is enabled
- Clear cache and reload if issues persist
- Use export/import to backup data

**Issue: Slow performance**
- Reduce AI API calls by using local model
- Clear old exercise history
- Check network connection for API calls

### Browser Compatibility

- **Chrome/Edge**: Full support including speech recognition
- **Firefox**: Full support except speech recognition
- **Safari**: Most features supported
- **Mobile browsers**: Responsive design, limited speech support

## Performance Tips

1. **Use local AI models** (Ollama) for faster responses
2. **Practice offline** - Most features work without internet
3. **Regular reviews** - Better than cramming
4. **Set realistic daily goals** - Consistency over intensity
5. **Export progress regularly** - Backup your data

## Privacy & Security

- All data stored locally (no external database)
- API keys stored in browser localStorage
- No data collection or analytics
- Optional data export for portability
- Reset feature to clear all data

## Future Enhancements

Potential features for future versions:
- [ ] Pronunciation scoring with audio analysis
- [ ] Group challenges and competitions
- [ ] Video-based learning scenarios
- [ ] Custom vocabulary lists
- [ ] Integration with language learning APIs
- [ ] Mobile app versions (React Native)
- [ ] Offline AI model support
- [ ] Multi-language support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Anthropic** for Claude API
- **Ollama** for local AI model support
- **React** community for excellent tools and libraries
- All contributors and testers

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

**Happy Learning! 🎓✨**

Remember: Consistency is key. Practice a little every day, and you'll see amazing progress in your English skills!

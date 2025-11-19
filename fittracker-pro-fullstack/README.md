# FitTracker Pro - Full Stack Application

A comprehensive fitness tracking application with a Spring Boot backend and React TypeScript frontend. Track your workouts, nutrition, monitor progress, and achieve your fitness goals.

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Development](#development)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

FitTracker Pro is a full-stack fitness tracking application that helps users monitor their nutrition, workouts, and progress. Built with modern technologies and best practices, it provides a seamless experience for fitness enthusiasts.

### Key Capabilities

- **User Management**: Secure authentication with JWT tokens
- **Nutrition Tracking**: Log meals, track macros, and monitor calorie intake
- **Workout Tracking**: Create workouts, track exercises, sets, and reps
- **Analytics**: Visualize progress with charts and statistics
- **Profile Management**: Customize goals, track body metrics
- **Settings**: Personalize preferences and notifications

## ✨ Features

### Authentication & Authorization
- JWT-based authentication
- Secure password encryption with BCrypt
- Token refresh mechanism
- Role-based access control

### Nutrition Management
- Meal logging with detailed nutritional information
- Food database with 500+ pre-loaded items
- Daily and weekly nutrition summaries
- Macro tracking (protein, carbs, fats, fiber)
- Calorie goal monitoring

### Workout Management
- Custom workout creation
- Exercise library with 100+ exercises
- Set, rep, and weight tracking
- Workout history and statistics
- Progress tracking over time

### Analytics & Reports
- Weekly calorie trends
- Macro distribution charts
- Workout frequency analysis
- Body weight progression
- Custom date range reports

### User Profile
- Personal information management
- Body metrics tracking (weight, height, BMI)
- Fitness goal setting
- Activity level configuration
- Progress photos (future enhancement)

## 🛠 Technology Stack

### Backend
- **Framework**: Spring Boot 3.2.0
- **Language**: Java 17
- **Database**: PostgreSQL 15
- **Security**: Spring Security with JWT
- **ORM**: Hibernate/JPA
- **Validation**: Bean Validation API
- **Testing**: JUnit 5, Mockito
- **Build Tool**: Maven

### Frontend
- **Framework**: React 18+
- **Language**: TypeScript
- **State Management**: Redux Toolkit
- **Routing**: React Router v6
- **UI Library**: Material-UI v7
- **Charts**: Recharts
- **Forms**: React Hook Form + Zod
- **HTTP Client**: Axios
- **Build Tool**: Vite

### DevOps & Tools
- **Version Control**: Git
- **CI/CD**: GitHub Actions (optional)
- **Containerization**: Docker & Docker Compose
- **API Documentation**: Swagger/OpenAPI

## 📁 Project Structure

```
fittracker-pro-fullstack/
├── backend/                    # Spring Boot backend
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/
│   │   │   │   └── com/ram/fittrackerpro/
│   │   │   │       ├── config/         # Security, CORS, etc.
│   │   │   │       ├── controller/     # REST API endpoints
│   │   │   │       ├── dto/            # Data Transfer Objects
│   │   │   │       ├── entity/         # JPA entities
│   │   │   │       ├── enums/          # Enumerations
│   │   │   │       ├── exception/      # Custom exceptions
│   │   │   │       ├── repository/     # Data access layer
│   │   │   │       ├── security/       # JWT, authentication
│   │   │   │       ├── service/        # Business logic
│   │   │   │       └── util/           # Helper utilities
│   │   │   └── resources/
│   │   │       ├── application.properties
│   │   │       └── data.sql           # Sample data
│   │   └── test/                      # Unit & integration tests
│   ├── pom.xml                        # Maven dependencies
│   └── README.md                      # Backend documentation
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── api/               # API service layer
│   │   ├── components/        # Reusable components
│   │   ├── features/          # Redux slices
│   │   ├── pages/             # Page components
│   │   ├── store/             # Redux store
│   │   ├── types/             # TypeScript definitions
│   │   ├── App.tsx            # Main app component
│   │   └── main.tsx           # Entry point
│   ├── public/                # Static assets
│   ├── package.json           # NPM dependencies
│   ├── tsconfig.json          # TypeScript config
│   ├── vite.config.ts         # Vite configuration
│   └── README.md              # Frontend documentation
│
├── docker-compose.yml         # Docker orchestration
├── .gitignore                 # Git ignore rules
├── LICENSE                    # MIT License
└── README.md                  # This file
```

## 🚀 Getting Started

### Prerequisites

- **Java 17** or higher
- **Node.js 18+** and npm
- **PostgreSQL 15** or higher
- **Maven 3.8+**
- **Git**

### Quick Start (Development)

1. **Clone the repository**
```bash
git clone <repository-url>
cd fittracker-pro-fullstack
```

2. **Set up the database**
```bash
# Create PostgreSQL database
createdb fittracker_db

# Or using psql
psql -U postgres
CREATE DATABASE fittracker_db;
```

3. **Start the backend**
```bash
cd backend
mvn clean install
mvn spring-boot:run

# Backend will run on http://localhost:8080
```

4. **Start the frontend**
```bash
cd frontend
npm install
npm run dev

# Frontend will run on http://localhost:5173
```

5. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8080
- Swagger UI: http://localhost:8080/swagger-ui.html

### Quick Start (Docker)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8080
```

## 💻 Development

### Backend Development

```bash
cd backend

# Run tests
mvn test

# Run with specific profile
mvn spring-boot:run -Dspring-boot.run.profiles=dev

# Build JAR
mvn clean package

# Run JAR
java -jar target/fittracker-pro-0.0.1-SNAPSHOT.jar
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linting
npm run lint
```

### Database Migrations

The application uses JPA with Hibernate for database management. On first run:
- Tables are auto-created based on entities
- Sample data is loaded from `src/main/resources/data.sql`

## 🐳 Docker Deployment

### Build Images

```bash
# Build backend image
cd backend
docker build -t fittracker-backend .

# Build frontend image
cd frontend
docker build -t fittracker-frontend .
```

### Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 📚 API Documentation

### Authentication Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile
- `PUT /api/auth/change-password` - Change password

### Nutrition Endpoints

- `GET /api/meals/date/{date}` - Get meals by date
- `POST /api/meals` - Create a new meal
- `PUT /api/meals/{id}` - Update meal
- `DELETE /api/meals/{id}` - Delete meal
- `GET /api/nutrition/summary/daily/{date}` - Daily nutrition summary
- `GET /api/nutrition/summary/weekly` - Weekly nutrition summary

### Workout Endpoints

- `GET /api/workouts/date/{date}` - Get workouts by date
- `POST /api/workouts` - Create a new workout
- `PUT /api/workouts/{id}/complete` - Complete workout
- `DELETE /api/workouts/{id}` - Delete workout
- `GET /api/exercises/search` - Search exercises

For complete API documentation, visit: http://localhost:8080/swagger-ui.html

## 🧪 Testing

### Backend Tests

```bash
cd backend
mvn test                    # Run all tests
mvn test -Dtest=ClassNameTest  # Run specific test
```

### Frontend Tests

```bash
cd frontend
npm test                    # Run all tests
npm run test:coverage      # Run with coverage
```

## 📝 Environment Variables

### Backend (.env or application.properties)

```properties
# Database
spring.datasource.url=jdbc:postgresql://localhost:5432/fittracker_db
spring.datasource.username=postgres
spring.datasource.password=your_password

# JWT
jwt.secret=your-secret-key
jwt.expiration=86400000

# Server
server.port=8080
```

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8080
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Coding Standards

- **Backend**: Follow Java coding conventions, use meaningful variable names
- **Frontend**: Follow TypeScript/React best practices, use ESLint
- **Git**: Write clear commit messages, reference issues when applicable
- **Testing**: Write tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Ramandeep Singh Bhatia** - Initial work

## 🙏 Acknowledgments

- Spring Boot team for the excellent framework
- React team for the powerful UI library
- Material-UI for the beautiful component library
- All contributors and users of FitTracker Pro

## 📞 Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Email: support@fittrackerpro.com (if applicable)

## 🗺 Roadmap

### Upcoming Features

- [ ] Mobile app (React Native)
- [ ] Social features (friend challenges, leaderboards)
- [ ] Meal planning and recipes
- [ ] Workout program templates
- [ ] Integration with fitness trackers (Fitbit, Apple Watch)
- [ ] AI-powered recommendations
- [ ] Progress photos and body measurements
- [ ] Nutritionist/trainer collaboration features

### Version History

- **v1.0.0** (Current) - Initial release with core features
  - User authentication
  - Nutrition tracking
  - Workout tracking
  - Analytics and reports
  - Profile management
  - Settings and preferences

---

**Built with ❤️ for fitness enthusiasts**

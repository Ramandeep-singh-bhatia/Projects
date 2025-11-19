# FitTracker Pro - Frontend

A comprehensive fitness tracking application built with React, TypeScript, and Material-UI. Track your workouts, nutrition, and analyze your progress all in one place.

## Features

### Authentication & User Management
- Secure JWT-based authentication
- User registration with comprehensive profile setup
- Login with "Remember Me" functionality
- Profile management and editing
- Secure password change
- Private routes protection

### Dashboard
- Quick stats overview (calories, workouts, weight, BMI)
- Weekly progress visualization
- Recent activity feed
- Quick action buttons for common tasks

### Nutrition Tracking
- Meal logging with detailed nutritional information
- Food item search from comprehensive database
- Daily nutrition summary with macro tracking
- Visual progress bars for calories and macros
- Meal history by date
- Food serving size customization

### Workout Tracking
- Workout creation with exercise selection
- Exercise search and database
- Set, rep, and weight tracking
- Workout completion and status management
- Workout history and statistics
- Calories burned estimation

### Analytics & Progress
- Weekly calorie consumption trends
- Macro distribution pie charts
- Workout breakdown by type
- Summary statistics (avg calories, total workouts, calories burned)
- Historical data visualization

### Settings & Preferences
- Notification preferences (email, push, reminders)
- Theme customization (light, dark, auto)
- Language selection
- Date format preferences
- Unit system selection (metric/imperial)
- Data export functionality
- Account management

## Technology Stack

- **React** 18+ - UI library
- **TypeScript** - Type safety and better DX
- **Redux Toolkit** - State management
- **React Router** v6 - Client-side routing
- **Material-UI** v7 - Component library
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **React Hook Form** - Form management
- **Zod** - Schema validation
- **Vite** - Build tool and dev server

## Project Structure

```
fittracker-frontend/
├── public/              # Static assets
├── src/
│   ├── api/            # API services and axios configuration
│   │   ├── axios-config.ts
│   │   ├── auth.service.ts
│   │   ├── nutrition.service.ts
│   │   └── workout.service.ts
│   ├── components/     # Reusable components
│   │   ├── auth/       # Authentication components
│   │   ├── dashboard/  # Dashboard-specific components
│   │   ├── layout/     # Layout components (Header, Sidebar, MainLayout)
│   │   ├── nutrition/  # Nutrition tracking components
│   │   └── workouts/   # Workout tracking components
│   ├── features/       # Redux slices
│   │   ├── auth/       # Auth slice
│   │   ├── nutrition/  # Nutrition slice
│   │   └── workout/    # Workout slice
│   ├── pages/          # Page components
│   │   ├── analytics/  # Analytics page
│   │   ├── auth/       # Login & Register pages
│   │   ├── dashboard/  # Dashboard page
│   │   ├── nutrition/  # Nutrition tracking page
│   │   ├── profile/    # Profile pages (view, edit, change password)
│   │   ├── settings/   # Settings page
│   │   └── workouts/   # Workout tracking page
│   ├── store/          # Redux store configuration
│   ├── types/          # TypeScript type definitions
│   ├── App.tsx         # Main app component with routing
│   └── main.tsx        # Application entry point
├── .env.development    # Development environment variables
├── .env.production     # Production environment variables
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8080`

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd fittracker-frontend
```

2. Install dependencies
```bash
npm install
```

3. Configure environment variables
```bash
# .env.development already configured for local development
VITE_API_BASE_URL=http://localhost:8080
```

### Development

Run the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Build

Create a production build:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## API Integration

The frontend integrates with the FitTracker Pro backend API. All API calls are handled through service modules in `/src/api/`:

- **Auth Service**: Authentication, registration, token management
- **Nutrition Service**: Meals, food items, nutrition summaries
- **Workout Service**: Workouts, exercises, workout completion

### JWT Token Management

- Automatic token attachment to requests via Axios interceptors
- Token refresh on 401 errors
- Automatic logout and redirect on token expiration
- Token persistence in localStorage

## State Management

The application uses Redux Toolkit for centralized state management:

- **Auth Slice**: User authentication, profile data, token management
- **Nutrition Slice**: Meals, daily summaries, weekly summaries
- **Workout Slice**: Workouts, exercises, workout status

### Async Thunks

All API calls use Redux Toolkit's `createAsyncThunk` for standardized async operations with loading/error states.

## Routing

React Router v6 handles all routing with:

- Public routes: `/login`, `/register`
- Private routes: All other routes (protected by `PrivateRoute` component)
- Automatic redirect to login for unauthenticated users
- Return URL preservation for seamless login flow

## Form Validation

Forms use React Hook Form with Zod schema validation:

- Type-safe validation schemas
- Real-time validation feedback
- Custom validation rules (password strength, age verification, etc.)
- Accessible error messages

## Responsive Design

- Mobile-first approach
- Material-UI breakpoints for responsive layouts
- Drawer navigation for mobile
- Responsive charts and data visualizations
- Optimized for desktop, tablet, and mobile devices

## Key Components

### Layout Components

- **MainLayout**: Main application layout with header and sidebar
- **Header**: Top navigation with user menu
- **Sidebar**: Left navigation menu
- **PrivateRoute**: Route protection wrapper

### Feature Components

- **AddMealDialog**: Modal for adding meals with food search
- **AddWorkoutDialog**: Modal for creating workouts with exercise selection
- **NutritionSummaryCard**: Daily nutrition overview
- **MealCard**: Individual meal display
- **WeeklyProgressChart**: Calorie trends visualization

## Error Handling

- Axios interceptors for global error handling
- Automatic token refresh on 401 errors
- User-friendly error messages
- Loading states for all async operations
- Empty states for no data scenarios

## Performance Optimizations

- React.memo for component memoization
- useMemo for expensive calculations
- Lazy loading for route-based code splitting (potential)
- Optimized bundle size with Vite
- Efficient state updates with Redux Toolkit

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development Guidelines

### Code Style

- TypeScript strict mode enabled
- ESLint for code quality
- Consistent naming conventions (camelCase for variables, PascalCase for components)
- Type-safe imports with `import type` for type-only imports

### Component Structure

- Functional components with hooks
- Props interfaces defined with TypeScript
- Clear separation of concerns (presentation vs. logic)
- Reusable components in `/components`
- Page-specific components in `/pages`

### State Management Best Practices

- Centralized state in Redux for shared data
- Local state with useState for component-specific data
- Async thunks for all API calls
- Selectors for computed state

## Testing

Testing infrastructure can be added with:
- Vitest for unit tests
- React Testing Library for component tests
- MSW for API mocking

## Deployment

The application can be deployed to any static hosting service:

- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages

Build the production bundle:
```bash
npm run build
```

The `dist/` directory will contain the optimized production build.

## Environment Variables

- `VITE_API_BASE_URL`: Backend API base URL (default: http://localhost:8080)

## Known Issues & Future Enhancements

### Potential Improvements

- WebSocket integration for real-time updates
- PWA support for offline functionality
- Dark mode implementation
- Internationalization (i18n)
- Unit and integration tests
- Code splitting for better performance
- Error boundary implementation
- Accessibility improvements (ARIA labels, keyboard navigation)
- Advanced analytics (goal tracking, progress predictions)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

- Material-UI for the comprehensive component library
- Redux Toolkit for simplified Redux development
- Recharts for beautiful data visualizations
- Vite for blazing-fast development experience

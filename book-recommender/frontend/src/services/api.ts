/**
 * API service for interacting with the backend.
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Book {
  id: number;
  title: string;
  author: string;
  isbn?: string;
  genre: string;
  page_count?: number;
  cover_url?: string;
  description?: string;
  publication_year?: number;
  snoisle_available: boolean;
  format_available?: string;
}

export interface ReadingLog {
  id: number;
  book_id: number;
  status: 'to_read' | 'reading' | 'completed' | 'dnf';
  date_added: string;
  date_started?: string;
  date_completed?: string;
  rating?: number;
  reading_duration_days?: number;
  format_used?: string;
  personal_notes?: string;
  ai_summary?: string;
}

export interface Recommendation {
  title: string;
  author: string;
  isbn?: string;
  publication_year?: number;
  page_count?: number;
  reason: string;
  score: number;
  tags: string[];
  book_id?: number;
  library_availability?: LibraryAvailability;
  cover_url?: string;
  description?: string;
}

export interface LibraryAvailability {
  available: boolean;
  is_available_now: boolean;
  formats: string[];
  catalog_url?: string;
  library_system: string;
}

export interface DashboardStats {
  books_read_year: number;
  books_read_all_time: number;
  pages_read_total: number;
  average_reading_speed: number;
  completion_rate: number;
  current_streak_days: number;
  books_this_month: number;
  genre_distribution: Record<string, number>;
  monthly_trends: Array<{
    month: number;
    books_completed: number;
    pages_read: number;
    avg_rating: number;
  }>;
  top_rated_books: any[];
  currently_reading: any[];
  active_goals: any[];
}

// Book endpoints
export const searchExternalBooks = (query: string, limit: number = 10) =>
  api.get('/books/external/search', { params: { q: query, limit } });

export const getBooks = (query?: string, genre?: string) =>
  api.get('/books', { params: { q: query, genre } });

export const getBook = (bookId: number) =>
  api.get(`/books/${bookId}`);

export const createBook = (bookData: Partial<Book>) =>
  api.post('/books', bookData);

export const checkLibraryAvailability = (bookId: number) =>
  api.get(`/books/${bookId}/library-availability`);

// Reading log endpoints
export const getReadingLogs = (status?: string) =>
  api.get('/reading-logs', { params: { status } });

export const createReadingLog = (logData: Partial<ReadingLog>) =>
  api.post('/reading-logs', logData);

export const updateReadingLog = (logId: number, updateData: Partial<ReadingLog>) =>
  api.patch(`/reading-logs/${logId}`, updateData);

export const startReading = (bookId: number, formatUsed: string = 'Physical') =>
  api.post(`/books/${bookId}/start-reading`, null, { params: { format_used: formatUsed } });

export const markCompleted = (logId: number, rating: number, notes?: string, generateSummary: boolean = true) =>
  api.post(`/reading-logs/${logId}/complete`, null, {
    params: { rating, notes, generate_summary: generateSummary }
  });

// Recommendation endpoints
export const getRecommendations = (genre: string, count: number = 3, refresh: boolean = false) =>
  api.get(`/recommendations/${genre}`, { params: { count, refresh } });

// Analytics endpoints
export const getDashboardStats = (year?: number) =>
  api.get('/analytics/dashboard', { params: { year } });

export const getGenreStats = () =>
  api.get('/analytics/genre-stats');

export const getReadingPatterns = () =>
  api.get('/analytics/reading-patterns');

export const getAIInsights = () =>
  api.get('/analytics/ai-insights');

export default api;

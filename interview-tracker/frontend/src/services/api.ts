import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.message || error.message || 'An error occurred';
    console.error('API Error:', message);
    return Promise.reject(error);
  }
);

export default api;

// Topic Services
export const topicService = {
  getAll: (category: string) => api.get(`/topics/${category}`),
  getById: (category: string, id: number) => api.get(`/topics/${category}/${id}`),
  create: (category: string, topic: any) => api.post(`/topics/${category}`, topic),
  update: (category: string, id: number, topic: any) => api.put(`/topics/${category}/${id}`, topic),
  delete: (category: string, id: number) => api.delete(`/topics/${category}/${id}`),
};

// Practice Session Services
export const sessionService = {
  getByTopicId: (topicId: number) => api.get(`/sessions/topic/${topicId}`),
  create: (topicId: number, session: any) => api.post(`/sessions/topic/${topicId}`, session),
  update: (id: number, session: any) => api.put(`/sessions/${id}`, session),
  delete: (id: number) => api.delete(`/sessions/${id}`),
  getRecent: (limit: number = 10) => api.get(`/sessions/recent?limit=${limit}`),
};

// File Services
export const fileService = {
  upload: (topicId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/files/upload/${topicId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getByTopicId: (topicId: number) => api.get(`/files/topic/${topicId}`),
  download: (id: number) => api.get(`/files/${id}`, { responseType: 'blob' }),
  preview: (id: number) => api.get(`/files/${id}/preview`),
  delete: (id: number) => api.delete(`/files/${id}`),
};

// Dashboard Services
export const dashboardService = {
  getSuggestions: (category?: string, limit: number = 15) => {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    params.append('limit', limit.toString());
    return api.get(`/dashboard/suggestions?${params.toString()}`);
  },
  getWeeklyProgress: () => api.get('/dashboard/weekly/progress'),
  getWeeklyHistory: (weeks: number = 8) => api.get(`/dashboard/weekly/history?weeks=${weeks}`),
};

// Analytics Services
export const analyticsService = {
  getSummary: () => api.get('/analytics/summary'),
  getRecentActivity: (limit: number = 10) => api.get(`/analytics/recent-activity?limit=${limit}`),
};

// Settings Services
export const settingsService = {
  get: () => api.get('/settings'),
  update: (settings: any) => api.put('/settings', settings),
};

// Data Management Services
export const dataService = {
  export: () => api.get('/data/export', { responseType: 'blob' }),
  import: (file: File, merge: boolean = false) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/data/import?merge=${merge}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  reset: () => api.delete('/data/reset'),
  backup: () => api.post('/data/backup'),
  getStorageInfo: () => api.get('/data/storage-info'),
};

// Phase 2: Dependency Services
export const dependencyService = {
  addPrerequisite: (topicId: number, prerequisiteId: number) =>
    api.post(`/dependencies/topics/${topicId}/prerequisites/${prerequisiteId}`),
  removePrerequisite: (topicId: number, prerequisiteId: number) =>
    api.delete(`/dependencies/topics/${topicId}/prerequisites/${prerequisiteId}`),
  getPrerequisites: (topicId: number) => api.get(`/dependencies/topics/${topicId}/prerequisites`),
  getDependents: (topicId: number) => api.get(`/dependencies/topics/${topicId}/dependents`),
  getLearningPath: (topicId: number) => api.get(`/dependencies/topics/${topicId}/learning-path`),
  getBlockedTopics: () => api.get('/dependencies/blocked'),
  validateNonCircular: (topicId: number, prerequisiteId: number) =>
    api.post('/dependencies/validate', { topicId, prerequisiteId }),
  getReadyTopics: () => api.get('/dependencies/ready-topics'),
  getNextLogicalTopic: () => api.get('/dependencies/next-logical-topic'),
  importPrerequisites: (data: any) => api.post('/dependencies/import', data),
};

// Phase 2: Confidence Decay Services
export const confidenceService = {
  applyDecay: () => api.post('/confidence/apply-decay'),
  getHistory: (topicId: number) => api.get(`/confidence/history/${topicId}`),
  getDecayPreview: () => api.get('/confidence/decay-preview'),
};

// Phase 2: Study Plan Services
export const studyPlanService = {
  generate: (params: any) => api.post('/study-plan/generate', params),
  getActive: () => api.get('/study-plan/active'),
  getAll: () => api.get('/study-plan'),
  getById: (id: number) => api.get(`/study-plan/${id}`),
  markItemComplete: (itemId: number, actualMinutes: number) =>
    api.post(`/study-plan/items/${itemId}/complete`, { actualMinutes }),
  delete: (id: number) => api.delete(`/study-plan/${id}`),
};

// Phase 2: Mock Interview Services
export const mockInterviewService = {
  start: (params: any) => api.post('/mock-interview/start', params),
  complete: (id: number, assessment: any) => api.post(`/mock-interview/${id}/complete`, assessment),
  getAll: () => api.get('/mock-interview'),
  getById: (id: number) => api.get(`/mock-interview/${id}`),
  getAnalytics: () => api.get('/mock-interview/analytics'),
  delete: (id: number) => api.delete(`/mock-interview/${id}`),
};

// Phase 2: Pomodoro Services
export const pomodoroService = {
  start: (params: any) => api.post('/pomodoro/start', params),
  getActive: () => api.get('/pomodoro/active'),
  complete: (id: number) => api.post(`/pomodoro/${id}/complete`),
  stop: (id: number) => api.post(`/pomodoro/${id}/stop`),
  logSession: (id: number, data: any) => api.post(`/pomodoro/${id}/log-session`, data),
  getStats: () => api.get('/pomodoro/stats'),
  getHistory: (limit: number = 50) => api.get(`/pomodoro/history?limit=${limit}`),
  getByTopic: (topicId: number) => api.get(`/pomodoro/topic/${topicId}`),
};

// Phase 2: Enhanced Analytics Services
export const enhancedAnalyticsService = {
  get: () => api.get('/analytics/enhanced'),
};

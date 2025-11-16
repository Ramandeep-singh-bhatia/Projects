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

// Phase 3: Flashcard Services
export const flashcardService = {
  create: (flashcard: any) => api.post('/flashcards', flashcard),
  getAll: (activeOnly?: boolean) => api.get(`/flashcards${activeOnly ? '?activeOnly=true' : ''}`),
  getById: (id: number) => api.get(`/flashcards/${id}`),
  update: (id: number, flashcard: any) => api.put(`/flashcards/${id}`, flashcard),
  delete: (id: number) => api.delete(`/flashcards/${id}`),
  archive: (id: number) => api.post(`/flashcards/${id}/archive`),
  getDue: () => api.get('/flashcards/due'),
  getNext: () => api.get('/flashcards/next'),
  submitReview: (id: number, quality: number) => api.post(`/flashcards/${id}/review`, { quality }),
  getByTopic: (topicId: number) => api.get(`/flashcards/by-topic/${topicId}`),
  getByCategory: (category: string) => api.get(`/flashcards/by-category?category=${category}`),
  search: (q: string) => api.get(`/flashcards/search?q=${q}`),
  getAnalytics: () => api.get('/flashcards/analytics'),
  generateFromTopic: (topicId: number) => api.post(`/flashcards/generate/${topicId}`),
  bulkCreate: (flashcards: any[]) => api.post('/flashcards/bulk-create', flashcards),
};

// Phase 3: Calibration Services
export const calibrationService = {
  getPendingTopics: () => api.get('/calibration/pending-topics'),
  trigger: (topicId: number, type: string) => api.post(`/calibration/trigger/${topicId}?type=${type}`),
  complete: (id: number, data: any) => api.post(`/calibration/${id}/complete`, data),
  getPending: () => api.get('/calibration/pending'),
  getHistory: (topicId: number) => api.get(`/calibration/history/${topicId}`),
  getAccuracy: () => api.get('/calibration/accuracy'),
};

// Phase 3: Voice Note Services
export const voiceNoteService = {
  record: (formData: FormData) => api.post('/voice-notes/record', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getById: (id: number) => api.get(`/voice-notes/${id}`),
  getAll: () => api.get('/voice-notes'),
  getByTopic: (topicId: number) => api.get(`/voice-notes/topic/${topicId}`),
  update: (id: number, voiceNote: any) => api.put(`/voice-notes/${id}`, voiceNote),
  delete: (id: number) => api.delete(`/voice-notes/${id}`),
  downloadAudio: (id: number) => api.get(`/voice-notes/${id}/audio`, { responseType: 'blob' }),
  updateTranscription: (id: number, transcription: string) =>
    api.put(`/voice-notes/${id}/transcription`, { transcription }),
  search: (q: string) => api.get(`/voice-notes/search?q=${q}`),
  getAnalytics: () => api.get('/voice-notes/analytics'),
  appendToNotes: (id: number) => api.post(`/voice-notes/${id}/to-notes`),
};

// Phase 3: Backup Services
export const backupService = {
  create: () => api.post('/backup/create'),
  list: () => api.get('/backup/list'),
  download: (fileName: string) => api.get(`/backup/${fileName}/download`, { responseType: 'blob' }),
  delete: (fileName: string) => api.delete(`/backup/${fileName}`),
  verify: (fileName: string) => api.post(`/backup/${fileName}/verify`),
  getStats: () => api.get('/backup/stats'),
};

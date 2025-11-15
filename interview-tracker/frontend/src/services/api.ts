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

/**
 * Backend API Client
 * Handles all communication with the JobFlow FastAPI backend
 */

import type {
  UserProfile,
  Resume,
  Question,
  QuestionMatch,
  Application,
  APIResponse,
} from '../types';

export class BackendClient {
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  /**
   * Set backend URL
   */
  setBaseURL(url: string): void {
    this.baseURL = url;
  }

  /**
   * Generic API request handler
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        const error = await response.text();
        return {
          error: error || response.statusText,
          status: response.status,
        };
      }

      const data = await response.json();
      return {
        data,
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  // ========== Profile API ==========

  async getProfile(): Promise<APIResponse<UserProfile>> {
    return this.request<UserProfile>('/api/profile/');
  }

  async createProfile(profile: Partial<UserProfile>): Promise<APIResponse<UserProfile>> {
    return this.request<UserProfile>('/api/profile/', {
      method: 'POST',
      body: JSON.stringify(profile),
    });
  }

  async updateProfile(profile: Partial<UserProfile>): Promise<APIResponse<UserProfile>> {
    return this.request<UserProfile>('/api/profile/', {
      method: 'PUT',
      body: JSON.stringify(profile),
    });
  }

  // ========== Questions API ==========

  async listQuestions(params?: {
    category?: string;
    search?: string;
    skip?: number;
    limit?: number;
  }): Promise<APIResponse<Question[]>> {
    const queryParams = new URLSearchParams();
    if (params?.category) queryParams.set('category', params.category);
    if (params?.search) queryParams.set('search', params.search);
    if (params?.skip !== undefined) queryParams.set('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.set('limit', params.limit.toString());

    const query = queryParams.toString();
    return this.request<Question[]>(`/api/questions/${query ? '?' + query : ''}`);
  }

  async matchQuestion(questionText: string): Promise<APIResponse<QuestionMatch>> {
    const encodedText = encodeURIComponent(questionText);
    return this.request<QuestionMatch>(
      `/api/questions/match/search?question_text=${encodedText}`
    );
  }

  async learnQuestion(
    questionText: string,
    answer: string,
    category?: string
  ): Promise<APIResponse<Question>> {
    return this.request<Question>('/api/questions/learn', {
      method: 'POST',
      body: JSON.stringify({
        question_text: questionText,
        answer,
        category,
      }),
    });
  }

  async createQuestion(question: {
    question_text: string;
    answer: string;
    category?: string;
    field_type?: string;
  }): Promise<APIResponse<Question>> {
    return this.request<Question>('/api/questions/', {
      method: 'POST',
      body: JSON.stringify({ user_id: 1, ...question }),
    });
  }

  // ========== Resumes API ==========

  async listResumes(): Promise<APIResponse<Resume[]>> {
    return this.request<Resume[]>('/api/resumes/');
  }

  async getResume(resumeId: number): Promise<APIResponse<Resume>> {
    return this.request<Resume>(`/api/resumes/${resumeId}`);
  }

  async selectBestResume(
    jobDescription: string
  ): Promise<
    APIResponse<{
      resume_id?: number;
      resume_name?: string;
      match_score: number;
      reasons: string[];
    }>
  > {
    return this.request('/api/resumes/select', {
      method: 'POST',
      body: JSON.stringify({ job_description: jobDescription }),
    });
  }

  async downloadResume(resumeId: number): Promise<Blob | null> {
    try {
      const response = await fetch(`${this.baseURL}/api/resumes/download/${resumeId}`);
      if (!response.ok) return null;
      return await response.blob();
    } catch {
      return null;
    }
  }

  // ========== Applications API ==========

  async createApplication(application: Application): Promise<APIResponse<Application>> {
    return this.request<Application>('/api/applications/', {
      method: 'POST',
      body: JSON.stringify(application),
    });
  }

  async listApplications(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    company?: string;
    platform?: string;
  }): Promise<APIResponse<Application[]>> {
    const queryParams = new URLSearchParams();
    if (params?.skip !== undefined) queryParams.set('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.set('limit', params.limit.toString());
    if (params?.status) queryParams.set('status', params.status);
    if (params?.company) queryParams.set('company', params.company);
    if (params?.platform) queryParams.set('platform', params.platform);

    const query = queryParams.toString();
    return this.request<Application[]>(
      `/api/applications/${query ? '?' + query : ''}`
    );
  }

  async updateApplicationStatus(
    appId: number,
    status: string,
    notes?: string
  ): Promise<APIResponse<any>> {
    return this.request(`/api/applications/${appId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status_value: status, notes }),
    });
  }

  async addApplicationAnswer(
    appId: number,
    questionText: string,
    answer: string,
    questionId?: number,
    confidence?: number
  ): Promise<APIResponse<any>> {
    return this.request(`/api/applications/${appId}/answers`, {
      method: 'POST',
      body: JSON.stringify({
        application_id: appId,
        question_text: questionText,
        answer,
        question_id: questionId,
        confidence,
      }),
    });
  }

  // ========== Analytics API ==========

  async getOverview(days: number = 30): Promise<APIResponse<any>> {
    return this.request(`/api/analytics/overview?days=${days}`);
  }

  async getRecommendations(days: number = 7): Promise<APIResponse<any>> {
    return this.request(`/api/analytics/recommendations?days=${days}`);
  }

  // ========== Jobs API ==========

  async scoreJob(jobUrl: string): Promise<APIResponse<any>> {
    return this.request('/api/jobs/score', {
      method: 'POST',
      body: JSON.stringify({ job_url: jobUrl }),
    });
  }

  async prepareApplication(jobId: number): Promise<APIResponse<any>> {
    return this.request(`/api/jobs/${jobId}/prepare`, {
      method: 'POST',
    });
  }

  // ========== Health Check ==========

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }

  async getServerInfo(): Promise<APIResponse<{
    name: string;
    version: string;
    status: string;
  }>> {
    return this.request('/');
  }
}

// Export singleton instance
export const backendClient = new BackendClient();

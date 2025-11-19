import axiosInstance from './axios-config';
import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  User,
  ChangePasswordRequest,
} from '../types/auth.types';
import type { ApiResponse } from '../types/common.types';

class AuthService {
  /**
   * Login user with email and password
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await axiosInstance.post<ApiResponse<LoginResponse>>(
      '/api/users/login',
      credentials
    );

    const { token, user, expiresIn } = response.data.data;

    // Store token and user in localStorage
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));

    // Store expiration time
    const expirationTime = Date.now() + expiresIn;
    localStorage.setItem('tokenExpiration', expirationTime.toString());

    return response.data.data;
  }

  /**
   * Register new user
   */
  async register(userData: RegisterRequest): Promise<RegisterResponse> {
    const response = await axiosInstance.post<ApiResponse<RegisterResponse>>(
      '/api/users/register',
      userData
    );

    const { token } = response.data.data;

    // Store token
    if (token) {
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(response.data.data));

      // Set expiration (default 24 hours)
      const expirationTime = Date.now() + (24 * 60 * 60 * 1000);
      localStorage.setItem('tokenExpiration', expirationTime.toString());
    }

    return response.data.data;
  }

  /**
   * Logout user
   */
  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('tokenExpiration');
    localStorage.removeItem('refreshToken');
  }

  /**
   * Get current user from localStorage
   */
  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr) as User;
      } catch (error) {
        console.error('Error parsing user from localStorage:', error);
        return null;
      }
    }
    return null;
  }

  /**
   * Get current user profile from API
   */
  async getUserProfile(): Promise<User> {
    const response = await axiosInstance.get<ApiResponse<User>>('/api/users/profile');

    // Update localStorage
    localStorage.setItem('user', JSON.stringify(response.data.data));

    return response.data.data;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = localStorage.getItem('token');
    const expirationStr = localStorage.getItem('tokenExpiration');

    if (!token || !expirationStr) {
      return false;
    }

    // Check if token is expired
    const expiration = parseInt(expirationStr, 10);
    if (Date.now() >= expiration) {
      this.logout();
      return false;
    }

    return true;
  }

  /**
   * Get stored token
   */
  getToken(): string | null {
    return localStorage.getItem('token');
  }

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<string> {
    const refreshToken = localStorage.getItem('refreshToken');

    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await axiosInstance.post<ApiResponse<{ token: string }>>(
      '/api/auth/refresh',
      { refreshToken }
    );

    const { token } = response.data.data;

    localStorage.setItem('token', token);

    // Update expiration time (default 24 hours)
    const expirationTime = Date.now() + (24 * 60 * 60 * 1000);
    localStorage.setItem('tokenExpiration', expirationTime.toString());

    return token;
  }

  /**
   * Change user password
   */
  async changePassword(passwords: ChangePasswordRequest): Promise<void> {
    await axiosInstance.put<ApiResponse<void>>('/api/users/password', passwords);
  }

  /**
   * Initialize auth state on app load
   */
  async initializeAuth(): Promise<User | null> {
    if (this.isAuthenticated()) {
      try {
        // Fetch fresh user data from API
        return await this.getUserProfile();
      } catch (error) {
        console.error('Failed to fetch user profile:', error);
        this.logout();
        return null;
      }
    }
    return null;
  }
}

export default new AuthService();

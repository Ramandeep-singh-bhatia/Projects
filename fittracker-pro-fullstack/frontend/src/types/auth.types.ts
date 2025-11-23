import { Gender, ActivityLevel, FitnessGoal } from './common.types';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: User;
  expiresIn: number;
}

export interface RegisterRequest {
  email: string;
  password: string;
  confirmPassword?: string;
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  gender: Gender;
  heightCm?: number;
  weightKg?: number;
}

export interface RegisterResponse {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  token: string;
  dateOfBirth: string;
  gender: Gender;
  heightCm?: number;
  weightKg?: number;
  createdAt: string;
}

export interface User {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  gender: Gender;
  heightCm?: number;
  weightKg?: number;
  profile?: UserProfile;
  createdAt: string;
  updatedAt: string;
}

export interface UserProfile {
  id: number;
  userId: number;
  activityLevel?: ActivityLevel;
  fitnessGoal?: FitnessGoal;
  targetWeightKg?: number;
  targetCaloriesPerDay?: number;
  targetProteinGrams?: number;
  targetCarbsGrams?: number;
  targetFatGrams?: number;
  createdAt: string;
  updatedAt: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

export interface UpdateProfileRequest {
  activityLevel?: ActivityLevel;
  fitnessGoal?: FitnessGoal;
  targetWeightKg?: number;
  targetCaloriesPerDay?: number;
  targetProteinGrams?: number;
  targetCarbsGrams?: number;
  targetFatGrams?: number;
}

export interface UpdateUserRequest {
  firstName?: string;
  lastName?: string;
  dateOfBirth?: string;
  gender?: Gender;
  heightCm?: number;
  weightKg?: number;
}

export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
}

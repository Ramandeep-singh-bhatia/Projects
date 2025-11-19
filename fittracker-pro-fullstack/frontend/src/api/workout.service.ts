import axiosInstance from './axios-config';
import type { ApiResponse, PaginatedResponse } from '../types/common.types';
import type { Workout, CreateWorkoutRequest, Exercise } from '../types/workout.types';

class WorkoutService {
  // Workouts
  async getWorkoutsByDate(date: string): Promise<Workout[]> {
    const response = await axiosInstance.get<ApiResponse<Workout[]>>(
      `/api/workouts/date/${date}`
    );
    return response.data.data;
  }

  async getWorkoutsByDateRange(startDate: string, endDate: string): Promise<Workout[]> {
    const response = await axiosInstance.get<ApiResponse<Workout[]>>(
      '/api/workouts/range',
      { params: { startDate, endDate } }
    );
    return response.data.data;
  }

  async getWorkoutById(id: number): Promise<Workout> {
    const response = await axiosInstance.get<ApiResponse<Workout>>(`/api/workouts/${id}`);
    return response.data.data;
  }

  async createWorkout(workoutData: CreateWorkoutRequest): Promise<Workout> {
    const response = await axiosInstance.post<ApiResponse<Workout>>('/api/workouts', workoutData);
    return response.data.data;
  }

  async completeWorkout(id: number): Promise<Workout> {
    const response = await axiosInstance.put<ApiResponse<Workout>>(`/api/workouts/${id}/complete`);
    return response.data.data;
  }

  async deleteWorkout(id: number): Promise<void> {
    await axiosInstance.delete(`/api/workouts/${id}`);
  }

  // Exercises
  async searchExercises(query: string, page = 0, size = 20): Promise<PaginatedResponse<Exercise>> {
    const response = await axiosInstance.get<ApiResponse<PaginatedResponse<Exercise>>>(
      '/api/exercises/search',
      { params: { query, page, size } }
    );
    return response.data.data;
  }

  async getExerciseById(id: number): Promise<Exercise> {
    const response = await axiosInstance.get<ApiResponse<Exercise>>(`/api/exercises/${id}`);
    return response.data.data;
  }
}

export default new WorkoutService();

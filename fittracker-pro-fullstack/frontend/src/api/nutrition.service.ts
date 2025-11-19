import axiosInstance from './axios-config';
import type { ApiResponse, PaginatedResponse } from '../types/common.types';
import type {
  Meal,
  CreateMealRequest,
  UpdateMealRequest,
  FoodItem,
  NutritionSummary
} from '../types/nutrition.types';

class NutritionService {
  // Meals
  async getMealsByDate(date: string): Promise<Meal[]> {
    const response = await axiosInstance.get<ApiResponse<Meal[]>>(
      `/api/meals/date/${date}`
    );
    return response.data.data;
  }

  async getMealById(id: number): Promise<Meal> {
    const response = await axiosInstance.get<ApiResponse<Meal>>(`/api/meals/${id}`);
    return response.data.data;
  }

  async createMeal(mealData: CreateMealRequest): Promise<Meal> {
    const response = await axiosInstance.post<ApiResponse<Meal>>('/api/meals', mealData);
    return response.data.data;
  }

  async updateMeal(id: number, mealData: UpdateMealRequest): Promise<Meal> {
    const response = await axiosInstance.put<ApiResponse<Meal>>(`/api/meals/${id}`, mealData);
    return response.data.data;
  }

  async deleteMeal(id: number): Promise<void> {
    await axiosInstance.delete(`/api/meals/${id}`);
  }

  // Food Items
  async searchFoodItems(query: string, page = 0, size = 20): Promise<PaginatedResponse<FoodItem>> {
    const response = await axiosInstance.get<ApiResponse<PaginatedResponse<FoodItem>>>(
      '/api/food-items/search',
      { params: { query, page, size } }
    );
    return response.data.data;
  }

  async getFoodItemById(id: number): Promise<FoodItem> {
    const response = await axiosInstance.get<ApiResponse<FoodItem>>(`/api/food-items/${id}`);
    return response.data.data;
  }

  async createFoodItem(foodData: Partial<FoodItem>): Promise<FoodItem> {
    const response = await axiosInstance.post<ApiResponse<FoodItem>>('/api/food-items', foodData);
    return response.data.data;
  }

  // Nutrition Summary
  async getDailySummary(date: string): Promise<NutritionSummary> {
    const response = await axiosInstance.get<ApiResponse<NutritionSummary>>(
      `/api/nutrition/summary/daily/${date}`
    );
    return response.data.data;
  }

  async getWeeklySummary(startDate: string): Promise<NutritionSummary[]> {
    const response = await axiosInstance.get<ApiResponse<NutritionSummary[]>>(
      '/api/nutrition/summary/weekly',
      { params: { startDate } }
    );
    return response.data.data;
  }
}

export default new NutritionService();

import { MealType } from './common.types';

export interface FoodCategory {
  id: number;
  name: string;
  description: string;
  createdAt: string;
}

export interface FoodItem {
  id: number;
  name: string;
  brand?: string;
  category: FoodCategory;
  servingSize: number;
  servingUnit: string;
  caloriesPerServing: number;
  proteinGrams: number;
  carbsGrams: number;
  fatGrams: number;
  fiberGrams: number;
  sugarGrams: number;
  sodiumMg: number;
  isVerified: boolean;
  barcode?: string;
  createdAt: string;
  updatedAt: string;
}

export interface MealItem {
  id: number;
  mealId: number;
  foodItem: FoodItem;
  servings: number;
  calories: number;
  proteinGrams: number;
  carbsGrams: number;
  fatGrams: number;
  createdAt: string;
}

export interface Meal {
  id: number;
  userId: number;
  mealType: MealType;
  mealDate: string;
  mealTime: string;
  notes?: string;
  totalCalories: number;
  totalProtein: number;
  totalCarbs: number;
  totalFat: number;
  totalFiber: number;
  totalSugar: number;
  items: MealItem[];
  createdAt: string;
  updatedAt: string;
}

export interface MealItemRequest {
  foodItemId: number;
  servings: number;
}

export interface CreateMealRequest {
  userId: number;
  mealType: MealType;
  mealDate: string;
  mealTime: string;
  notes?: string;
  items: MealItemRequest[];
}

export interface UpdateMealRequest {
  mealType?: MealType;
  mealTime?: string;
  notes?: string;
  items?: MealItemRequest[];
}

export interface NutritionSummary {
  date: string;
  meals: Meal[];
  dailyTotals: {
    totalCalories: number;
    totalProtein: number;
    totalCarbs: number;
    totalFat: number;
    totalFiber: number;
    totalSugar: number;
    mealCount: number;
  };
}

export interface NutritionState {
  meals: Meal[];
  currentDayMeals: Meal[];
  foodItems: FoodItem[];
  searchResults: FoodItem[];
  selectedFood: FoodItem | null;
  loading: boolean;
  error: string | null;
}

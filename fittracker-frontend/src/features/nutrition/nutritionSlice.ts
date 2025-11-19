import { createSlice, createAsyncThunk, type PayloadAction } from '@reduxjs/toolkit';
import nutritionService from '../../api/nutrition.service';
import type { Meal, CreateMealRequest, UpdateMealRequest, NutritionSummary } from '../../types/nutrition.types';
import type { RootState } from '../../store';

interface NutritionState {
  meals: Meal[];
  currentDate: string;
  dailySummary: NutritionSummary | null;
  weeklySummary: NutritionSummary[];
  loading: boolean;
  error: string | null;
}

const initialState: NutritionState = {
  meals: [],
  currentDate: new Date().toISOString().split('T')[0],
  dailySummary: null,
  weeklySummary: [],
  loading: false,
  error: null,
};

// Async thunks
export const fetchMealsByDate = createAsyncThunk(
  'nutrition/fetchMealsByDate',
  async (date: string, { rejectWithValue }) => {
    try {
      return await nutritionService.getMealsByDate(date);
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch meals');
    }
  }
);

export const fetchDailySummary = createAsyncThunk(
  'nutrition/fetchDailySummary',
  async (date: string, { rejectWithValue }) => {
    try {
      return await nutritionService.getDailySummary(date);
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch summary');
    }
  }
);

export const fetchWeeklySummary = createAsyncThunk(
  'nutrition/fetchWeeklySummary',
  async (startDate: string, { rejectWithValue }) => {
    try {
      return await nutritionService.getWeeklySummary(startDate);
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch weekly summary');
    }
  }
);

export const createMeal = createAsyncThunk(
  'nutrition/createMeal',
  async (mealData: CreateMealRequest, { rejectWithValue }) => {
    try {
      return await nutritionService.createMeal(mealData);
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to create meal');
    }
  }
);

export const updateMeal = createAsyncThunk(
  'nutrition/updateMeal',
  async ({ id, data }: { id: number; data: UpdateMealRequest }, { rejectWithValue }) => {
    try {
      return await nutritionService.updateMeal(id, data);
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to update meal');
    }
  }
);

export const deleteMeal = createAsyncThunk(
  'nutrition/deleteMeal',
  async (id: number, { rejectWithValue }) => {
    try {
      await nutritionService.deleteMeal(id);
      return id;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to delete meal');
    }
  }
);

const nutritionSlice = createSlice({
  name: 'nutrition',
  initialState,
  reducers: {
    setCurrentDate: (state, action: PayloadAction<string>) => {
      state.currentDate = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch meals by date
      .addCase(fetchMealsByDate.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMealsByDate.fulfilled, (state, action) => {
        state.loading = false;
        state.meals = action.payload;
      })
      .addCase(fetchMealsByDate.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Fetch daily summary
      .addCase(fetchDailySummary.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDailySummary.fulfilled, (state, action) => {
        state.loading = false;
        state.dailySummary = action.payload;
      })
      .addCase(fetchDailySummary.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Fetch weekly summary
      .addCase(fetchWeeklySummary.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchWeeklySummary.fulfilled, (state, action) => {
        state.loading = false;
        state.weeklySummary = action.payload;
      })
      .addCase(fetchWeeklySummary.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Create meal
      .addCase(createMeal.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createMeal.fulfilled, (state, action) => {
        state.loading = false;
        state.meals.push(action.payload);
      })
      .addCase(createMeal.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Update meal
      .addCase(updateMeal.fulfilled, (state, action) => {
        const index = state.meals.findIndex(m => m.id === action.payload.id);
        if (index !== -1) {
          state.meals[index] = action.payload;
        }
      })
      // Delete meal
      .addCase(deleteMeal.fulfilled, (state, action) => {
        state.meals = state.meals.filter(m => m.id !== action.payload);
      });
  },
});

export const { setCurrentDate, clearError } = nutritionSlice.actions;

// Selectors
export const selectMeals = (state: RootState) => state.nutrition.meals;
export const selectCurrentDate = (state: RootState) => state.nutrition.currentDate;
export const selectDailySummary = (state: RootState) => state.nutrition.dailySummary;
export const selectWeeklySummary = (state: RootState) => state.nutrition.weeklySummary;
export const selectNutritionLoading = (state: RootState) => state.nutrition.loading;
export const selectNutritionError = (state: RootState) => state.nutrition.error;

export default nutritionSlice.reducer;

import { createSlice, createAsyncThunk, type PayloadAction } from '@reduxjs/toolkit';
import workoutService from '../../api/workout.service';
import type { Workout, CreateWorkoutRequest } from '../../types/workout.types';
import type { RootState } from '../../store';

interface WorkoutState {
  workouts: Workout[];
  currentDate: string;
  loading: boolean;
  error: string | null;
}

const initialState: WorkoutState = {
  workouts: [],
  currentDate: new Date().toISOString().split('T')[0],
  loading: false,
  error: null,
};

export const fetchWorkoutsByDate = createAsyncThunk(
  'workout/fetchWorkoutsByDate',
  async (date: string, { rejectWithValue }) => {
    try {
      return await workoutService.getWorkoutsByDate(date);
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch workouts');
    }
  }
);

export const fetchWorkouts = createAsyncThunk(
  'workout/fetchWorkouts',
  async (params: { startDate: string; endDate: string }, { rejectWithValue }) => {
    try {
      return await workoutService.getWorkoutsByDateRange(params.startDate, params.endDate);
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch workouts');
    }
  }
);

export const createWorkout = createAsyncThunk(
  'workout/createWorkout',
  async (workoutData: CreateWorkoutRequest, { rejectWithValue }) => {
    try {
      return await workoutService.createWorkout(workoutData);
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to create workout');
    }
  }
);

export const completeWorkout = createAsyncThunk(
  'workout/completeWorkout',
  async (id: number, { rejectWithValue }) => {
    try {
      return await workoutService.completeWorkout(id);
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to complete workout');
    }
  }
);

export const deleteWorkout = createAsyncThunk(
  'workout/deleteWorkout',
  async (id: number, { rejectWithValue }) => {
    try {
      await workoutService.deleteWorkout(id);
      return id;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to delete workout');
    }
  }
);

const workoutSlice = createSlice({
  name: 'workout',
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
      .addCase(fetchWorkoutsByDate.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchWorkoutsByDate.fulfilled, (state, action) => {
        state.loading = false;
        state.workouts = action.payload;
      })
      .addCase(fetchWorkoutsByDate.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchWorkouts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchWorkouts.fulfilled, (state, action) => {
        state.loading = false;
        state.workouts = action.payload;
      })
      .addCase(fetchWorkouts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(createWorkout.fulfilled, (state, action) => {
        state.workouts.push(action.payload);
      })
      .addCase(completeWorkout.fulfilled, (state, action) => {
        const index = state.workouts.findIndex(w => w.id === action.payload.id);
        if (index !== -1) {
          state.workouts[index] = action.payload;
        }
      })
      .addCase(deleteWorkout.fulfilled, (state, action) => {
        state.workouts = state.workouts.filter(w => w.id !== action.payload);
      });
  },
});

export const { setCurrentDate, clearError } = workoutSlice.actions;
export const selectWorkouts = (state: RootState) => state.workout.workouts;
export const selectWorkoutLoading = (state: RootState) => state.workout.loading;
export const selectWorkoutError = (state: RootState) => state.workout.error;

export default workoutSlice.reducer;

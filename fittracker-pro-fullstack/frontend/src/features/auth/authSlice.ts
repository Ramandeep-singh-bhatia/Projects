import { createSlice, createAsyncThunk, type PayloadAction } from '@reduxjs/toolkit';
import authService from '../../api/auth.service';
import type {
  AuthState,
  LoginRequest,
  RegisterRequest,
  User,
  ChangePasswordRequest,
} from '../../types/auth.types';
import type { RootState } from '../../store';

// Initial state
const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  loading: false,
  error: null,
};

// Async thunks

/**
 * Login user
 */
export const loginUser = createAsyncThunk(
  'auth/loginUser',
  async (credentials: LoginRequest, { rejectWithValue }) => {
    try {
      const response = await authService.login(credentials);
      return response;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Login failed. Please try again.'
      );
    }
  }
);

/**
 * Register new user
 */
export const registerUser = createAsyncThunk(
  'auth/registerUser',
  async (userData: RegisterRequest, { rejectWithValue }) => {
    try {
      const response = await authService.register(userData);
      return response;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Registration failed. Please try again.'
      );
    }
  }
);

/**
 * Load user from localStorage and refresh from API
 */
export const loadUser = createAsyncThunk(
  'auth/loadUser',
  async (_, { rejectWithValue }) => {
    try {
      const user = await authService.initializeAuth();
      if (!user) {
        return rejectWithValue('No authenticated user found');
      }
      return user;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to load user'
      );
    }
  }
);

/**
 * Refresh user profile
 */
export const refreshUserProfile = createAsyncThunk(
  'auth/refreshUserProfile',
  async (_, { rejectWithValue }) => {
    try {
      const user = await authService.getUserProfile();
      return user;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to refresh user profile'
      );
    }
  }
);

/**
 * Change password
 */
export const changePassword = createAsyncThunk(
  'auth/changePassword',
  async (passwords: ChangePasswordRequest, { rejectWithValue }) => {
    try {
      await authService.changePassword(passwords);
      return true;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to change password'
      );
    }
  }
);

// Slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // Logout user
    logout: (state) => {
      authService.logout();
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      state.loading = false;
      state.error = null;
    },

    // Set user (for manual updates)
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
    },

    // Clear error
    clearError: (state) => {
      state.error = null;
    },

    // Set token
    setToken: (state, action: PayloadAction<string>) => {
      state.token = action.payload;
      state.isAuthenticated = true;
    },
  },
  extraReducers: (builder) => {
    // Login user
    builder
      .addCase(loginUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false;
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        state.error = action.payload as string;
      });

    // Register user
    builder
      .addCase(registerUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload as any; // Register response contains user data
        state.token = action.payload.token;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.loading = false;
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        state.error = action.payload as string;
      });

    // Load user
    builder
      .addCase(loadUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loadUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.token = authService.getToken();
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(loadUser.rejected, (state, action) => {
        state.loading = false;
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        state.error = action.payload as string;
      });

    // Refresh user profile
    builder
      .addCase(refreshUserProfile.pending, (state) => {
        state.loading = true;
      })
      .addCase(refreshUserProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.error = null;
      })
      .addCase(refreshUserProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Change password
    builder
      .addCase(changePassword.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(changePassword.fulfilled, (state) => {
        state.loading = false;
        state.error = null;
      })
      .addCase(changePassword.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

// Actions
export const { logout, setUser, clearError, setToken } = authSlice.actions;

// Selectors
export const selectCurrentUser = (state: RootState) => state.auth.user;
export const selectIsAuthenticated = (state: RootState) => state.auth.isAuthenticated;
export const selectAuthLoading = (state: RootState) => state.auth.loading;
export const selectAuthError = (state: RootState) => state.auth.error;
export const selectToken = (state: RootState) => state.auth.token;

// Reducer
export default authSlice.reducer;

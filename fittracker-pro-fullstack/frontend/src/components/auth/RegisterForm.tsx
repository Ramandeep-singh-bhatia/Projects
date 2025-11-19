import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Box,
  TextField,
  Button,
  Typography,
  Link,
  Alert,
  CircularProgress,
  Paper,
  InputAdornment,
  IconButton,
  MenuItem,
  Stack,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '../../store';
import { registerUser, clearError, selectAuthLoading, selectAuthError } from '../../features/auth/authSlice';
import type { RegisterRequest } from '../../types/auth.types';
import { Gender } from '../../types/common.types';

// Validation schema
const registerSchema = z
  .object({
    email: z
      .string()
      .min(1, 'Email is required')
      .email('Invalid email format'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
      .regex(/[0-9]/, 'Password must contain at least one number')
      .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character'),
    confirmPassword: z.string().min(1, 'Please confirm your password'),
    firstName: z
      .string()
      .min(1, 'First name is required')
      .min(2, 'First name must be at least 2 characters'),
    lastName: z
      .string()
      .min(1, 'Last name is required')
      .min(2, 'Last name must be at least 2 characters'),
    dateOfBirth: z
      .string()
      .min(1, 'Date of birth is required')
      .refine((date) => {
        const birthDate = new Date(date);
        const today = new Date();
        const age = today.getFullYear() - birthDate.getFullYear();
        return age >= 13 && age <= 120;
      }, 'You must be at least 13 years old'),
    gender: z.enum([Gender.MALE, Gender.FEMALE, Gender.OTHER, Gender.PREFER_NOT_TO_SAY] as const, {
      message: 'Gender is required'
    }),
    heightCm: z
      .number()
      .min(50, 'Height must be at least 50 cm')
      .max(300, 'Height must be less than 300 cm')
      .optional(),
    weightKg: z
      .number()
      .min(20, 'Weight must be at least 20 kg')
      .max(500, 'Weight must be less than 500 kg')
      .optional(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

const RegisterForm: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const loading = useAppSelector(selectAuthLoading);
  const error = useAppSelector(selectAuthError);

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: '',
      password: '',
      confirmPassword: '',
      firstName: '',
      lastName: '',
      dateOfBirth: '',
      gender: undefined,
      heightCm: undefined,
      weightKg: undefined,
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    dispatch(clearError());

    const registerData: RegisterRequest = {
      email: data.email,
      password: data.password,
      firstName: data.firstName,
      lastName: data.lastName,
      dateOfBirth: data.dateOfBirth,
      gender: data.gender,
      heightCm: data.heightCm,
      weightKg: data.weightKg,
    };

    try {
      const result = await dispatch(registerUser(registerData)).unwrap();
      if (result) {
        navigate('/dashboard');
      }
    } catch (err) {
      // Error is handled by Redux state
      console.error('Registration failed:', err);
    }
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 4,
        maxWidth: 600,
        width: '100%',
        borderRadius: 2,
      }}
    >
      <Box sx={{ mb: 3, textAlign: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Create Account
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Join FitTracker Pro and start your fitness journey
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => dispatch(clearError())}>
          {error}
        </Alert>
      )}

      <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <Stack spacing={2}>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <Controller
              name="firstName"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="First Name"
                  fullWidth
                  autoComplete="given-name"
                  autoFocus
                  error={!!errors.firstName}
                  helperText={errors.firstName?.message}
                  disabled={loading}
                />
              )}
            />

            <Controller
              name="lastName"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Last Name"
                  fullWidth
                  autoComplete="family-name"
                  error={!!errors.lastName}
                  helperText={errors.lastName?.message}
                  disabled={loading}
                />
              )}
            />
          </Stack>

          <Controller
            name="email"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Email Address"
                type="email"
                fullWidth
                autoComplete="email"
                error={!!errors.email}
                helperText={errors.email?.message}
                disabled={loading}
              />
            )}
          />

          <Controller
            name="password"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Password"
                type={showPassword ? 'text' : 'password'}
                fullWidth
                autoComplete="new-password"
                error={!!errors.password}
                helperText={errors.password?.message}
                disabled={loading}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="toggle password visibility"
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            )}
          />

          <Controller
            name="confirmPassword"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Confirm Password"
                type={showConfirmPassword ? 'text' : 'password'}
                fullWidth
                autoComplete="new-password"
                error={!!errors.confirmPassword}
                helperText={errors.confirmPassword?.message}
                disabled={loading}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="toggle confirm password visibility"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        edge="end"
                      >
                        {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            )}
          />

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <Controller
              name="dateOfBirth"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Date of Birth"
                  type="date"
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                  error={!!errors.dateOfBirth}
                  helperText={errors.dateOfBirth?.message}
                  disabled={loading}
                />
              )}
            />

            <Controller
              name="gender"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  select
                  label="Gender"
                  fullWidth
                  error={!!errors.gender}
                  helperText={errors.gender?.message}
                  disabled={loading}
                >
                  <MenuItem value={Gender.MALE}>Male</MenuItem>
                  <MenuItem value={Gender.FEMALE}>Female</MenuItem>
                  <MenuItem value={Gender.OTHER}>Other</MenuItem>
                  <MenuItem value={Gender.PREFER_NOT_TO_SAY}>Prefer not to say</MenuItem>
                </TextField>
              )}
            />
          </Stack>

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <Controller
              name="heightCm"
              control={control}
              render={({ field: { onChange, value, ...field } }) => (
                <TextField
                  {...field}
                  label="Height (cm)"
                  type="number"
                  fullWidth
                  value={value || ''}
                  onChange={(e) => {
                    const val = e.target.value;
                    onChange(val === '' ? undefined : parseFloat(val));
                  }}
                  error={!!errors.heightCm}
                  helperText={errors.heightCm?.message}
                  disabled={loading}
                />
              )}
            />

            <Controller
              name="weightKg"
              control={control}
              render={({ field: { onChange, value, ...field } }) => (
                <TextField
                  {...field}
                  label="Weight (kg)"
                  type="number"
                  fullWidth
                  value={value || ''}
                  onChange={(e) => {
                    const val = e.target.value;
                    onChange(val === '' ? undefined : parseFloat(val));
                  }}
                  error={!!errors.weightKg}
                  helperText={errors.weightKg?.message}
                  disabled={loading}
                />
              )}
            />
          </Stack>
        </Stack>

        <Button
          type="submit"
          fullWidth
          variant="contained"
          size="large"
          sx={{ mt: 3, mb: 2, py: 1.5 }}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} color="inherit" /> : 'Sign Up'}
        </Button>

        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Already have an account?{' '}
            <Link component={RouterLink} to="/login" variant="body2" fontWeight="medium">
              Sign in
            </Link>
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default RegisterForm;

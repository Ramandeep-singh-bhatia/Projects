import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Stack,
  MenuItem,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Save, Cancel } from '@mui/icons-material';
import { useAppSelector } from '../../store';
import { selectCurrentUser } from '../../features/auth/authSlice';
import { Gender, ActivityLevel, FitnessGoal } from '../../types/common.types';
import MainLayout from '../../components/layout/MainLayout';

const editProfileSchema = z.object({
  firstName: z.string().min(1, 'First name is required').min(2, 'First name must be at least 2 characters'),
  lastName: z.string().min(1, 'Last name is required').min(2, 'Last name must be at least 2 characters'),
  dateOfBirth: z.string().min(1, 'Date of birth is required'),
  gender: z.enum([Gender.MALE, Gender.FEMALE, Gender.OTHER, Gender.PREFER_NOT_TO_SAY] as const),
  heightCm: z.number().min(50, 'Height must be at least 50 cm').max(300, 'Height must be less than 300 cm').optional(),
  weightKg: z.number().min(20, 'Weight must be at least 20 kg').max(500, 'Weight must be less than 500 kg').optional(),
  activityLevel: z.enum([
    ActivityLevel.SEDENTARY,
    ActivityLevel.LIGHTLY_ACTIVE,
    ActivityLevel.MODERATELY_ACTIVE,
    ActivityLevel.VERY_ACTIVE,
    ActivityLevel.EXTRA_ACTIVE
  ] as const).optional(),
  fitnessGoal: z.enum([
    FitnessGoal.WEIGHT_LOSS,
    FitnessGoal.WEIGHT_GAIN,
    FitnessGoal.MUSCLE_GAIN,
    FitnessGoal.MAINTENANCE
  ] as const).optional(),
  targetCaloriesPerDay: z.number().min(1000, 'Target calories must be at least 1000').max(5000, 'Target calories must be less than 5000').optional(),
});

type EditProfileFormData = z.infer<typeof editProfileSchema>;

const EditProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const user = useAppSelector(selectCurrentUser);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [success, setSuccess] = React.useState(false);

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<EditProfileFormData>({
    resolver: zodResolver(editProfileSchema),
    defaultValues: {
      firstName: user?.firstName || '',
      lastName: user?.lastName || '',
      dateOfBirth: user?.dateOfBirth || '',
      gender: user?.gender || undefined,
      heightCm: user?.heightCm || undefined,
      weightKg: user?.weightKg || undefined,
      activityLevel: user?.profile?.activityLevel || undefined,
      fitnessGoal: user?.profile?.fitnessGoal || undefined,
      targetCaloriesPerDay: user?.profile?.targetCaloriesPerDay || undefined,
    },
  });

  useEffect(() => {
    if (user) {
      reset({
        firstName: user.firstName,
        lastName: user.lastName,
        dateOfBirth: user.dateOfBirth,
        gender: user.gender,
        heightCm: user.heightCm,
        weightKg: user.weightKg,
        activityLevel: user.profile?.activityLevel,
        fitnessGoal: user.profile?.fitnessGoal,
        targetCaloriesPerDay: user.profile?.targetCaloriesPerDay,
      });
    }
  }, [user, reset]);

  const onSubmit = async (data: EditProfileFormData) => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // TODO: Call API to update profile
      console.log('Updating profile:', data);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      setSuccess(true);
      setTimeout(() => {
        navigate('/profile');
      }, 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return null;
  }

  return (
    <MainLayout>
      <Stack spacing={4}>
        <Box>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Edit Profile
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Update your personal information and fitness preferences
          </Typography>
        </Box>

        {error && <Alert severity="error">{error}</Alert>}
        {success && <Alert severity="success">Profile updated successfully! Redirecting...</Alert>}

        <Card elevation={2}>
          <CardContent>
            <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
              <Stack spacing={3}>
                <Typography variant="h6" fontWeight="bold">
                  Personal Information
                </Typography>

                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                  <Controller
                    name="firstName"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="First Name"
                        fullWidth
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
                        error={!!errors.lastName}
                        helperText={errors.lastName?.message}
                        disabled={loading}
                      />
                    )}
                  />
                </Stack>

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

                <Typography variant="h6" fontWeight="bold" sx={{ mt: 2 }}>
                  Fitness Profile
                </Typography>

                <Controller
                  name="activityLevel"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      select
                      label="Activity Level"
                      fullWidth
                      error={!!errors.activityLevel}
                      helperText={errors.activityLevel?.message || 'How active are you in daily life?'}
                      disabled={loading}
                    >
                      <MenuItem value={ActivityLevel.SEDENTARY}>Sedentary (little or no exercise)</MenuItem>
                      <MenuItem value={ActivityLevel.LIGHTLY_ACTIVE}>Lightly Active (exercise 1-3 days/week)</MenuItem>
                      <MenuItem value={ActivityLevel.MODERATELY_ACTIVE}>Moderately Active (exercise 3-5 days/week)</MenuItem>
                      <MenuItem value={ActivityLevel.VERY_ACTIVE}>Very Active (exercise 6-7 days/week)</MenuItem>
                      <MenuItem value={ActivityLevel.EXTRA_ACTIVE}>Extra Active (very intense exercise daily)</MenuItem>
                    </TextField>
                  )}
                />

                <Controller
                  name="fitnessGoal"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      select
                      label="Fitness Goal"
                      fullWidth
                      error={!!errors.fitnessGoal}
                      helperText={errors.fitnessGoal?.message || 'What are you trying to achieve?'}
                      disabled={loading}
                    >
                      <MenuItem value={FitnessGoal.WEIGHT_LOSS}>Weight Loss</MenuItem>
                      <MenuItem value={FitnessGoal.WEIGHT_GAIN}>Weight Gain</MenuItem>
                      <MenuItem value={FitnessGoal.MUSCLE_GAIN}>Muscle Gain</MenuItem>
                      <MenuItem value={FitnessGoal.MAINTENANCE}>Maintenance</MenuItem>
                    </TextField>
                  )}
                />

                <Controller
                  name="targetCaloriesPerDay"
                  control={control}
                  render={({ field: { onChange, value, ...field } }) => (
                    <TextField
                      {...field}
                      label="Target Calories (kcal/day)"
                      type="number"
                      fullWidth
                      value={value || ''}
                      onChange={(e) => {
                        const val = e.target.value;
                        onChange(val === '' ? undefined : parseFloat(val));
                      }}
                      error={!!errors.targetCaloriesPerDay}
                      helperText={errors.targetCaloriesPerDay?.message || 'Daily calorie goal'}
                      disabled={loading}
                    />
                  )}
                />

                <Stack direction="row" spacing={2} sx={{ mt: 3 }}>
                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    startIcon={loading ? <CircularProgress size={20} /> : <Save />}
                    disabled={loading || !isDirty}
                    fullWidth
                  >
                    {loading ? 'Saving...' : 'Save Changes'}
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    startIcon={<Cancel />}
                    onClick={() => navigate('/profile')}
                    disabled={loading}
                    fullWidth
                  >
                    Cancel
                  </Button>
                </Stack>
              </Stack>
            </Box>
          </CardContent>
        </Card>
      </Stack>
    </MainLayout>
  );
};

export default EditProfilePage;

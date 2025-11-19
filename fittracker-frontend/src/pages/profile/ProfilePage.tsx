import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Button,
  Stack,
  Chip,
  Divider,
} from '@mui/material';
import {
  Edit,
  Person,
  FitnessCenter,
  Height,
  MonitorWeight,
  Cake,
  Email,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAppSelector } from '../../store';
import { selectCurrentUser } from '../../features/auth/authSlice';
import MainLayout from '../../components/layout/MainLayout';

const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const user = useAppSelector(selectCurrentUser);

  if (!user) {
    return null;
  }

  const getUserInitials = () => {
    return `${user.firstName.charAt(0)}${user.lastName.charAt(0)}`.toUpperCase();
  };

  const getAge = () => {
    const birthDate = new Date(user.dateOfBirth);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  return (
    <MainLayout>
      <Stack spacing={4}>
        {/* Header */}
        <Box>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            My Profile
          </Typography>
          <Typography variant="body1" color="text.secondary">
            View and manage your personal information
          </Typography>
        </Box>

        {/* Profile Card */}
        <Card elevation={2}>
          <CardContent>
            <Stack spacing={3}>
              {/* Avatar and Basic Info */}
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 3 }}>
                <Avatar
                  sx={{
                    width: 100,
                    height: 100,
                    fontSize: 40,
                    bgcolor: 'primary.main',
                    fontWeight: 600,
                  }}
                >
                  {getUserInitials()}
                </Avatar>

                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="h5" fontWeight="bold" gutterBottom>
                    {user.firstName} {user.lastName}
                  </Typography>
                  <Typography variant="body1" color="text.secondary" paragraph>
                    {user.email}
                  </Typography>
                  <Stack direction="row" spacing={1}>
                    <Chip
                      label={user.gender}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                    <Chip
                      label={`${getAge()} years old`}
                      size="small"
                      color="secondary"
                      variant="outlined"
                    />
                  </Stack>
                </Box>

                <Button
                  variant="contained"
                  startIcon={<Edit />}
                  onClick={() => navigate('/profile/edit')}
                >
                  Edit Profile
                </Button>
              </Box>

              <Divider />

              {/* Personal Details */}
              <Box>
                <Typography variant="h6" gutterBottom fontWeight="bold">
                  Personal Details
                </Typography>
                <Stack spacing={2}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Person color="action" />
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Full Name
                      </Typography>
                      <Typography variant="body1">
                        {user.firstName} {user.lastName}
                      </Typography>
                    </Box>
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Email color="action" />
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Email Address
                      </Typography>
                      <Typography variant="body1">{user.email}</Typography>
                    </Box>
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Cake color="action" />
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Date of Birth
                      </Typography>
                      <Typography variant="body1">
                        {new Date(user.dateOfBirth).toLocaleDateString()} ({getAge()} years old)
                      </Typography>
                    </Box>
                  </Box>

                  {user.heightCm && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Height color="action" />
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Height
                        </Typography>
                        <Typography variant="body1">{user.heightCm} cm</Typography>
                      </Box>
                    </Box>
                  )}

                  {user.weightKg && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <MonitorWeight color="action" />
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Weight
                        </Typography>
                        <Typography variant="body1">{user.weightKg} kg</Typography>
                      </Box>
                    </Box>
                  )}
                </Stack>
              </Box>

              {user.profile && (
                <>
                  <Divider />
                  <Box>
                    <Typography variant="h6" gutterBottom fontWeight="bold">
                      Fitness Profile
                    </Typography>
                    <Stack spacing={2}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <FitnessCenter color="action" />
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Activity Level
                          </Typography>
                          <Typography variant="body1">
                            {user.profile.activityLevel?.replace(/_/g, ' ')}
                          </Typography>
                        </Box>
                      </Box>

                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <FitnessCenter color="action" />
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Fitness Goal
                          </Typography>
                          <Typography variant="body1">
                            {user.profile.fitnessGoal?.replace(/_/g, ' ')}
                          </Typography>
                        </Box>
                      </Box>

                      {user.profile.targetCaloriesPerDay && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <FitnessCenter color="action" />
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Target Calories
                            </Typography>
                            <Typography variant="body1">
                              {user.profile.targetCaloriesPerDay} kcal/day
                            </Typography>
                          </Box>
                        </Box>
                      )}
                    </Stack>
                  </Box>
                </>
              )}

              <Divider />

              {/* Account Info */}
              <Box>
                <Typography variant="h6" gutterBottom fontWeight="bold">
                  Account Information
                </Typography>
                <Stack spacing={2}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Member Since
                    </Typography>
                    <Typography variant="body1">
                      {new Date(user.createdAt).toLocaleDateString()}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Last Updated
                    </Typography>
                    <Typography variant="body1">
                      {new Date(user.updatedAt).toLocaleDateString()}
                    </Typography>
                  </Box>
                </Stack>
              </Box>
            </Stack>
          </CardContent>
        </Card>

        {/* Actions */}
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <Button
            variant="outlined"
            onClick={() => navigate('/profile/change-password')}
            fullWidth
          >
            Change Password
          </Button>
          <Button
            variant="outlined"
            color="error"
            onClick={() => {
              /* TODO: Implement account deletion */
            }}
            fullWidth
          >
            Delete Account
          </Button>
        </Stack>
      </Stack>
    </MainLayout>
  );
};

export default ProfilePage;

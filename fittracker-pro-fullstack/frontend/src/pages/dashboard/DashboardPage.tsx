import React from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Stack,
} from '@mui/material';
import {
  Restaurant,
  FitnessCenter,
  ShowChart,
  LocalFireDepartment,
  Add,
  TrendingUp,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAppSelector } from '../../store';
import { selectCurrentUser } from '../../features/auth/authSlice';
import MainLayout from '../../components/layout/MainLayout';
import StatCard from '../../components/dashboard/StatCard';
import WeeklyProgressChart from '../../components/dashboard/WeeklyProgressChart';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const user = useAppSelector(selectCurrentUser);

  const recentActivities = [
    {
      id: 1,
      type: 'meal',
      title: 'Breakfast logged',
      time: '2 hours ago',
      icon: <Restaurant />,
      color: 'success.main',
    },
    {
      id: 2,
      type: 'workout',
      title: 'Morning Run - 5km',
      time: '4 hours ago',
      icon: <FitnessCenter />,
      color: 'primary.main',
    },
    {
      id: 3,
      type: 'meal',
      title: 'Lunch logged',
      time: '6 hours ago',
      icon: <Restaurant />,
      color: 'success.main',
    },
  ];

  return (
    <MainLayout>
      <Stack spacing={4}>
        {/* Welcome Section */}
        <Box>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Welcome back, {user?.firstName}! 👋
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Here's your fitness overview for today
          </Typography>
        </Box>

        {/* Stats Cards */}
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3} sx={{ flexWrap: 'wrap' }}>
          <Box sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 12px)', md: '1 1 calc(25% - 18px)' } }}>
            <StatCard
              title="Calories Today"
              value="1,850"
              subtitle="of 2,200 goal"
              icon={LocalFireDepartment}
              color="#ff6b6b"
              trend={{ value: 5, isPositive: true }}
            />
          </Box>
          <Box sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 12px)', md: '1 1 calc(25% - 18px)' } }}>
            <StatCard
              title="Workouts"
              value="2"
              subtitle="sessions today"
              icon={FitnessCenter}
              color="#667eea"
              trend={{ value: 15, isPositive: true }}
            />
          </Box>
          <Box sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 12px)', md: '1 1 calc(25% - 18px)' } }}>
            <StatCard
              title="Meals Logged"
              value="3"
              subtitle="of 4 meals"
              icon={Restaurant}
              color="#48bb78"
            />
          </Box>
          <Box sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 12px)', md: '1 1 calc(25% - 18px)' } }}>
            <StatCard
              title="Weekly Progress"
              value="85%"
              subtitle="on track"
              icon={TrendingUp}
              color="#764ba2"
              trend={{ value: 12, isPositive: true }}
            />
          </Box>
        </Stack>

        {/* Charts and Activity */}
        <Stack direction={{ xs: 'column', lg: 'row' }} spacing={3}>
          <Box sx={{ flex: { xs: '1 1 100%', lg: '1 1 65%' } }}>
            <WeeklyProgressChart />
          </Box>
          <Box sx={{ flex: { xs: '1 1 100%', lg: '1 1 35%' } }}>
            <Card elevation={2} sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom fontWeight="bold">
                  Recent Activity
                </Typography>
                <List>
                  {recentActivities.map((activity) => (
                    <ListItem
                      key={activity.id}
                      sx={{
                        borderRadius: 1,
                        mb: 1,
                        '&:hover': { backgroundColor: 'action.hover' },
                      }}
                    >
                      <ListItemIcon>
                        <Box
                          sx={{
                            backgroundColor: activity.color,
                            borderRadius: 1,
                            p: 0.75,
                            display: 'flex',
                            alignItems: 'center',
                          }}
                        >
                          {React.cloneElement(activity.icon, {
                            sx: { color: 'white', fontSize: 20 },
                          })}
                        </Box>
                      </ListItemIcon>
                      <ListItemText
                        primary={activity.title}
                        secondary={activity.time}
                        primaryTypographyProps={{ fontWeight: 500 }}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Box>
        </Stack>

        {/* Quick Actions */}
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Quick Actions
            </Typography>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mt: 2, flexWrap: 'wrap' }}>
              <Box sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 8px)', md: '1 1 calc(25% - 12px)' } }}>
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={<Add />}
                  onClick={() => navigate('/nutrition')}
                  sx={{
                    py: 1.5,
                    background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
                  }}
                >
                  Log Meal
                </Button>
              </Box>
              <Box sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 8px)', md: '1 1 calc(25% - 12px)' } }}>
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={<Add />}
                  onClick={() => navigate('/workouts')}
                  sx={{
                    py: 1.5,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  }}
                >
                  Start Workout
                </Button>
              </Box>
              <Box sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 8px)', md: '1 1 calc(25% - 12px)' } }}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<ShowChart />}
                  onClick={() => navigate('/analytics')}
                  sx={{ py: 1.5 }}
                >
                  View Analytics
                </Button>
              </Box>
              <Box sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 8px)', md: '1 1 calc(25% - 12px)' } }}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<ShowChart />}
                  onClick={() => navigate('/profile')}
                  sx={{ py: 1.5 }}
                >
                  Update Goals
                </Button>
              </Box>
            </Stack>
          </CardContent>
        </Card>
      </Stack>
    </MainLayout>
  );
};

export default DashboardPage;

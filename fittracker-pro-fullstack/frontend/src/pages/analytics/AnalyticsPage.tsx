import React, { useEffect, useMemo } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Stack,
  LinearProgress,
} from '@mui/material';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import MainLayout from '../../components/layout/MainLayout';
import { useAppDispatch, useAppSelector } from '../../store';
import { fetchWeeklySummary, selectWeeklySummary, selectNutritionLoading } from '../../features/nutrition/nutritionSlice';
import { fetchWorkouts, selectWorkouts, selectWorkoutLoading } from '../../features/workout/workoutSlice';

const AnalyticsPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const weeklySummary = useAppSelector(selectWeeklySummary);
  const workouts = useAppSelector(selectWorkouts);
  const nutritionLoading = useAppSelector(selectNutritionLoading);
  const workoutLoading = useAppSelector(selectWorkoutLoading);

  useEffect(() => {
    // Get data for the last 7 days
    const today = new Date();
    const sevenDaysAgo = new Date(today);
    sevenDaysAgo.setDate(today.getDate() - 6);
    const startDate = sevenDaysAgo.toISOString().split('T')[0];

    dispatch(fetchWeeklySummary(startDate));

    // Fetch workouts for the last 30 days for workout analytics
    const thirtyDaysAgo = new Date(today);
    thirtyDaysAgo.setDate(today.getDate() - 30);
    const thirtyDaysAgoStr = thirtyDaysAgo.toISOString().split('T')[0];
    dispatch(fetchWorkouts({ startDate: thirtyDaysAgoStr, endDate: today.toISOString().split('T')[0] }));
  }, [dispatch]);

  // Transform weekly nutrition data for charts
  const weeklyData = useMemo(() => {
    if (!weeklySummary || weeklySummary.length === 0) {
      return [];
    }

    return weeklySummary.map(summary => {
      const date = new Date(summary.date);
      const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

      return {
        day: dayNames[date.getDay()],
        calories: summary.dailyTotals.totalCalories,
        burned: 0, // We'll calculate from workouts if available
        protein: summary.dailyTotals.totalProtein,
        carbs: summary.dailyTotals.totalCarbs,
        fat: summary.dailyTotals.totalFat,
      };
    });
  }, [weeklySummary]);

  // Calculate macro distribution from weekly average
  const macroData = useMemo(() => {
    if (weeklySummary.length === 0) {
      return [];
    }

    const avgProtein = weeklySummary.reduce((sum, s) => sum + s.dailyTotals.totalProtein, 0) / weeklySummary.length;
    const avgCarbs = weeklySummary.reduce((sum, s) => sum + s.dailyTotals.totalCarbs, 0) / weeklySummary.length;
    const avgFat = weeklySummary.reduce((sum, s) => sum + s.dailyTotals.totalFat, 0) / weeklySummary.length;

    // Calculate calories from macros (protein/carbs = 4 cal/g, fat = 9 cal/g)
    const proteinCal = avgProtein * 4;
    const carbsCal = avgCarbs * 4;
    const fatCal = avgFat * 9;
    const total = proteinCal + carbsCal + fatCal;

    if (total === 0) return [];

    return [
      { name: 'Protein', value: Math.round((proteinCal / total) * 100), color: '#667eea' },
      { name: 'Carbs', value: Math.round((carbsCal / total) * 100), color: '#f6ad55' },
      { name: 'Fat', value: Math.round((fatCal / total) * 100), color: '#fc8181' },
    ];
  }, [weeklySummary]);

  // Workout breakdown - show total stats
  const workoutData = useMemo(() => {
    if (!workouts || workouts.length === 0) {
      return [];
    }

    return [
      {
        type: 'All Workouts',
        count: workouts.length,
        duration: workouts.reduce((sum, w) => sum + (w.totalDurationMinutes || 0), 0),
      },
    ];
  }, [workouts]);

  // Calculate summary stats
  const avgCalories = useMemo(() => {
    if (weeklySummary.length === 0) return 0;
    return Math.round(weeklySummary.reduce((sum, s) => sum + s.dailyTotals.totalCalories, 0) / weeklySummary.length);
  }, [weeklySummary]);

  const totalWorkouts = workouts?.length || 0;
  const totalCaloriesBurned = useMemo(() => {
    return workouts?.reduce((sum, w) => sum + (w.totalCaloriesBurned || 0), 0) || 0;
  }, [workouts]);

  const loading = nutritionLoading || workoutLoading;

  if (loading && weeklySummary.length === 0 && workouts.length === 0) {
    return (
      <MainLayout>
        <Box sx={{ py: 4 }}>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Analytics & Progress
          </Typography>
          <LinearProgress sx={{ mt: 2 }} />
        </Box>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <Stack spacing={4}>
        <Box>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Analytics & Progress
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Track your progress with detailed charts and insights
          </Typography>
        </Box>

        {weeklyData.length > 0 && (
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                Weekly Calorie Trends
              </Typography>
              <Box sx={{ width: '100%', height: 300, mt: 2 }}>
                <ResponsiveContainer>
                  <LineChart data={weeklyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="calories" stroke="#667eea" strokeWidth={2} name="Consumed" />
                    <Line type="monotone" dataKey="burned" stroke="#764ba2" strokeWidth={2} name="Burned" />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        )}

        <Stack direction={{ xs: 'column', lg: 'row' }} spacing={3}>
          {macroData.length > 0 && (
            <Card elevation={2} sx={{ flex: 1 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom fontWeight="bold">
                  Macro Distribution
                </Typography>
                <Box sx={{ width: '100%', height: 300, mt: 2 }}>
                  <ResponsiveContainer>
                    <PieChart>
                      <Pie
                        data={macroData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value }) => `${name}: ${value}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {macroData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          )}

          {workoutData.length > 0 && (
            <Card elevation={2} sx={{ flex: 1 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom fontWeight="bold">
                  Workout Breakdown
                </Typography>
                <Box sx={{ width: '100%', height: 300, mt: 2 }}>
                  <ResponsiveContainer>
                    <BarChart data={workoutData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="type" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="count" fill="#667eea" name="Sessions" />
                      <Bar dataKey="duration" fill="#764ba2" name="Minutes" />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          )}
        </Stack>

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <Card elevation={2} sx={{ flex: 1 }}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">Avg Calories</Typography>
              <Typography variant="h4" fontWeight="bold">{avgCalories}</Typography>
              <Typography variant="body2" color="text.secondary">per day</Typography>
            </CardContent>
          </Card>
          <Card elevation={2} sx={{ flex: 1 }}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">Workouts</Typography>
              <Typography variant="h4" fontWeight="bold">{totalWorkouts}</Typography>
              <Typography variant="body2" color="text.secondary">last 30 days</Typography>
            </CardContent>
          </Card>
          <Card elevation={2} sx={{ flex: 1 }}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">Calories Burned</Typography>
              <Typography variant="h4" fontWeight="bold">{totalCaloriesBurned}</Typography>
              <Typography variant="body2" color="text.secondary">total</Typography>
            </CardContent>
          </Card>
          <Card elevation={2} sx={{ flex: 1 }}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">Weekly Avg</Typography>
              <Typography variant="h4" fontWeight="bold">
                {weeklySummary.length > 0 ? Math.round(weeklySummary.reduce((sum, s) => sum + s.dailyTotals.mealCount, 0) / weeklySummary.length) : 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">meals/day</Typography>
            </CardContent>
          </Card>
        </Stack>

        {weeklySummary.length === 0 && workouts.length === 0 && !loading && (
          <Card elevation={2}>
            <CardContent sx={{ textAlign: 'center', py: 8 }}>
              <Typography variant="h6" gutterBottom>No analytics data yet</Typography>
              <Typography variant="body2" color="text.secondary">
                Start logging meals and workouts to see your analytics
              </Typography>
            </CardContent>
          </Card>
        )}
      </Stack>
    </MainLayout>
  );
};

export default AnalyticsPage;

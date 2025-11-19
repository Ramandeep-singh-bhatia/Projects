import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Stack,
  IconButton,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Add, ArrowBack, ArrowForward, Today } from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '../../store';
import {
  fetchMealsByDate,
  fetchDailySummary,
  deleteMeal,
  setCurrentDate,
  selectMeals,
  selectCurrentDate,
  selectDailySummary,
  selectNutritionLoading,
  selectNutritionError,
} from '../../features/nutrition/nutritionSlice';
import MainLayout from '../../components/layout/MainLayout';
import NutritionSummaryCard from '../../components/nutrition/NutritionSummaryCard';
import MealCard from '../../components/nutrition/MealCard';
import AddMealDialog from '../../components/nutrition/AddMealDialog';
import type { Meal } from '../../types/nutrition.types';

const NutritionPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const meals = useAppSelector(selectMeals);
  const currentDate = useAppSelector(selectCurrentDate);
  const dailySummary = useAppSelector(selectDailySummary);
  const loading = useAppSelector(selectNutritionLoading);
  const error = useAppSelector(selectNutritionError);

  const [addMealOpen, setAddMealOpen] = useState(false);

  useEffect(() => {
    loadData();
  }, [currentDate]);

  const loadData = async () => {
    await Promise.all([
      dispatch(fetchMealsByDate(currentDate)),
      dispatch(fetchDailySummary(currentDate)),
    ]);
  };

  const handlePreviousDay = () => {
    const date = new Date(currentDate);
    date.setDate(date.getDate() - 1);
    dispatch(setCurrentDate(date.toISOString().split('T')[0]));
  };

  const handleNextDay = () => {
    const date = new Date(currentDate);
    date.setDate(date.getDate() + 1);
    dispatch(setCurrentDate(date.toISOString().split('T')[0]));
  };

  const handleToday = () => {
    dispatch(setCurrentDate(new Date().toISOString().split('T')[0]));
  };

  const handleDeleteMeal = async (mealId: number) => {
    if (window.confirm('Are you sure you want to delete this meal?')) {
      await dispatch(deleteMeal(mealId));
      loadData(); // Refresh data after deletion
    }
  };

  const handleEditMeal = (meal: Meal) => {
    // TODO: Implement edit functionality
    console.log('Edit meal:', meal);
    alert('Edit functionality coming soon!');
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    }
  };

  const groupMealsByType = () => {
    const groups: Record<string, Meal[]> = {
      BREAKFAST: [],
      LUNCH: [],
      DINNER: [],
      SNACK: [],
    };

    meals.forEach(meal => {
      if (groups[meal.mealType]) {
        groups[meal.mealType].push(meal);
      }
    });

    return groups;
  };

  const mealGroups = groupMealsByType();

  return (
    <MainLayout>
      <Stack spacing={4}>
        {/* Header */}
        <Box>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Nutrition Tracking
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Track your meals and monitor your nutrition intake
          </Typography>
        </Box>

        {/* Date Navigator */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Stack direction="row" spacing={1} alignItems="center">
            <IconButton onClick={handlePreviousDay} size="small">
              <ArrowBack />
            </IconButton>
            <Box sx={{ minWidth: 250, textAlign: 'center' }}>
              <Typography variant="h6" fontWeight="bold">
                {formatDate(currentDate)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {currentDate}
              </Typography>
            </Box>
            <IconButton onClick={handleNextDay} size="small">
              <ArrowForward />
            </IconButton>
            <Button
              variant="outlined"
              size="small"
              startIcon={<Today />}
              onClick={handleToday}
            >
              Today
            </Button>
          </Stack>

          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setAddMealOpen(true)}
            size="large"
          >
            Add Meal
          </Button>
        </Box>

        {error && (
          <Alert severity="error" onClose={() => {}}>
            {error}
          </Alert>
        )}

        {/* Nutrition Summary */}
        <NutritionSummaryCard summary={dailySummary} loading={loading} />

        {/* Meals */}
        {loading && meals.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <CircularProgress />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Loading meals...
            </Typography>
          </Box>
        ) : (
          <Stack spacing={3}>
            {Object.entries(mealGroups).map(([type, typeMeals]) => {
              if (typeMeals.length === 0) return null;

              return (
                <Box key={type}>
                  <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
                    {type.charAt(0) + type.slice(1).toLowerCase()} ({typeMeals.length})
                  </Typography>
                  <Stack spacing={2}>
                    {typeMeals.map(meal => (
                      <MealCard
                        key={meal.id}
                        meal={meal}
                        onEdit={handleEditMeal}
                        onDelete={handleDeleteMeal}
                      />
                    ))}
                  </Stack>
                </Box>
              );
            })}

            {meals.length === 0 && !loading && (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <Typography variant="h6" gutterBottom>
                  No meals logged yet
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Start tracking your nutrition by adding your first meal
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => setAddMealOpen(true)}
                >
                  Add First Meal
                </Button>
              </Box>
            )}
          </Stack>
        )}
      </Stack>

      {/* Add Meal Dialog */}
      <AddMealDialog
        open={addMealOpen}
        onClose={() => {
          setAddMealOpen(false);
          loadData(); // Refresh data after adding meal
        }}
        date={currentDate}
      />
    </MainLayout>
  );
};

export default NutritionPage;

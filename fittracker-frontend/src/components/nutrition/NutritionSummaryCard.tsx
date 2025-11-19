import React from 'react';
import { Card, CardContent, Typography, Box, LinearProgress, Stack } from '@mui/material';
import { LocalFireDepartment, Fastfood } from '@mui/icons-material';
import type { NutritionSummary } from '../../types/nutrition.types';

interface NutritionSummaryCardProps {
  summary: NutritionSummary | null;
  loading?: boolean;
}

const NutritionSummaryCard: React.FC<NutritionSummaryCardProps> = ({ summary, loading = false }) => {
  if (loading) {
    return (
      <Card elevation={2}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Loading summary...</Typography>
          <LinearProgress />
        </CardContent>
      </Card>
    );
  }

  if (!summary) {
    return (
      <Card elevation={2}>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <Fastfood sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>No nutrition data yet</Typography>
          <Typography variant="body2" color="text.secondary">
            Start logging your meals to see your nutrition summary
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const caloriesPercent = (summary.dailyTotals.totalCalories / 2200) * 100;
  const proteinPercent = (summary.dailyTotals.totalProtein / 150) * 100;
  const carbsPercent = (summary.dailyTotals.totalCarbs / 250) * 100;
  const fatPercent = (summary.dailyTotals.totalFat / 70) * 100;

  return (
    <Card elevation={2}>
      <CardContent>
        <Stack spacing={3}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <LocalFireDepartment color="error" />
            <Typography variant="h6" fontWeight="bold">
              Today's Nutrition
            </Typography>
          </Box>

          {/* Calories */}
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="body2" fontWeight="medium">Calories</Typography>
              <Typography variant="body2">
                {summary.dailyTotals.totalCalories.toFixed(0)} / {2200?.toFixed(0) || '—'} kcal
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={Math.min(caloriesPercent, 100)}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: 'grey.200',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: caloriesPercent > 100 ? 'error.main' : 'primary.main',
                },
              }}
            />
          </Box>

          {/* Macros */}
          <Stack direction="row" spacing={2}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" color="text.secondary">Protein</Typography>
              <Typography variant="h6" fontWeight="bold" color="primary.main">
                {summary.dailyTotals.totalProtein.toFixed(0)}g
              </Typography>
              <LinearProgress
                variant="determinate"
                value={Math.min(proteinPercent, 100)}
                sx={{ height: 4, borderRadius: 2, mt: 0.5 }}
              />
            </Box>

            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" color="text.secondary">Carbs</Typography>
              <Typography variant="h6" fontWeight="bold" color="warning.main">
                {summary.dailyTotals.totalCarbs.toFixed(0)}g
              </Typography>
              <LinearProgress
                variant="determinate"
                value={Math.min(carbsPercent, 100)}
                color="warning"
                sx={{ height: 4, borderRadius: 2, mt: 0.5 }}
              />
            </Box>

            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" color="text.secondary">Fat</Typography>
              <Typography variant="h6" fontWeight="bold" color="error.main">
                {summary.dailyTotals.totalFat.toFixed(0)}g
              </Typography>
              <LinearProgress
                variant="determinate"
                value={Math.min(fatPercent, 100)}
                color="error"
                sx={{ height: 4, borderRadius: 2, mt: 0.5 }}
              />
            </Box>
          </Stack>

          {/* Additional Info */}
          <Box sx={{ display: 'flex', justifyContent: 'space-around', pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">Fiber</Typography>
              <Typography variant="body1" fontWeight="medium">
                {summary.dailyTotals.totalFiber.toFixed(0)}g
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">Meals</Typography>
              <Typography variant="body1" fontWeight="medium">
                {summary.dailyTotals.mealCount}
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">Net Cal</Typography>
              <Typography variant="body1" fontWeight="medium" color={summary.dailyTotals.totalCalories > 0 ? 'success.main' : 'text.primary'}>
                {summary.dailyTotals.totalCalories.toFixed(0)}
              </Typography>
            </Box>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
};

export default NutritionSummaryCard;

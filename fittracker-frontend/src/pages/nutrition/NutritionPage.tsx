import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { Restaurant } from '@mui/icons-material';
import MainLayout from '../../components/layout/MainLayout';

const NutritionPage: React.FC = () => {
  return (
    <MainLayout>
      <Box>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Nutrition Tracking
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Track your meals and monitor your nutrition intake
        </Typography>

        <Card elevation={2}>
          <CardContent sx={{ textAlign: 'center', py: 8 }}>
            <Restaurant sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Nutrition Tracking - Coming in Phase 4
            </Typography>
            <Typography variant="body2" color="text.secondary">
              This feature will allow you to log meals, track calories, and monitor your nutritional intake.
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </MainLayout>
  );
};

export default NutritionPage;

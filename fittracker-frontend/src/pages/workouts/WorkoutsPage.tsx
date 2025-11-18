import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { FitnessCenter } from '@mui/icons-material';
import MainLayout from '../../components/layout/MainLayout';

const WorkoutsPage: React.FC = () => {
  return (
    <MainLayout>
      <Box>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Workout Tracking
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Track your workouts and monitor your fitness progress
        </Typography>

        <Card elevation={2}>
          <CardContent sx={{ textAlign: 'center', py: 8 }}>
            <FitnessCenter sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Workout Tracking - Coming in Phase 5
            </Typography>
            <Typography variant="body2" color="text.secondary">
              This feature will allow you to log workouts, track exercises, and monitor your fitness progress.
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </MainLayout>
  );
};

export default WorkoutsPage;

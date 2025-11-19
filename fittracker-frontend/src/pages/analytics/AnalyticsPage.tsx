import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { ShowChart } from '@mui/icons-material';
import MainLayout from '../../components/layout/MainLayout';

const AnalyticsPage: React.FC = () => {
  return (
    <MainLayout>
      <Box>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Analytics & Progress
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          View detailed analytics and track your progress over time
        </Typography>

        <Card elevation={2}>
          <CardContent sx={{ textAlign: 'center', py: 8 }}>
            <ShowChart sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Analytics & Progress - Coming in Phase 6
            </Typography>
            <Typography variant="body2" color="text.secondary">
              This feature will provide detailed charts, trends, and insights into your fitness journey.
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </MainLayout>
  );
};

export default AnalyticsPage;

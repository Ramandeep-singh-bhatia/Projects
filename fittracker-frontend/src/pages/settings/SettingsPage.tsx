import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { Settings } from '@mui/icons-material';
import MainLayout from '../../components/layout/MainLayout';

const SettingsPage: React.FC = () => {
  return (
    <MainLayout>
      <Box>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Settings
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Manage your account settings and preferences
        </Typography>

        <Card elevation={2}>
          <CardContent sx={{ textAlign: 'center', py: 8 }}>
            <Settings sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Settings - Coming in Phase 8
            </Typography>
            <Typography variant="body2" color="text.secondary">
              This feature will allow you to customize your app preferences and account settings.
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </MainLayout>
  );
};

export default SettingsPage;

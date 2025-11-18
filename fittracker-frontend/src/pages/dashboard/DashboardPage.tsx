import React from 'react';
import { Box, Container, Typography, Button, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../store';
import { logout, selectCurrentUser } from '../../features/auth/authSlice';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const user = useAppSelector(selectCurrentUser);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        py: 4,
      }}
    >
      <Container maxWidth="lg">
        <Paper
          elevation={3}
          sx={{
            p: 4,
            borderRadius: 2,
          }}
        >
          <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">
            Welcome to FitTracker Pro!
          </Typography>

          {user && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h5" gutterBottom>
                Hello, {user.firstName} {user.lastName}!
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                Email: {user.email}
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                Member since: {new Date(user.createdAt).toLocaleDateString()}
              </Typography>
            </Box>
          )}

          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              🎉 Phase 1: Authentication - Complete!
            </Typography>
            <Typography variant="body1" paragraph>
              You have successfully logged in to FitTracker Pro. The authentication system is working correctly.
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              The full dashboard with nutrition tracking, workout management, and analytics will be implemented in the upcoming phases.
            </Typography>
          </Box>

          <Box sx={{ mt: 4 }}>
            <Button variant="contained" color="primary" onClick={handleLogout} size="large">
              Logout
            </Button>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default DashboardPage;

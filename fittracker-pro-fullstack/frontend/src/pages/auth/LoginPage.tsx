import React from 'react';
import { Box, Container } from '@mui/material';
import LoginForm from '../../components/auth/LoginForm';

const LoginPage: React.FC = () => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Container maxWidth="sm">
        <LoginForm />
      </Container>
    </Box>
  );
};

export default LoginPage;

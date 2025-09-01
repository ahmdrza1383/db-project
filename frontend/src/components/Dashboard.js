// frontend/src/components/Dashboard.js
import React from 'react';
import { Container, Typography, Box, Button } from '@mui/material';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  return (
    <Container maxWidth="md" sx={{ textAlign: 'center', mt: 5 }}>
      <Typography variant="h4" gutterBottom>
        به پنل کاربری خود خوش آمدید!
      </Typography>
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 3 }}>
        <Button variant="contained" component={Link} to="/search">
          جستجوی بلیط ✈️
        </Button>
        <Button variant="outlined" component={Link} to="/profile">
          پروفایل من 👤
        </Button>
        <Button variant="contained" color="error" onClick={() => {
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          window.location.href = '/';
        }}>
          خروج
        </Button>
      </Box>
    </Container>
  );
};

export default Dashboard;
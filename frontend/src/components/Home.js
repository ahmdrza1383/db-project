// src/components/Home.js
import React, { useState, useEffect } from 'react';
import { Typography, Container, Button, Box } from '@mui/material';
import { Link } from 'react-router-dom';

function Home() {
    const [currentUser, setCurrentUser] = useState(null);

    useEffect(() => {
        const userInfo = localStorage.getItem('userInfo');

        if (userInfo) {
            setCurrentUser(JSON.parse(userInfo));
        }
    }, []);

    return (
        <Container>
            <Box sx={{ my: 4, textAlign: 'center' }}>
                <Typography variant="h4" component="h1" gutterBottom>

                    {currentUser ? (
                        `به سایت سفر با ما خوش آمدید، ${currentUser.name}!`
                    ) : (
                        'به پلتفرم فروش بلیت خوش آمدید'
                    )}
                </Typography>

                {!currentUser && (
                    <Box>
                        <Button component={Link} to="/login" variant="contained" color="primary" sx={{ mx: 1 }}>
                            ورود
                        </Button>
                        <Button component={Link} to="/signup" variant="outlined" color="primary" sx={{ mx: 1 }}>
                            ثبت نام
                        </Button>
                    </Box>
                )}
            </Box>
        </Container>
    );
}

export default Home;
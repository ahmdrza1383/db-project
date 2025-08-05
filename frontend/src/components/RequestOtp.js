import React, { useState } from 'react';
import axios from 'axios';
import { Container, TextField, Button, Typography, Box, Alert } from '@mui/material';

function RequestOtp({ onOtpSent }) {
    const [identifier, setIdentifier] = useState('');
    const [error, setError] = useState(null);
    const [message, setMessage] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setMessage(null);

        try {
            await axios.post('http://localhost:8000/api-test/request-otp/', { identifier });
            setMessage('کد یکبار مصرف با موفقیت ارسال شد. لطفاً ایمیل خود را چک کنید.');

            onOtpSent(identifier);

        } catch (err) {
            const errorMessage = err.response?.data?.message || 'خطایی در ارسال کد رخ داد.';
            setError(errorMessage);
        }
    };

    return (
        <Container maxWidth="xs">
            <Box sx={{ marginTop: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Typography component="h1" variant="h5">
                    ورود به حساب کاربری
                </Typography>
                <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
                    برای ورود، ایمیل یا شماره تلفن خود را وارد کنید.
                </Typography>
                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        id="identifier"
                        label="ایمیل یا شماره تلفن"
                        name="identifier"
                        value={identifier}
                        onChange={(e) => setIdentifier(e.target.value)}
                        autoFocus
                    />
                    <Button type="submit" fullWidth variant="contained" sx={{ mt: 3, mb: 2 }}>
                        ارسال کد
                    </Button>
                    {message && <Alert severity="success">{message}</Alert>}
                    {error && <Alert severity="error">{error}</Alert>}
                </Box>
            </Box>
        </Container>
    );
}

export default RequestOtp;
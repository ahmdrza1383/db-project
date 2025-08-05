import React, { useState } from 'react';
import axios from 'axios';
import { Container, TextField, Button, Typography, Box, Alert } from '@mui/material';

function VerifyOtp({ identifier }) {
    const [otpCode, setOtpCode] = useState('');
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        try {
            const response = await axios.post('http://localhost:8000/api-test/verify-otp/', {
                identifier: identifier,
                otp_code: otpCode
            });

            const { access_token, refresh_token, user_info } = response.data;
            localStorage.setItem('accessToken', access_token);
            localStorage.setItem('refreshToken', refresh_token);
            localStorage.setItem('userInfo', JSON.stringify(user_info));

            window.location.href = '/';

        } catch (err) {
            const errorMessage = err.response?.data?.message || 'خطا در تایید کد.';
            setError(errorMessage);
        }
    };

    return (
        <Container maxWidth="xs">
            <Box sx={{ marginTop: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Typography component="h1" variant="h5">
                    تایید کد یکبار مصرف
                </Typography>
                <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
                    کد ارسال شده به {identifier} را وارد کنید.
                </Typography>
                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        id="otp_code"
                        label="کد تایید"
                        name="otp_code"
                        value={otpCode}
                        onChange={(e) => setOtpCode(e.target.value)}
                        autoFocus
                    />
                    <Button type="submit" fullWidth variant="contained" sx={{ mt: 3, mb: 2 }}>
                        ورود
                    </Button>
                    {error && <Alert severity="error">{error}</Alert>}
                </Box>
            </Box>
        </Container>
    );
}

export default VerifyOtp;
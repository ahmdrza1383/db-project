import React, { useState } from 'react';
import axios from 'axios';
import { Container, TextField, Button, Typography, Box, Alert } from '@mui/material';

function Register() {
    // State برای نگهداری مقادیر فرم، دقیقاً مطابق با API شما
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        name: '',
        email: '',
        phone_number: '' // این فیلد اختیاری است
    });

    // State برای نمایش پیام‌های موفقیت یا خطا
    const [message, setMessage] = useState(null);
    const [error, setError] = useState(null);

    // تابعی که با تغییر هر فیلد فرم، state را آپدیت می‌کند
    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    // تابعی که هنگام ارسال فرم اجرا می‌شود
    const handleSubmit = async (e) => {
        e.preventDefault(); // جلوگیری از رفرش شدن صفحه
        setMessage(null);
        setError(null);

        // آماده‌سازی داده‌ها برای ارسال (فیلد تلفن اگر خالی بود ارسال نمی‌شود)
        const payload = { ...formData };
        if (!payload.phone_number) {
            delete payload.phone_number;
        }

        try {
            // ارسال درخواست POST به آدرس صحیح API شما
            const response = await axios.post('http://localhost:8000/api-test/user-signup/', payload);

            console.log('Success:', response.data);
            setMessage('ثبت‌نام شما با موفقیت انجام شد!');

        } catch (err) {
            console.error('Error:', err.response ? err.response.data : err.message);
            // نمایش پیام خطای دریافتی از بک‌اند
            const errorMessage = err.response && err.response.data && err.response.data.message
                ? err.response.data.message
                : 'خطایی در ارتباط با سرور رخ داد. لطفاً دوباره تلاش کنید.';
            setError(errorMessage);
        }
    };

    return (
        <Container maxWidth="xs">
            <Box sx={{ marginTop: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Typography component="h1" variant="h5">
                    ثبت‌نام کاربر جدید
                </Typography>
                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
                    <TextField margin="normal" required fullWidth label="نام و نام خانوادگی" name="name" value={formData.name} onChange={handleChange} autoFocus />
                    <TextField margin="normal" required fullWidth label="نام کاربری" name="username" value={formData.username} onChange={handleChange} />
                    <TextField margin="normal" required fullWidth label="آدرس ایمیل" name="email" type="email" value={formData.email} onChange={handleChange} />
                    <TextField margin="normal" required fullWidth label="شماره تلفن" name="phone_number" value={formData.phone_number} onChange={handleChange} />
                    <TextField margin="normal" required fullWidth name="password" label="رمز عبور" type="password" value={formData.password} onChange={handleChange} />

                    <Button type="submit" fullWidth variant="contained" sx={{ mt: 3, mb: 2 }}>
                        ثبت‌نام
                    </Button>

                    {message && <Alert severity="success">{message}</Alert>}
                    {error && <Alert severity="error">{error}</Alert>}
                </Box>
            </Box>
        </Container>
    );
}

export default Register;
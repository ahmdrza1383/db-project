// src/components/admin/AdminDashboard.js
import React, {useState, useEffect} from 'react';
import {Container, Typography, Paper, Box, Button, Grid, Card, CardContent, CardActions} from '@mui/material';
import {Link, useNavigate} from 'react-router-dom';
import AssessmentIcon from '@mui/icons-material/Assessment'; // آیکون برای گزارش‌ها
import PeopleIcon from '@mui/icons-material/People';

function AdminDashboard() {
    // State برای نگهداری اطلاعات کاربر ادمین
    const [adminUser, setAdminUser] = useState(null);
    const navigate = useNavigate();

    // در زمان بارگذاری صفحه، اطلاعات ادمین را از حافظه مرورگر می‌خوانیم
    useEffect(() => {
        const userInfoString = localStorage.getItem('userInfo');
        if (userInfoString) {
            setAdminUser(JSON.parse(userInfoString));
        }
    }, []);

    // تابع برای خروج از سیستم
    const handleLogout = () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('userInfo');
        // هدایت به صفحه ورود برای تجربه کاربری بهتر
        navigate('/login');
    };

    return (
        <Container maxWidth="lg" sx={{mt: 4}}>
            {/* بخش هدر داشبورد: خوش‌آمدگویی و دکمه خروج */}
            <Box sx={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4}}>
                <Typography variant="h4" component="h1">
                    {adminUser ? `سلام، ${adminUser.name}!` : 'داشبورد ادمین'}
                </Typography>
                <Button variant="outlined" color="error" onClick={handleLogout}>
                    خروج از حساب کاربری
                </Button>
            </Box>

            <Typography variant="h5" gutterBottom>
                پنل مدیریت
            </Typography>

            {/* بخش اصلی داشبورد با چیدمان Grid */}
            <Grid container spacing={3}>
                {/* کارت مدیریت گزارش‌ها */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Box sx={{display: 'flex', alignItems: 'center', mb: 1}}>
                                <AssessmentIcon color="primary" sx={{mr: 1}}/>
                                <Typography variant="h6">مدیریت گزارش‌ها</Typography>
                            </Box>
                            <Typography color="text.secondary">
                                در این بخش می‌توانید گزارش‌های ثبت‌شده توسط کاربران را مشاهده، فیلتر و به آن‌ها پاسخ
                                دهید.
                            </Typography>
                        </CardContent>
                        <CardActions>
                            <Button component={Link} to="/admin/reports" size="small">مشاهده گزارش‌ها</Button>
                        </CardActions>
                    </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Box sx={{display: 'flex', alignItems: 'center', mb: 1}}>
                                <PeopleIcon color="primary" sx={{mr: 1}}/>
                                <Typography variant="h6">مدیریت درخواست‌ها</Typography>
                            </Box>
                            <Typography color="text.secondary">
                                درخواست‌های کنسلی یا تغییر تاریخ کاربران را در این بخش بررسی، تایید یا رد کنید.
                            </Typography>
                        </CardContent>
                        <CardActions>
                            <Button component={Link} to="/admin/requests" size="small">مشاهده درخواست‌ها</Button>
                        </CardActions>
                    </Card>
                </Grid>
            </Grid>
        </Container>
    );
}

export default AdminDashboard;
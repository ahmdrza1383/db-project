import React, {useState, useEffect, useCallback} from 'react';
import axios from 'axios';
import {useNavigate} from 'react-router-dom';
import {
    Container, Typography, Paper, Box, Grid, TextField, Button,
    CircularProgress, Alert, Avatar, Tabs, Tab, Select, MenuItem, FormControl, InputLabel, InputAdornment, Divider
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';

function UserProfile() {
    const navigate = useNavigate();
    // --- State ها ---
    const [user, setUser] = useState(null);
    const [editMode, setEditMode] = useState(false);
    const [formData, setFormData] = useState({});
    const [walletAmount, setWalletAmount] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [cities, setCities] = useState([]);
    const [activeTab, setActiveTab] = useState(0);

    // --- توابع ---
    const loadInitialData = useCallback(async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('accessToken');
            if (!token) {
                setError("توکن دسترسی یافت نشد. لطفاً دوباره وارد شوید.");
                setLoading(false);
                return;
            }

            // API call to get the latest user info from the database
            const userResponse = await axios.get('http://localhost:8000/api-test/user-profile/', {
                headers: {Authorization: `Bearer ${token}`}
            });
            const latestUserInfo = userResponse.data.user_info;

            setUser(latestUserInfo);
            setFormData({
                name: latestUserInfo.name || '',
                phone_number: latestUserInfo.phone_number || '',
                city_id: latestUserInfo.city_id || '',
                date_of_birth: latestUserInfo.date_of_birth || '',
                new_username: latestUserInfo.username || '',
                new_email: latestUserInfo.email || '',
                new_password: '',
                authentication_method: latestUserInfo.authentication_method || 'EMAIL',
            });

            // API call to get the list of cities
            const citiesResponse = await axios.get('http://localhost:8000/api-test/cities-list/', {
                headers: {Authorization: `Bearer ${token}`}
            });
            setCities(citiesResponse.data.data);

        } catch (err) {
            setError("خطا در بارگذاری اطلاعات. لطفاً دوباره وارد شوید.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadInitialData();
    }, [loadInitialData]);

    const handleInputChange = (e) => setFormData({...formData, [e.target.name]: e.target.value});
    const handleTabChange = (event, newValue) => setActiveTab(newValue);

    const handleUpdateProfile = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setSuccess(null);

        const payload = {};
        // مقادیر نهایی پاک‌سازی‌شده
        const cleaned = {
            name: (formData.name ?? '').trim(),
            phone_number: (formData.phone_number ?? '').trim(),
            city_id: formData.city_id ?? '',
            date_of_birth: (formData.date_of_birth ?? '').trim(),
            new_username: (formData.new_username ?? '').trim(),
            new_email: (formData.new_email ?? '').trim().toLowerCase(),
            new_password: (formData.new_password ?? '').trim(),
            authentication_method: (formData.authentication_method ?? '').trim().toUpperCase(),
        };

        // فیلدهای معمولی
        if (cleaned.name && cleaned.name !== (user.name ?? '')) payload.name = cleaned.name;
        if (cleaned.phone_number && cleaned.phone_number !== (user.phone_number ?? '')) payload.phone_number = cleaned.phone_number;
        if ((cleaned.city_id || cleaned.city_id === 0) && cleaned.city_id !== (user.city_id ?? '')) payload.city_id = cleaned.city_id;
        if (cleaned.date_of_birth && cleaned.date_of_birth !== (user.date_of_birth ?? '')) payload.date_of_birth = cleaned.date_of_birth;

        // فیلدهای خاص طبق API
        if (cleaned.new_username && cleaned.new_username !== (user.username ?? '')) payload.new_username = cleaned.new_username;
        if (cleaned.new_email && cleaned.new_email !== (user.email ?? '').toLowerCase()) payload.new_email = cleaned.new_email;
        if (cleaned.new_password) payload.new_password = cleaned.new_password;
        if (cleaned.authentication_method && cleaned.authentication_method !== (user.authentication_method ?? '').toUpperCase()) {
            payload.new_authentication_method = cleaned.authentication_method;
        }

        if (Object.keys(payload).length === 0) {
            setSuccess("هیچ تغییری برای ذخیره وجود ندارد.");
            setEditMode(false);
            setLoading(false);
            return;
        }

        try {
            const token = localStorage.getItem('accessToken');
            const response = await axios.patch(
                'http://localhost:8000/api-test/user-update-profile/',
                payload,
                {headers: {Authorization: `Bearer ${token}`, 'Content-Type': 'application/json'}}
            );

            const updatedUserInfo = response.data.user_info;

            if (response.data.access_token) {
                localStorage.setItem('accessToken', response.data.access_token);
                localStorage.setItem('refreshToken', response.data.refresh_token);
            }

            localStorage.setItem('userInfo', JSON.stringify(updatedUserInfo));
            setUser(updatedUserInfo);
            setSuccess(response.data.message || "پروفایل شما با موفقیت به‌روزرسانی شد.");
            setEditMode(false);
        } catch (err) {
            setError(err.response?.data?.message || "خطا در به‌روزرسانی پروفایل.");
        } finally {
            setLoading(false);
        }
    };

    const handleAddToWallet = async () => {
        if (!walletAmount || Number(walletAmount) <= 0 || !Number.isFinite(Number(walletAmount))) {
            setError("لطفاً یک مبلغ معتبر وارد کنید.");
            return;
        }
        setLoading(true);
        setError(null);
        setSuccess(null);
        try {
            const token = localStorage.getItem('accessToken');
            const response = await axios.patch(
                'http://localhost:8000/api-test/user-update-profile/',
                {add_to_wallet_balance: parseInt(walletAmount, 10)},
                {headers: {Authorization: `Bearer ${token}`, 'Content-Type': 'application/json'}}
            );
            const updatedUserInfo = response.data.user_info;
            localStorage.setItem('userInfo', JSON.stringify(updatedUserInfo));
            setUser(updatedUserInfo);
            setSuccess(`مبلغ ${Number(walletAmount).toLocaleString()} تومان با موفقیت به کیف پول شما اضافه شد.`);
            setWalletAmount('');
        } catch (err) {
            setError(err.response?.data?.message || "خطا در افزایش موجودی.");
        } finally {
            setLoading(false);
        }
    };

    if (loading && !user) return <Box sx={{display: 'flex', justifyContent: 'center', mt: 5}}><CircularProgress/></Box>;
    if (error && !user) return <Container><Alert severity="error" sx={{mt: 4}}>{error}</Alert></Container>;
    if (!user) return null;

    return (
        <Container maxWidth="lg" sx={{mt: 4, mb: 4}}>
            <Paper elevation={3}
                   sx={{p: {xs: 2, md: 4}, mb: 4, display: 'flex', alignItems: 'center', flexWrap: 'wrap'}}>
                <Avatar sx={{width: 90, height: 90, mr: 3, bgcolor: 'primary.main', fontSize: '2.5rem'}}>
                    {user.name ? user.name.charAt(0) : <PersonIcon sx={{fontSize: 50}}/>}
                </Avatar>
                <Box sx={{flexGrow: 1}}>
                    <Typography variant="h4" component="h1">{user.name}</Typography>
                    <Typography variant="subtitle1" color="text.secondary">{user.email}</Typography>
                </Box>
            </Paper>

            {error && <Alert severity="error" sx={{mb: 2}}>{error}</Alert>}
            {success && <Alert severity="success" sx={{mb: 2}}>{success}</Alert>}

            <Box sx={{borderBottom: 1, borderColor: 'divider'}}>
                <Tabs value={activeTab} onChange={handleTabChange} aria-label="profile tabs">
                    <Tab label="اطلاعات شخصی"/>
                    <Tab label="تنظیمات حساب و امنیت"/>
                    <Tab label="مدیریت کیف پول"/>
                </Tabs>
            </Box>

            <Box component="form" onSubmit={handleUpdateProfile}>
                {activeTab === 0 && (
                    <Paper elevation={0} sx={{p: 3, mt: 3}}>
                        <Box sx={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2}}>
                            <Typography variant="h6">اطلاعات شخصی</Typography>
                            <Button variant={editMode ? "text" : "outlined"} startIcon={editMode ? null : <EditIcon/>}
                                    onClick={() => setEditMode(!editMode)}>
                                {editMode ? 'لغو' : 'ویرایش'}
                            </Button>
                        </Box>
                        <Divider sx={{mb: 3}}/>
                        <Grid container spacing={3}>
                            <Grid item xs={12} md={6}><TextField fullWidth label="نام و نام خانوادگی" name="name"
                                                                 value={formData.name} onChange={handleInputChange}
                                                                 disabled={!editMode}/></Grid>
                            <Grid item xs={12} md={6}><TextField fullWidth label="شماره تلفن" name="phone_number"
                                                                 value={formData.phone_number}
                                                                 onChange={handleInputChange}
                                                                 disabled={!editMode}/></Grid>
                            <Grid item xs={12} md={6}>
                                <FormControl fullWidth disabled={!editMode}>
                                    <InputLabel>شهر</InputLabel>
                                    <Select name="city_id" value={formData.city_id || ''} label="شهر"
                                            onChange={handleInputChange}>
                                        <MenuItem value=""><em>انتخاب نشده</em></MenuItem>
                                        {cities.map(city => <MenuItem key={city.location_id}
                                                                      value={city.location_id}>{city.province} - {city.city}</MenuItem>)}
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={12} md={6}><TextField fullWidth label="تاریخ تولد" name="date_of_birth"
                                                                 type="date" value={formData.date_of_birth || ''}
                                                                 onChange={handleInputChange} disabled={!editMode}
                                                                 InputLabelProps={{shrink: true}}/></Grid>
                        </Grid>
                    </Paper>
                )}

                {activeTab === 1 && (
                    <Paper elevation={0} sx={{p: 3, mt: 3}}>
                        <Box sx={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2}}>
                            <Typography variant="h6">تنظیمات حساب و امنیت</Typography>
                            {!editMode && <Button variant="outlined" startIcon={<EditIcon/>}
                                                  onClick={() => setEditMode(true)}>ویرایش</Button>}
                        </Box>
                        <Divider sx={{mb: 3}}/>
                        <Grid container spacing={3}>
                            <Grid item xs={12} md={6}><TextField fullWidth label="نام کاربری جدید" name="new_username"
                                                                 value={formData.new_username}
                                                                 onChange={handleInputChange} disabled={!editMode}
                                                                 helperText="برای تغییر، نام کاربری جدید را وارد کنید"/></Grid>
                            <Grid item xs={12} md={6}><TextField fullWidth label="ایمیل جدید" name="new_email"
                                                                 type="email" value={formData.new_email}
                                                                 onChange={handleInputChange} disabled={!editMode}
                                                                 helperText="برای تغییر، ایمیل جدید را وارد کنید"/></Grid>
                            <Grid item xs={12} md={6}><TextField fullWidth label="رمز عبور جدید" name="new_password"
                                                                 type="password" value={formData.new_password}
                                                                 onChange={handleInputChange} disabled={!editMode}
                                                                 helperText="برای تغییر، رمز عبور جدید را وارد کنید"/></Grid>
                            <Grid item xs={12} md={6}>
                                <FormControl fullWidth disabled={!editMode}>
                                    <InputLabel>روش ورود پیش‌فرض</InputLabel>
                                    <Select name="authentication_method" value={formData.authentication_method}
                                            label="روش ورود پیش‌فرض" onChange={handleInputChange}>
                                        <MenuItem value="EMAIL">ایمیل</MenuItem>
                                        <MenuItem value="PHONE_NUMBER">شماره تلفن</MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                        </Grid>
                    </Paper>
                )}

                {editMode && (
                    <Box sx={{mt: 3, display: 'flex', justifyContent: 'flex-end'}}>
                        <Button type="submit" startIcon={<SaveIcon/>} variant="contained" disabled={loading}>
                            {loading ? <CircularProgress size={24}/> : 'ذخیره تمام تغییرات'}
                        </Button>
                    </Box>
                )}
            </Box>

            {activeTab === 2 && (
                <Paper elevation={0} sx={{p: 3, mt: 3}}>
                    <Typography variant="h6" gutterBottom>مدیریت کیف پول</Typography>
                    <Divider sx={{mb: 3}}/>
                    <Box sx={{
                        display: 'flex',
                        alignItems: 'center',
                        p: 2,
                        background: 'linear-gradient(to right, #43a047, #66bb6a)',
                        color: 'white',
                        borderRadius: 2,
                        mb: 3
                    }}>
                        <AccountBalanceWalletIcon sx={{mr: 2, fontSize: '2.5rem'}}/>
                        <Box>
                            <Typography>موجودی فعلی</Typography>
                            <Typography variant="h5">{(user.wallet_balance || 0).toLocaleString()} تومان</Typography>
                        </Box>
                    </Box>
                    <Typography variant="subtitle1" sx={{mb: 1}}>افزایش موجودی:</Typography>
                    <TextField fullWidth label="مبلغ" name="walletAmount" type="number" value={walletAmount}
                               onChange={(e) => setWalletAmount(e.target.value)}
                               InputProps={{endAdornment: <InputAdornment position="end">تومان</InputAdornment>}}/>
                    <Button fullWidth variant="contained" color="success" startIcon={<AddCircleOutlineIcon/>}
                            sx={{mt: 2}} onClick={handleAddToWallet} disabled={loading}>
                        {loading ? <CircularProgress size={24}/> : 'افزایش موجودی'}
                    </Button>
                </Paper>
            )}
            <Button
                variant="outlined"
                color="secondary"
                sx={{mt: 2}}
                onClick={() => navigate(-1)}
            >
                بازگشت
            </Button>
        </Container>

    );
}

export default UserProfile;

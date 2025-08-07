// src/components/UserProfile.js

import React, { useState, useEffect } from 'react';
import {
  Container, Typography, TextField, Button, Box,
  Alert, CircularProgress, Select, MenuItem, InputLabel,
  FormControl, Divider
} from '@mui/material';
import { Link } from 'react-router-dom';
import axios from 'axios';

const UserProfile = () => {
  const [profile, setProfile] = useState({});
  const [editableProfile, setEditableProfile] = useState({});
  const [newPassword, setNewPassword] = useState('');
  const [addToWallet, setAddToWallet] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      setError('شما وارد نشده‌اید. لطفا ابتدا وارد شوید.');
      setLoading(false);
      return;
    }

    try {
      const response = await axios.get('http://localhost:8000/api-test/user-profile/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProfile(response.data.user_info);
      setEditableProfile({});
      setLoading(false);
    } catch {
      setError('خطا در دریافت اطلاعات پروفایل.');
      setLoading(false);
    }
  };

  const handleEditableChange = (e) => {
    setEditableProfile({ ...editableProfile, [e.target.name]: e.target.value });
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setIsUpdating(true);
    setError('');
    setSuccess('');

    const token = localStorage.getItem('accessToken');
    const updatePayload = {};

    if (editableProfile.name) updatePayload.name = editableProfile.name;
    if (editableProfile.username) updatePayload.new_username = editableProfile.username;
    if (editableProfile.email) updatePayload.new_email = editableProfile.email;
    if (editableProfile.phone_number) updatePayload.phone_number = editableProfile.phone_number;
    if (editableProfile.date_of_birth) updatePayload.date_of_birth = editableProfile.date_of_birth;
    if (editableProfile.authentication_method) updatePayload.new_authentication_method = editableProfile.authentication_method;
    if (newPassword) updatePayload.new_password = newPassword;
    if (addToWallet) updatePayload.add_to_wallet_balance = parseInt(addToWallet);

    if (Object.keys(updatePayload).length === 0) {
      setError('هیچ تغییری برای به‌روزرسانی وجود ندارد.');
      setIsUpdating(false);
      return;
    }

    try {
      const response = await axios.patch('http://localhost:8000/api-test/user-update-profile/', updatePayload, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setSuccess(response.data.message);
      setProfile(response.data.user_info);
      setEditableProfile({});
      setNewPassword('');
      setAddToWallet('');

      if (response.data.access_token) {
        localStorage.setItem('accessToken', response.data.access_token);
        localStorage.setItem('refreshToken', response.data.refresh_token);
      }

      setIsUpdating(false);
    } catch (err) {
      const errorMessage = err.response?.data?.message || 'خطای ناشناخته در به‌روزرسانی پروفایل.';
      setError(errorMessage);
      setIsUpdating(false);
    }
  };

  if (loading) {
    return (
      <Container sx={{ textAlign: 'center', mt: 5 }}>
        <CircularProgress />
        <Typography>در حال بارگذاری پروفایل...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="sm" sx={{ mt: 5 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>پروفایل کاربری</Typography>
        <Button component={Link} to="/" variant="outlined">
          بازگشت به صفحه اصلی
        </Button>
      </Box>

      {error && <Alert severity="error">{error}</Alert>}
      {success && <Alert severity="success">{success}</Alert>}

      <Typography variant="h6" sx={{ mt: 4, mb: 2 }}>وضعیت فعلی پروفایل</Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <TextField label="نام کامل" value={profile.name || ''} disabled />
        <TextField label="نام کاربری" value={profile.username || ''} disabled />
        <TextField label="ایمیل" value={profile.email || ''} disabled />
        <TextField label="شماره تلفن" value={profile.phone_number || ''} disabled />
        <TextField label="تاریخ تولد" value={profile.date_of_birth || ''} disabled />
        <TextField label="موجودی کیف پول" value={`${profile.wallet_balance || 0} تومان`} disabled />
        <TextField label="روش احراز هویت" value={profile.authentication_method || ''} disabled />
      </Box>

      <Divider sx={{ my: 4 }} />

      <Typography variant="h6" sx={{ mb: 2 }}>به‌روزرسانی پروفایل</Typography>
      <Box component="form" onSubmit={handleUpdate} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <TextField name="name" label="نام کامل جدید" value={editableProfile.name || ''} onChange={handleEditableChange} />
        <TextField name="username" label="نام کاربری جدید" value={editableProfile.username || ''} onChange={handleEditableChange} helperText="در صورت تغییر، باید دوباره وارد شوید." />
        <TextField name="email" label="ایمیل جدید" value={editableProfile.email || ''} onChange={handleEditableChange} />
        <TextField name="phone_number" label="شماره تلفن جدید" value={editableProfile.phone_number || ''} onChange={handleEditableChange} />
        <TextField name="date_of_birth" label="تاریخ تولد جدید" type="date" value={editableProfile.date_of_birth || ''} onChange={handleEditableChange} InputLabelProps={{ shrink: true }} />
        <TextField name="newPassword" label="رمز عبور جدید" type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} helperText="در صورت تغییر، باید دوباره وارد شوید." />
        <TextField name="add_to_wallet_balance" label="افزایش موجودی کیف پول" type="number" value={addToWallet} onChange={(e) => setAddToWallet(e.target.value)} />
        <FormControl fullWidth>
          <InputLabel>روش احراز هویت جدید</InputLabel>
          <Select name="authentication_method" value={editableProfile.authentication_method || ''} onChange={handleEditableChange} label="روش احراز هویت جدید">
            <MenuItem value="EMAIL">ایمیل</MenuItem>
            <MenuItem value="PHONE_NUMBER">شماره تلفن</MenuItem>
          </Select>
        </FormControl>
        <Button type="submit" variant="contained" disabled={isUpdating} sx={{ mt: 3 }}>
          {isUpdating ? <CircularProgress size={24} /> : 'به‌روزرسانی پروفایل'}
        </Button>
      </Box>
    </Container>
  );
};

export default UserProfile;

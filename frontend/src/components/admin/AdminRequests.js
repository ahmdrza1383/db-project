// src/components/admin/AdminRequests.js
import React, {useState, useEffect, useCallback} from 'react';
import axios from 'axios';
import {Link} from 'react-router-dom';
import {useNavigate} from 'react-router-dom';
import {
    Container, Typography, Paper, Box, Grid, TextField, Button,
    Select, MenuItem, InputLabel, FormControl, CircularProgress, Alert,
    List, Pagination, Card, CardContent, CardActions, Chip, Divider, Tooltip
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

// استایل برای مودال پاسخ
const modalStyle = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 400,
    bgcolor: 'background.paper',
    border: '2px solid #000',
    boxShadow: 24,
    p: 4,
};

// تابع کمکی برای نمایش وضعیت درخواست با جزئیات بیشتر
const getStatusChip = (request) => {
    if (request.is_checked) {
        if (request.is_accepted) {
            return <Chip icon={<CheckCircleIcon/>} label="تایید شده" color="success" size="small"/>;
        } else {
            return <Chip icon={<CancelIcon/>} label="رد شده" color="error" size="small"/>;
        }
    }
    return <Chip icon={<HourglassEmptyIcon/>} label="در انتظار بررسی" color="warning" size="small"/>;
};


function AdminRequests() {
    // --- State ها (بدون تغییر) ---
    const [requests, setRequests] = useState([]);
    const [filters, setFilters] = useState({username: '', ticket_id: '', status: 'PENDING'});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const requestsPerPage = 5;
    const [selectedRequest, setSelectedRequest] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [replyText, setReplyText] = useState('');
    const [replyError, setReplyError] = useState('');

    // --- توابع (بدون تغییر) ---
    const fetchRequests = useCallback(async (currentFilters) => {
        setLoading(true);
        setError(null);
        try {
            const token = localStorage.getItem('accessToken');
            const cleanFilters = Object.fromEntries(Object.entries(currentFilters).filter(([_, v]) => v !== ''));
            const response = await axios.post(
                'http://localhost:8000/api-test/admin/requests/',
                cleanFilters,
                {headers: {Authorization: `Bearer ${token}`}}
            );
            setRequests(response.data.data);
            setPage(1);
        } catch (err) {
            setError(err.response?.data?.message || 'خطا در دریافت درخواست‌ها.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchRequests(filters);
    }, [fetchRequests]);

    const handleFilterChange = (e) => setFilters({...filters, [e.target.name]: e.target.value});
    const handleFilterSubmit = (e) => {
        e.preventDefault();
        fetchRequests(filters);
    };
    const handleOpenModal = (request) => {
        if (!request.is_checked) {
            setSelectedRequest(request);
            setIsModalOpen(true);
            setReplyText('');
            setReplyError('');
        }
    };
    const handleCloseModal = () => setIsModalOpen(false);
    const handleAction = async (requestId, action) => {
        const url = `http://localhost:8000/api-test/admin/requests/${requestId}/${action}/`;
        try {
            const token = localStorage.getItem('accessToken');
            await axios.post(url, {}, {headers: {Authorization: `Bearer ${token}`}});
            fetchRequests(filters);
        } catch (err) {
            setError(`خطا در ${action === 'approve' ? 'قبول' : 'رد'} درخواست.`);
            console.error(err);
        }
    };

    const indexOfLastRequest = page * requestsPerPage;
    const indexOfFirstRequest = indexOfLastRequest - requestsPerPage;
    const currentRequests = requests.slice(indexOfFirstRequest, indexOfLastRequest);
    const handlePageChange = (event, value) => setPage(value);

    return (
        <Container maxWidth="lg" sx={{mt: 4}}>
            <Button
                component={Link}
                to="/admin/dashboard"
                variant="outlined"
                startIcon={<ArrowBackIcon/>}
                sx={{mb: 2}}
            >
                بازگشت به داشبورد
            </Button>

            <Typography variant="h4" component="h1" gutterBottom>
                مدیریت درخواست‌های کاربران
            </Typography>

            {/* پنل فیلتر (بدون تغییر) */}
            <Paper sx={{p: 2, mb: 4}} component="form" onSubmit={handleFilterSubmit}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} sm={4}><TextField fullWidth label="نام کاربری" name="username"
                                                         value={filters.username} onChange={handleFilterChange}/></Grid>
                    <Grid item xs={12} sm={4}><TextField fullWidth label="شماره تیکت" name="ticket_id" type="number"
                                                         value={filters.ticket_id}
                                                         onChange={handleFilterChange}/></Grid>
                    <Grid item xs={12} sm={4}>
                        <FormControl fullWidth>
                            <InputLabel>وضعیت درخواست</InputLabel>
                            <Select name="status" value={filters.status} label="وضعیت درخواست"
                                    onChange={handleFilterChange}>
                                <MenuItem value=""><em>همه</em></MenuItem>
                                <MenuItem value="PENDING">در انتظار بررسی</MenuItem>
                                <MenuItem value="APPROVED">تایید شده</MenuItem>
                                <MenuItem value="REJECTED">رد شده</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12}><Button type="submit" variant="contained" fullWidth>جستجو</Button></Grid>
                </Grid>
            </Paper>

            {/* بخش نمایش نتایج (با طراحی و جزئیات جدید) */}
            {loading ? (
                <Box sx={{display: 'flex', justifyContent: 'center', mt: 5}}><CircularProgress/></Box>
            ) : error ? (
                <Alert severity="error">{error}</Alert>
            ) : (
                <Paper sx={{p: 2}}>
                    <Typography variant="h6" gutterBottom>لیست درخواست‌ها ({requests.length})</Typography>
                    <List>
                        {currentRequests.length > 0 ? currentRequests.map((req) => (
                            <Card key={req.request_id} sx={{mb: 2, background: req.is_checked ? '#f7f7f7' : '#fff'}}>
                                <CardContent>
                                    <Box sx={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center',
                                        mb: 2
                                    }}>
                                        <Typography variant="subtitle1" component="div">
                                            درخواست #{req.request_id} از کاربر: <strong>{req.username}</strong>
                                        </Typography>
                                        {getStatusChip(req)}
                                    </Box>
                                    <Grid container spacing={2}>
                                        <Grid item xs={6}><Typography
                                            color="text.secondary"><strong>موضوع:</strong> {req.request_subject === 'CANCEL' ? 'کنسلی' : 'تغییر تاریخ'}
                                        </Typography></Grid>
                                        <Grid item xs={6}><Typography color="text.secondary"><strong>تاریخ
                                            درخواست:</strong> {new Date(req.requested_at).toLocaleString('fa-IR')}
                                        </Typography></Grid>
                                        <Grid item xs={6}><Typography color="text.secondary"><strong>شماره
                                            رزرو:</strong> #{req.reservation_id}</Typography></Grid>
                                        <Grid item xs={6}><Typography color="text.secondary"><strong>شماره
                                            تیکت:</strong> #{req.ticket_id}</Typography></Grid>
                                    </Grid>
                                    <Tooltip title="متن درخواست کاربر" placement="top-start">
                                        <Typography variant="body2" sx={{
                                            mt: 2,
                                            p: 1.5,
                                            borderRadius: 1,
                                            background: '#fff',
                                            border: '1px solid #eee'
                                        }}>
                                            {req.request_text}
                                        </Typography>
                                    </Tooltip>
                                </CardContent>
                                {!req.is_checked && (
                                    <>
                                        <Divider/>
                                        <CardActions sx={{justifyContent: 'flex-end', p: 2}}>
                                            <Button size="small" color="error" variant="outlined"
                                                    onClick={() => handleAction(req.request_id, 'reject')}>
                                                رد کردن
                                            </Button>
                                            <Button size="small" color="success" variant="contained"
                                                    onClick={() => handleAction(req.request_id, 'approve')}>
                                                قبول کردن
                                            </Button>
                                        </CardActions>
                                    </>
                                )}
                            </Card>
                        )) : (
                            <Typography sx={{textAlign: 'center', p: 2}}>هیچ درخواستی یافت نشد.</Typography>
                        )}
                    </List>
                    {requests.length > requestsPerPage && (
                        <Box sx={{display: 'flex', justifyContent: 'center', mt: 3}}>
                            <Pagination count={Math.ceil(requests.length / requestsPerPage)} page={page}
                                        onChange={handlePageChange} color="primary"/>
                        </Box>
                    )}
                </Paper>
            )}
        </Container>
    );
}

export default AdminRequests;
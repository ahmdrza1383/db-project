import {Link} from 'react-router-dom';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import React, {useState, useEffect, useCallback} from 'react';
import axios from 'axios';
import {
    Container, Typography, Paper, Box, Grid, TextField, Button,
    Select, MenuItem, InputLabel, FormControl, CircularProgress, Alert,
    List, ListItemText, Divider, Pagination, Modal, Fade, Backdrop, Card, CardContent, Chip
} from '@mui/material';

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

function AdminReports() {
    // --- State های اصلی ---
    const [reports, setReports] = useState([]);
    const [filters, setFilters] = useState({
        username: '',
        ticket_id: '',
        report_type: '',
        report_status: '',
        reservation_id: ''
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // --- State های صفحه‌بندی ---
    const [page, setPage] = useState(1);
    const reportsPerPage = 5;

    // --- State های مودال پاسخ ---
    const [selectedReport, setSelectedReport] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [replyText, setReplyText] = useState('');
    const [replyError, setReplyError] = useState('');

    // --- توابع ---

    const fetchReports = useCallback(async (currentFilters) => {
        setLoading(true);
        setError(null);
        try {
            const token = localStorage.getItem('accessToken');
            if (!token) {
                setError("شما وارد نشده‌اید یا توکن شما نامعتبر است.");
                setLoading(false);
                return;
            }
            const cleanFilters = Object.fromEntries(
                Object.entries(currentFilters).filter(([_, v]) => v !== '')
            );
            const response = await axios.post(
                'http://localhost:8000/api-test/admin/reports/',
                cleanFilters,
                {headers: {Authorization: `Bearer ${token}`}}
            );
            setReports(response.data.data);
            setPage(1);
        } catch (err) {
            const errorMessage = err.response?.data?.message || 'خطا در دریافت گزارش‌ها.';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchReports(filters);
    }, [fetchReports]);

    const handleFilterChange = (e) => {
        setFilters({...filters, [e.target.name]: e.target.value});
    };
    const handleFilterSubmit = (e) => {
        e.preventDefault();
        fetchReports(filters);
    };

    const handleOpenModal = (report) => {
        if (report.report_status !== 'CHECKED') {
            setSelectedReport(report);
            setIsModalOpen(true);
            setReplyText('');
            setReplyError('');
        }
    };
    const handleCloseModal = () => setIsModalOpen(false);

    const handleReplySubmit = async () => {
        if (!replyText.trim()) {
            setReplyError('متن پاسخ نمی‌تواند خالی باشد.');
            return;
        }
        try {
            const token = localStorage.getItem('accessToken');
            await axios.patch(
                `http://localhost:8000/api-test/admin/reports/${selectedReport.report_id}/manage/`,
                {admin_response: replyText},
                {headers: {Authorization: `Bearer ${token}`}}
            );
            handleCloseModal();
            fetchReports(filters);
        } catch (err) {
            setReplyError(err.response?.data?.message || "خطا در ارسال پاسخ.");
        }
    };

    const indexOfLastReport = page * reportsPerPage;
    const indexOfFirstReport = indexOfLastReport - reportsPerPage;
    const currentReports = reports.slice(indexOfFirstReport, indexOfLastReport);
    const handlePageChange = (event, value) => {
        setPage(value);
    };

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
                مدیریت گزارش‌های کاربران
            </Typography>

            {/* *** این بخش پنل فیلتر است که در نسخه قبل جا افتاده بود *** */}
            <Paper sx={{p: 2, mb: 4}} component="form" onSubmit={handleFilterSubmit}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} sm={4}>
                        <TextField fullWidth label="نام کاربری" name="username" value={filters.username}
                                   onChange={handleFilterChange}/>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <TextField fullWidth label="شماره تیکت" name="ticket_id" type="number" value={filters.ticket_id}
                                   onChange={handleFilterChange}/>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <TextField fullWidth label="شماره رزرو" name="reservation_id" type="number"
                                   value={filters.reservation_id} onChange={handleFilterChange}/>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <FormControl fullWidth>
                            <InputLabel>نوع گزارش</InputLabel>
                            <Select name="report_type" value={filters.report_type} label="نوع گزارش"
                                    onChange={handleFilterChange}>
                                <MenuItem value=""><em>همه</em></MenuItem>
                                <MenuItem value="PAYMENT">پرداخت</MenuItem>
                                <MenuItem value="TRAVEL_DELAY">تاخیر سفر</MenuItem>
                                <MenuItem value="CANCEL">کنسلی</MenuItem>
                                <MenuItem value="OTHER">سایر</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <FormControl fullWidth>
                            <InputLabel>وضعیت گزارش</InputLabel>
                            <Select name="report_status" value={filters.report_status} label="وضعیت گزارش"
                                    onChange={handleFilterChange}>
                                <MenuItem value=""><em>همه</em></MenuItem>
                                <MenuItem value="CHECKED">بررسی شده</MenuItem>
                                <MenuItem value="UNCHECKED">بررسی نشده</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <Button type="submit" variant="contained" fullWidth sx={{height: '100%'}}>جستجو</Button>
                    </Grid>
                </Grid>
            </Paper>

            {/* بخش نمایش نتایج */}
            {loading ? (
                <Box sx={{display: 'flex', justifyContent: 'center', mt: 5}}><CircularProgress/></Box>
            ) : error ? (
                <Alert severity="error">{error}</Alert>
            ) : (
                <Paper sx={{p: 2}}>
                    <Typography variant="h6" gutterBottom>لیست گزارش‌ها ({reports.length})</Typography>
                    <List>
                        {currentReports.length > 0 ? currentReports.map((report, index) => (
                            <React.Fragment key={report.report_id}>
                                <Card sx={{mb: 2, cursor: report.report_status !== 'CHECKED' ? 'pointer' : 'default'}}
                                      onClick={() => handleOpenModal(report)}>
                                    <CardContent>
                                        <Box sx={{
                                            display: 'flex',
                                            justifyContent: 'space-between',
                                            alignItems: 'center'
                                        }}>
                                            <Typography variant="subtitle1" component="div">
                                                گزارش #{report.report_id} از
                                                کاربر: <strong>{report.report_username}</strong>
                                            </Typography>
                                            <Chip
                                                label={report.report_status === 'CHECKED' ? 'بررسی شده' : 'بررسی نشده'}
                                                color={report.report_status === 'CHECKED' ? 'success' : 'warning'}
                                                size="small"
                                            />
                                        </Box>
                                        <Typography sx={{mt: 1.5}} color="text.secondary">
                                            <strong>نوع:</strong> {report.report_type} | <strong>رزرو:</strong> #{report.reservation_id}
                                        </Typography>
                                        <Typography variant="body2"
                                                    sx={{mt: 1, p: 1, borderRadius: 1, background: '#f9f9f9'}}>
                                            {report.report_text}
                                        </Typography>
                                        {report.admin_response && (
                                            <Paper variant="outlined" sx={{mt: 2, p: 1.5, bgcolor: '#e3f2fd'}}>
                                                <Typography variant="body2" color="text.secondary">
                                                    <strong>پاسخ شما:</strong> {report.admin_response}
                                                </Typography>
                                            </Paper>
                                        )}
                                    </CardContent>
                                </Card>
                                {index < currentReports.length - 1 && <Divider/>}
                            </React.Fragment>
                        )) : (
                            <Typography sx={{textAlign: 'center', p: 2}}>هیچ گزارشی یافت نشد.</Typography>
                        )}
                    </List>
                    {reports.length > reportsPerPage && (
                        <Box sx={{display: 'flex', justifyContent: 'center', mt: 3}}>
                            <Pagination
                                count={Math.ceil(reports.length / reportsPerPage)}
                                page={page}
                                onChange={handlePageChange}
                                color="primary"
                            />
                        </Box>
                    )}
                </Paper>
            )}

            {/* مودال پاسخ به گزارش */}
            <Modal open={isModalOpen} onClose={handleCloseModal} closeAfterTransition BackdropComponent={Backdrop}
                   BackdropProps={{timeout: 500}}>
                <Fade in={isModalOpen}>
                    <Box sx={modalStyle}>
                        <Typography variant="h6" component="h2">
                            پاسخ به گزارش #{selectedReport?.report_id}
                        </Typography>
                        <TextField fullWidth multiline rows={4} label="متن پاسخ شما" value={replyText}
                                   onChange={(e) => setReplyText(e.target.value)} margin="normal"/>
                        {replyError && <Alert severity="error" sx={{mt: 1}}>{replyError}</Alert>}
                        <Box sx={{mt: 2, display: 'flex', justifyContent: 'flex-end', gap: 1}}>
                            <Button onClick={handleCloseModal}>انصراف</Button>
                            <Button variant="contained" onClick={handleReplySubmit}>ارسال پاسخ</Button>
                        </Box>
                    </Box>
                </Fade>
            </Modal>
        </Container>
    );
}

export default AdminReports;
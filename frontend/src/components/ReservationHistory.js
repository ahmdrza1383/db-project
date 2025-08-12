import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Typography, MenuItem, Select, FormControl, InputLabel, TextField, Button, Modal, Box } from '@mui/material';
import { Link } from 'react-router-dom';
import './ReservationHistory.css';

const ReservationHistory = () => {
    const accessToken = localStorage.getItem('accessToken');
    const userInfo = JSON.parse(localStorage.getItem('userInfo'));

    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // state ها برای پاپ‌آپ دیدن جواب
    const [isPopupOpen, setIsPopupOpen] = useState(false);
    const [popupTitle, setPopupTitle] = useState('');
    const [popupReports, setPopupReports] = useState([]);

    // state ها برای پاپ‌آپ ثبت گزارش
    const [isReportPopupOpen, setIsReportPopupOpen] = useState(false);
    const [reportReservationId, setReportReservationId] = useState(null);
    const [reportType, setReportType] = useState('PAYMENT');
    const [reportText, setReportText] = useState('');

    // state ها برای پاپ‌آپ ثبت درخواست لغو
    const [isCancelRequestPopupOpen, setIsCancelRequestPopupOpen] = useState(false);
    const [cancelReason, setCancelReason] = useState('');
    const [requestReservationId, setRequestReservationId] = useState(null);
    const [isCancelDetailsPopupOpen, setIsCancelDetailsPopupOpen] = useState(false);
    const [cancellationDetails, setCancellationDetails] = useState(null);

    // تابع کمکی برای تعیین کلاس CSS بر اساس وضعیت
    const getBoxClass = (operationType, buyStatus) => {
        if (operationType === 'BUY') {
            return buyStatus === 'SUCCESSFUL' ? 'successful-buy-box' : 'unsuccessful-buy-box';
        }
        return 'cancel-box';
    };

    useEffect(() => {
        const fetchHistory = async () => {
            if (!accessToken) {
                setError("برای مشاهده تاریخچه، ابتدا وارد حساب کاربری خود شوید.");
                setLoading(false);
                return;
            }

            try {
                const response = await axios.post(
                    'http://localhost:8000/api-test/user-bookings/',
                    {},
                    { headers: { Authorization: `Bearer ${accessToken}` } }
                );
                setHistory(response.data.data);
                setLoading(false);
            } catch (err) {
                console.error("Error fetching user bookings:", err.response?.data || err);
                setError("خطا در دریافت تاریخچه رزروها.");
                setLoading(false);
            }
        };

        fetchHistory();
    }, [accessToken]);

    // توابع مربوط به دکمه ها
    const handleReport = (reservationId) => {
        // این تابع دیگر گزارشی را چک نمی کند و مستقیما پاپ آپ را باز می کند
        setReportReservationId(reservationId);
        setIsReportPopupOpen(true);
    };

    const submitReport = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post(
                `http://localhost:8000/api-test/report-issue/`,
                {
                    reservation_id: reportReservationId,
                    report_type: reportType,
                    report_text: reportText,
                },
                {
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                }
            );
            alert('گزارش شما با موفقیت ثبت شد.');
            setIsReportPopupOpen(false);
            setReportText('');
            setReportType('PAYMENT');
        } catch (err) {
            alert(err.response?.data?.message || 'خطا در ثبت گزارش.');
        }
    };

    const handleViewResponse = async (reservationId) => {
        try {
            const response = await axios.get(
                `http://localhost:8000/api-test/report/status/${reservationId}/`,
                { headers: { Authorization: `Bearer ${accessToken}` } }
            );

            const data = response.data;
            if (data.status === 'info') {
                setPopupTitle('وضعیت گزارش');
                setPopupReports([]);
            } else if (data.status === 'success') {
                setPopupTitle('جزئیات گزارش‌ها');
                setPopupReports(data.reports);
            }
            setIsPopupOpen(true);
        } catch (err) {
            alert(err.response?.data?.message || 'خطا در دریافت پاسخ گزارش.');
        }
    };

    const handleRequest = async (booking) => {
        const departureTime = new Date(booking.ticket_details.departure_start);
        const now = new Date();

        if (departureTime <= now) {
            alert("نمی‌توانید برای بلیتی که تاریخ حرکت آن گذشته است، درخواست لغو ثبت کنید.");
            return;
        }

        try {
            // گام ۱: بررسی درخواست‌های قبلی
            const pendingCheckResponse = await axios.get(
                `http://localhost:8000/api-test/reservations/pending-request/${booking.reservation_id}/`,
                { headers: { Authorization: `Bearer ${accessToken}` } }
            );

            if (pendingCheckResponse.data.has_pending_request) {
                alert("شما قبلاً یک درخواست لغو برای این رزرو ثبت کرده‌اید که هنوز در حال بررسی است.");
                return;
            }

            // گام ۲: اگر درخواست قبلی وجود نداشت، جزئیات جریمه را دریافت کن
            const detailsResponse = await axios.get(
                `http://localhost:8000/api-test/reservations/${booking.reservation_id}/cancel/`,
                { headers: { Authorization: `Bearer ${accessToken}` } }
            );

            if (detailsResponse.data.status === 'success') {
                setCancellationDetails(detailsResponse.data.cancellation_info);
                setRequestReservationId(booking.reservation_id);
                setIsCancelDetailsPopupOpen(true);
            } else {
                alert(detailsResponse.data.message);
            }
        } catch (err) {
            alert(err.response?.data?.message || "خطا در دریافت جزئیات لغو.");
        }
    };

    const submitCancelRequest = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post(
                `http://localhost:8000/api-test/reservations/${requestReservationId}/requests/`,
                {
                    request_subject: 'CANCEL',
                    request_text: cancelReason
                },
                { headers: { Authorization: `Bearer ${accessToken}` } }
            );
            alert(response.data.message);
            setIsCancelDetailsPopupOpen(false);
            setCancelReason('');
        } catch (err) {
            alert(err.response?.data?.message || "خطا در ثبت درخواست لغو.");
        }
    };

    if (loading) return <Typography>در حال بارگذاری...</Typography>;
    if (error) return <Typography color="error">{error}</Typography>;

    return (
        <Container>
            <Link to="/" className="home-btn">
                بازگشت به صفحه اصلی
            </Link>

            <Typography variant="h4" gutterBottom>تاریخچه رزروهای من</Typography>
            {history.length === 0 ? (
                <Typography>شما تاکنون هیچ بلیتی رزرو نکرده‌اید.</Typography>
            ) : (
                history.map((booking) => {
                    const isBuy = booking.operation_type === 'BUY';
                    const isOwner = userInfo && userInfo.username === booking.current_owner;
                    const boxClass = getBoxClass(booking.operation_type, booking.operation_status);

                    return (
                        <div
                            key={booking.history_id}
                            className={`history-item ${boxClass}`}
                        >
                            <div className="item-details">
                                <p className="item-status">
                                    وضعیت: {
                                        isBuy
                                        ? (booking.operation_status === 'SUCCESSFUL' ? 'خرید موفق' : 'خرید ناموفق')
                                        : 'لغو شده'
                                    }
                                </p>
                                <p>شماره تاریخچه رزرو: <strong>{booking.history_id}</strong></p>
                                <p>شماره رزرو: <strong>{booking.reservation_id}</strong></p>
                                <p>مبدأ: <strong>{booking.ticket_details.origin_city}</strong></p>
                                <p>مقصد: <strong>{booking.ticket_details.destination_city}</strong></p>
                                <p>تاریخ حرکت: <strong>{new Date(booking.ticket_details.departure_start).toLocaleDateString('fa-IR')}</strong></p>
                                <p>نوع وسیله نقلیه: <strong>{booking.vehicle_type}</strong></p>
                                <p>تاریخ انجام عملیات: <strong>{new Date(booking.operation_time).toLocaleString('fa-IR')}</strong></p>
                            </div>

                            <div className="item-actions">
                                {/* این دکمه‌ها فقط برای خریدهای موفق توسط کاربر فعلی نمایش داده می شوند */}
                                {isBuy && isOwner && booking.operation_status === 'SUCCESSFUL' && (
                                    <>
                                        <Button className="action-btn" onClick={() => handleViewResponse(booking.reservation_id)}>دیدن جواب</Button>
                                        <Button className="action-btn" onClick={() => handleReport(booking.reservation_id)}>ثبت گزارش</Button>
                                        <Button
                                            className="action-btn"
                                            onClick={() => handleRequest(booking)}>
                                            ثبت درخواست لغو
                                        </Button>
                                    </>
                                )}
                            </div>
                        </div>
                    );
                })
            )}

            {/* پاپ‌آپ دیدن جواب گزارش‌ها */}
            {isPopupOpen && (
                <Modal open={isPopupOpen} onClose={() => setIsPopupOpen(false)}>
                    <Box className="confirm-popup-box">
                        <div className="popup-header">
                            <h2>{popupTitle}</h2>
                            <Button className="popup-close-btn" onClick={() => setIsPopupOpen(false)}>
                                &times;
                            </Button>
                        </div>
                        <div className="popup-body">
                            {popupReports.length > 0 ? (
                                popupReports.map((report, index) => (
                                    <div key={report.report_id} className="report-item">
                                        <h3>گزارش #{index + 1}</h3>
                                        <div className="user-report-text">
                                            <strong>متن گزارش:</strong>
                                            <p>{report.report_text}</p>
                                        </div>
                                        <div className="admin-response-text">
                                            <strong>پاسخ مدیر:</strong>
                                            <p>
                                                {report.report_status === 'UNCHECKED'
                                                    ? 'هنوز پاسخی دریافت نکرده‌اید.'
                                                    : report.admin_response || 'پاسخی ثبت نشده است.'
                                                }
                                            </p>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <p>هنوز گزارشی برای این رزرو ثبت نشده است.</p>
                            )}
                        </div>
                    </Box>
                </Modal>
            )}

            {/* پاپ‌آپ ثبت گزارش */}
            {isReportPopupOpen && (
                <Modal open={isReportPopupOpen} onClose={() => setIsReportPopupOpen(false)}>
                    <Box className="confirm-popup-box">
                        <div className="popup-header">
                            <h2>ثبت گزارش جدید</h2>
                            <Button className="popup-close-btn" onClick={() => setIsReportPopupOpen(false)}>
                                &times;
                            </Button>
                        </div>
                        <form onSubmit={submitReport} className="report-form">
                            <FormControl fullWidth margin="normal">
                                <InputLabel>موضوع گزارش</InputLabel>
                                <Select
                                    value={reportType}
                                    label="موضوع گزارش"
                                    onChange={(e) => setReportType(e.target.value)}
                                >
                                    <MenuItem value="PAYMENT">پرداخت</MenuItem>
                                    <MenuItem value="TRAVEL_DELAY">تاخیر در سفر</MenuItem>
                                    <MenuItem value="CANCEL">لغو</MenuItem>
                                    <MenuItem value="OTHER">سایر</MenuItem>
                                </Select>
                            </FormControl>
                            <TextField
                                label="متن گزارش"
                                multiline
                                rows={4}
                                fullWidth
                                margin="normal"
                                value={reportText}
                                onChange={(e) => setReportText(e.target.value)}
                                required
                            />
                            <Button type="submit" variant="contained" color="primary" sx={{ mt: 2 }}>
                                ارسال گزارش
                            </Button>
                        </form>
                    </Box>
                </Modal>
            )}

            {/* پاپ‌آپ جزئیات لغو و ثبت درخواست */}
            {isCancelDetailsPopupOpen && cancellationDetails && (
                <Modal open={isCancelDetailsPopupOpen} onClose={() => setIsCancelDetailsPopupOpen(false)}>
                    <Box className="confirm-popup-box">
                        <div className="popup-header">
                            <h2>ثبت درخواست لغو</h2>
                            <Button className="popup-close-btn" onClick={() => setIsCancelDetailsPopupOpen(false)}>
                                &times;
                            </Button>
                        </div>
                        <div className="popup-body">
                            <p><strong>قیمت بلیت:</strong> {cancellationDetails.ticket_price} تومان</p>
                            <p><strong>نرخ جریمه:</strong> {cancellationDetails.penalty_percentage}%</p>
                            <p><strong>مبلغ جریمه:</strong> {cancellationDetails.penalty_amount} تومان</p>
                            <p><strong>مبلغ قابل برگشت:</strong> {cancellationDetails.refund_amount} تومان</p>
                            <p><strong>زمان باقی‌مانده تا حرکت:</strong> {cancellationDetails.time_to_departure_hours} ساعت</p>

                            <form onSubmit={submitCancelRequest} className="report-form">
                                <TextField
                                    label="دلیل لغو"
                                    name="reason"
                                    multiline
                                    rows={4}
                                    fullWidth
                                    margin="normal"
                                    value={cancelReason}
                                    onChange={(e) => setCancelReason(e.target.value)}
                                    required
                                />
                                <div className="item-actions">
                                    <Button type="submit" variant="contained" color="primary">تایید و ارسال درخواست</Button>
                                    <Button onClick={() => setIsCancelDetailsPopupOpen(false)} variant="outlined" color="primary">انصراف</Button>
                                </div>
                            </form>
                        </div>
                    </Box>
                </Modal>
            )}
        </Container>
    );
};

export default ReservationHistory;
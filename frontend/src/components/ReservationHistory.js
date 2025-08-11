import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Typography } from '@mui/material';
import './Home.css';

const ReservationHistory = () => {
    const accessToken = localStorage.getItem('accessToken');
    const userInfo = JSON.parse(localStorage.getItem('userInfo'));

    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

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
    const handleRequest = (reservationId) => {
        alert(`ثبت درخواست برای رزرو: ${reservationId}`);
    };

    const handleReport = (reservationId) => {
        alert(`ثبت گزارش برای رزرو: ${reservationId}`);
    };

    const handleViewResponse = (reservationId) => {
        alert(`دیدن جواب برای رزرو: ${reservationId}`);
    };

    if (loading) return <Typography>در حال بارگذاری...</Typography>;
    if (error) return <Typography color="error">{error}</Typography>;

    return (
        <Container>
            <Typography variant="h4" gutterBottom>تاریخچه رزروهای من</Typography>
            {history.length === 0 ? (
                <Typography>شما تاکنون هیچ بلیتی رزرو نکرده‌اید.</Typography>
            ) : (
                history.map((booking) => {
                    const isBuy = booking.operation_type === 'BUY';
                    const isOwner = userInfo && userInfo.username === booking.current_owner;
                    const boxClass = getBoxClass(booking.operation_type, booking.operation_status);
                    console.log(`Current User: ${userInfo.username} | Booking Owner: ${booking.username}`);


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
                                <p>تاریخ انجام عملیات: <strong>{new Date(booking.operation_time).toLocaleString('fa-IR')}</strong></p>
                            </div>

                            <div className="item-actions">
                                {isBuy && isOwner && (
                                    <>
                                        <button className="action-btn" onClick={() => handleViewResponse(booking.reservation_id)}>دیدن جواب</button>
                                        <button className="action-btn" onClick={() => handleReport(booking.reservation_id)}>ثبت گزارش</button>
                                        <button className="action-btn" onClick={() => handleRequest(booking.reservation_id)}>ثبت درخواست لغو</button>
                                    </>
                                )}

                                {(!isBuy || (isBuy && !isOwner)) && (
                                    <button className="action-btn" onClick={() => handleViewResponse(booking.reservation_id)}>دیدن جواب</button>
                                )}
                            </div>
                        </div>
                    );
                })
            )}
        </Container>
    );
};

export default ReservationHistory;
// src/components/ShoppingCart.js

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Typography, Button, Modal, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import './ShoppingCart.css'; // فایل استایل جدید را وارد می کنیم

const ShoppingCart = () => {
    const accessToken = localStorage.getItem('accessToken');
    const navigate = useNavigate();

    const [temporaryReservations, setTemporaryReservations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // state های مربوط به تایمر، پاپ‌آپ و نتیجه پرداخت
    const [timers, setTimers] = useState({});
    const [isConfirmPopupOpen, setIsConfirmPopupOpen] = useState(false);
    const [selectedReservation, setSelectedReservation] = useState(null);
    const [selectedPaymentMethod, setSelectedPaymentMethod] = useState('');
    const [paymentResult, setPaymentResult] = useState(null);

    const fetchTemporaryReservations = async () => {
        if (!accessToken) {
            setError("برای مشاهده سبد خرید، ابتدا وارد حساب کاربری خود شوید.");
            setLoading(false);
            return;
        }

        try {
            const response = await axios.get('http://localhost:8000/api-test/temporary-reservations/', { headers: { Authorization: `Bearer ${accessToken}` } });
            setTemporaryReservations(response.data.data);
            setLoading(false);
        } catch (err) {
            console.error("Error fetching temporary reservations:", err.response?.data || err);
            setError(err.response?.data?.message || "خطا در دریافت سبد خرید.");
            setLoading(false);
        }
    };

    // منطق تایمر برای هر رزرو
    useEffect(() => {
        if (temporaryReservations.length > 0) {
            const calculateRemainingTime = (reservationTime) => {
                const expiryDuration = 9 * 60 + 50;
                const now = new Date();
                const reservationDate = new Date(reservationTime + 'Z');
                const elapsedTime = Math.floor((now.getTime() - reservationDate.getTime()) / 1000);
                return expiryDuration - elapsedTime;
            };

            const initialTimers = temporaryReservations.reduce((acc, res) => {
                acc[res.reservation_id] = calculateRemainingTime(res.date_and_time_of_reservation);
                return acc;
            }, {});
            setTimers(initialTimers);

            const interval = setInterval(() => {
                setTimers(currentTimers => {
                    const newTimers = { ...currentTimers };
                    let shouldStop = true;
                    let hasExpired = false;
                    Object.keys(newTimers).forEach(id => {
                        if (newTimers[id] > 0) {
                            newTimers[id] -= 1;
                            shouldStop = false;
                        } else if (newTimers[id] <= 0) {
                            hasExpired = true;
                        }
                    });

                    if (shouldStop) {
                        clearInterval(interval);
                        if (hasExpired) {
                            fetchTemporaryReservations();
                        }
                    }
                    return newTimers;
                });
            }, 1000);
            return () => clearInterval(interval);
        }
    }, [temporaryReservations, fetchTemporaryReservations]);

    // تابع برای فرمت قیمت
    const formatPrice = (price) => {
        return new Intl.NumberFormat('fa-IR').format(price);
    };

    // تابع برای باز کردن پاپ‌آپ تایید
    const handlePaymentMethodSelect = (res, method) => {
        setSelectedReservation(res);
        setSelectedPaymentMethod(method);
        setIsConfirmPopupOpen(true);
    };

    // تابع اصلی پرداخت
    const confirmPayment = async () => {
        setIsConfirmPopupOpen(false);

        let paymentData = {
            reservation_id: selectedReservation.reservation_id,
            payment_method: selectedPaymentMethod,
        };

        if (selectedPaymentMethod !== 'WALLET') {
            paymentData.payment_status = 'SUCCESSFUL';
        }

        try {
            const response = await axios.post(
                'http://localhost:8000/api-test/pay-tickets/',
                paymentData,
                { headers: { Authorization: `Bearer ${accessToken}` } }
            );

            setPaymentResult({ status: 'success', message: response.data.message });
            fetchTemporaryReservations();
        } catch (err) {
            setPaymentResult({ status: 'error', message: err.response?.data?.message || 'خطا در پرداخت.' });
            console.error(err.response?.data || err);
            fetchTemporaryReservations();
        }
    };

    // تابع برای لغو پرداخت
    const cancelPayment = () => {
        setIsConfirmPopupOpen(false);
    };

    useEffect(() => {
        fetchTemporaryReservations();
    }, [accessToken]);

    if (loading) return <Typography>در حال بارگذاری...</Typography>;
    if (error) return <Typography color="error">{error}</Typography>;

    const paymentMethods = [
        { key: 'WALLET', label: 'کیف پول' },
        { key: 'CREDIT_CARD', label: 'کارت اعتباری' },
        { key: 'CRYPTOCURRENCY', label: 'ارز دیجیتال' },
    ];

    return (
        <Container className="cart-container">
        <Button
            onClick={() => navigate(-1)}
            sx={{
                position: 'absolute',
                top: 20,
                left: 20,
                backgroundColor: 'transparent', // پس‌زمینه شفاف
                color: '#007bff', // متن آبی
                border: '1px solid #007bff', // کادر آبی
                ':hover': {
                    backgroundColor: '#007bff', // در حالت هاور، پس‌زمینه آبی
                    color: '#fff', // متن در حالت هاور سفید
                }
            }}
        >
            بازگشت به صفحه اصلی
        </Button>
            <Typography variant="h4" gutterBottom>سبد خرید</Typography>

            {paymentResult && (
                <div className={`payment-result-message ${paymentResult.status}`}>
                    {paymentResult.message}
                </div>
            )}

            {temporaryReservations.length === 0 ? (
                <Typography>سبد خرید شما خالی است.</Typography>
            ) : (
                temporaryReservations.map((res) => (
                    <div key={res.reservation_id} className="cart-item">
                        <div className="cart-item-details">
                            <Typography><strong>شماره رزرو:</strong> {res.reservation_id}</Typography>
                            <Typography><strong>بلیت:</strong> {res.origin_city} به {res.destination_city}</Typography>
                            <Typography><strong>تاریخ حرکت:</strong> {new Date(res.departure_start).toLocaleDateString('fa-IR')}</Typography>
                            <Typography><strong>قیمت:</strong> {formatPrice(res.price)} تومان</Typography>
                            <Typography><strong>صندلی:</strong> {res.reservation_seat}</Typography>
                            <Typography>
                                <strong>زمان باقی‌مانده:</strong>
                                {' '}
                                {Math.floor(timers[res.reservation_id] / 60)}:
                                {timers[res.reservation_id] % 60 < 10 ? '0' : ''}{timers[res.reservation_id] % 60}
                            </Typography>
                        </div>
                        <div className="cart-actions">
                            {paymentMethods.map(method => (
                                <Button
                                    key={method.key}
                                    variant="contained"
                                    onClick={() => handlePaymentMethodSelect(res, method.key)}
                                    sx={{
                                        backgroundColor: '#007bff',
                                        color: '#fff',
                                        ':hover': { backgroundColor: '#0056b3' }
                                    }}
                                >
                                    پرداخت با {method.label}
                                </Button>
                            ))}
                        </div>
                    </div>
                ))
            )}

            {/* پاپ‌آپ تایید پرداخت */}
            <Modal open={isConfirmPopupOpen} onClose={cancelPayment}>
                <Box className="confirm-popup-box">
                    <Typography variant="h6" component="h2">تایید پرداخت</Typography>
                    <Typography sx={{ mt: 2 }}>
                        آیا مطمئنید می‌خواهید این بلیت را با روش {paymentMethods.find(m => m.key === selectedPaymentMethod)?.label} پرداخت کنید؟
                    </Typography>
                    <div className="item-actions" style={{ marginTop: '1.5rem' }}>
                        <Button onClick={confirmPayment} variant="contained" color="primary">تایید</Button>
                        <Button onClick={cancelPayment} variant="outlined" color="primary">انصراف</Button>
                    </div>
                </Box>
            </Modal>
        </Container>
    );
};

export default ShoppingCart;
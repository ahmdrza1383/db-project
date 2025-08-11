import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Typography, MenuItem, Select, FormControl, InputLabel, TextField, Button } from '@mui/material';
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
    const [popupReportText, setPopupReportText] = useState('');
    const [popupAdminResponse, setPopupAdminResponse] = useState('');

    // state ها برای پاپ‌آپ ثبت گزارش
    const [isReportPopupOpen, setIsReportPopupOpen] = useState(false);
    const [reportReservationId, setReportReservationId] = useState(null);
    const [reportType, setReportType] = useState('PAYMENT'); // مقدار پیش‌فرض
    const [reportText, setReportText] = useState('');

    // ... سایر state های شما
    const [isCancelDetailsPopupOpen, setIsCancelDetailsPopupOpen] = useState(false);
    const [cancelDetails, setCancelDetails] = useState(null);

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
    const handleReport = async (reservationId) => {
        try {
            const response = await axios.get(
                `http://localhost:8000/api-test/report/status/${reservationId}/`,
                { headers: { Authorization: `Bearer ${accessToken}` } }
            );

            const data = response.data;
            if (data.status === 'success') {
                // اگر قبلا گزارشی ثبت شده، اجازه ثبت دوباره نمی‌دهد
                alert('شما قبلاً برای این رزرو گزارشی ثبت کرده‌اید.');
                return;
            }

            // اگر گزارشی ثبت نشده، پاپ‌آپ ثبت گزارش را باز می‌کند
            setReportReservationId(reservationId);
            setIsReportPopupOpen(true);

        } catch (err) {
            alert(err.response?.data?.message || 'خطا در بررسی وضعیت گزارش.');
        }
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
                setPopupReportText('هنوز گزارشی برای این رزرو ثبت نشده است.');
                setPopupAdminResponse('');
            } else if (data.status === 'success') {
                const report = data.report;
                setPopupTitle('جزئیات گزارش');
                setPopupReportText(report.report_text || 'متن گزارش شما در دسترس نیست.');

                if (report.report_status === 'UNCHECKED') {
                    setPopupAdminResponse('گزارش شما ثبت شده اما هنوز پاسخی دریافت نکرده است.');
                } else {
                    setPopupAdminResponse(report.admin_response || 'پاسخی از طرف مدیر ثبت نشده است.');
                }
            }
            setIsPopupOpen(true);

        } catch (err) {
            alert(err.response?.data?.message || 'خطا در دریافت پاسخ گزارش.');
        }
    };

   const handleRequest = async (reservationId) => {
      try {
          // از API موجود برای گرفتن جزئیات لغو استفاده می کنیم
          const response = await axios.get(
              `http://localhost:8000/api-test/reservations/${reservationId}/cancel/`,
              { headers: { Authorization: `Bearer ${accessToken}` } }
          );

          if (response.data.status === 'success') {
              setCancelDetails({ ...response.data.cancellation_info, reservation_id: reservationId });
              setIsCancelDetailsPopupOpen(true);
          } else {
              alert(response.data.message);
          }
      } catch (err) {
          alert(err.response?.data?.message || "خطا در دریافت جزئیات لغو.");
      }
   };

  const confirmCancelRequest = async (cancelReason) => {
      try {
          const response = await axios.post(
              `http://localhost:8000/api-test/reservations/${cancelDetails.reservation_id}/requests/`,
              { request_subject: 'CANCEL', request_text: cancelReason },
              { headers: { Authorization: `Bearer ${accessToken}` } }
          );
          alert(response.data.message);
          setIsCancelDetailsPopupOpen(false);
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
                                <p>تاریخ انجام عملیات: <strong>{new Date(booking.operation_time).toLocaleString('fa-IR')}</strong></p>
                            </div>

                            <div className="item-actions">
                                {isBuy && isOwner && (
                                    <>
                                        <Button className="action-btn" onClick={() => handleViewResponse(booking.reservation_id)}>دیدن جواب</Button>
                                        <Button className="action-btn" onClick={() => handleReport(booking.reservation_id)}>ثبت گزارش</Button>
                                        <Button className="action-btn" onClick={() => handleRequest(booking.reservation_id)}>ثبت درخواست لغو</Button>
                                    </>
                                )}
                                {(!isBuy || (isBuy && !isOwner)) && (
                                    <Button className="action-btn" onClick={() => handleViewResponse(booking.reservation_id)}>دیدن جواب</Button>
                                )}
                            </div>
                        </div>
                    );
                })
            )}

            {/* پاپ‌آپ‌های مشترک در انتهای کامپوننت */}
            {/* پاپ‌آپ دیدن جواب */}
            {isPopupOpen && (
                <div className="popup-overlay">
                    <div className="popup-content">
                        <div className="popup-header">
                            <h2>{popupTitle}</h2>
                            <button className="popup-close-btn" onClick={() => setIsPopupOpen(false)}>
                                &times;
                            </button>
                        </div>
                        <div className="popup-body">
                            <div className="user-report-text">
                                <strong>متن گزارش شما:</strong>
                                <p>{popupReportText}</p>
                            </div>
                            {popupAdminResponse && (
                                <div className="admin-response-text">
                                    <strong>پاسخ مدیر:</strong>
                                    <p>{popupAdminResponse}</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* پاپ‌آپ ثبت گزارش */}
            {isReportPopupOpen && (
                <div className="popup-overlay">
                    <div className="popup-content">
                        <div className="popup-header">
                            <h2>ثبت گزارش جدید</h2>
                            <button className="popup-close-btn" onClick={() => setIsReportPopupOpen(false)}>
                                &times;
                            </button>
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
                    </div>
                </div>
            )}
            {/* پاپ‌آپ نمایش جزئیات لغو */}
            {isCancelDetailsPopupOpen && cancelDetails && (
                <div className="popup-overlay">
                    <div className="popup-content">
                        <div className="popup-header">
                            <h2>جزئیات لغو رزرو</h2>
                            <button className="popup-close-btn" onClick={() => setIsCancelDetailsPopupOpen(false)}>
                                &times;
                            </button>
                        </div>
                        <div className="popup-body">
                            <p><strong>قیمت بلیت:</strong> {cancelDetails.ticket_price} تومان</p>
                            <p><strong>نرخ جریمه:</strong> {cancelDetails.penalty_percentage}%</p>
                            <p><strong>مبلغ جریمه:</strong> {cancelDetails.penalty_amount} تومان</p>
                            <p><strong>مبلغ قابل برگشت:</strong> {cancelDetails.refund_amount} تومان</p>
                            <p><strong>زمان باقی‌مانده تا حرکت:</strong> {cancelDetails.time_to_departure_hours} ساعت</p>

                            <form onSubmit={(e) => { e.preventDefault(); confirmCancelRequest(e.target.reason.value); }}>
                                <TextField
                                    label="دلیل لغو"
                                    name="reason"
                                    multiline
                                    rows={3}
                                    fullWidth
                                    margin="normal"
                                    required
                                />
                                <div className="item-actions">
                                    <Button type="submit" variant="contained" color="primary">تایید و ارسال درخواست</Button>
                                    <Button onClick={() => setIsCancelDetailsPopupOpen(false)} variant="outlined" color="secondary">انصراف</Button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            )}
        </Container>
    );
};

export default ReservationHistory;
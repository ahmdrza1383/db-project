import React, {useState, useEffect} from 'react';
import {
    Button, Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Typography,
    Grid,
    Divider,
    Box,
    Chip,
} from '@mui/material';
import {Link, useNavigate} from "react-router-dom";
import axios from 'axios';
import './Home.css';


const Home = () => {
    const navigate = useNavigate();

    // فرم جستجو states
    const [origin, setOrigin] = useState('');
    const [destination, setDestination] = useState('');
    const [travelDate, setTravelDate] = useState('');
    const [vehicleType, setVehicleType] = useState('FLIGHT');
    const [minPrice, setMinPrice] = useState('');
    const [maxPrice, setMaxPrice] = useState('');
    const [companyName, setCompanyName] = useState('');
    const [flightClass, setFlightClass] = useState('');
    const [trainStars, setTrainStars] = useState('');
    const [busType, setBusType] = useState('');

    // نتایج جستجو
    const [searchResults, setSearchResults] = useState([]);
    const [searchLoading, setSearchLoading] = useState(false);
    const [searchError, setSearchError] = useState(null);
    const [ticketReservations, setTicketReservations] = useState([]);
    const [error, setError] = useState(null);

    // بلیط‌های فروخته نشده
    const [availableTickets, setAvailableTickets] = useState([]);

    // جزئیات بلیط انتخاب شده از لیست فروخته نشده
    const [selectedTicket, setSelectedTicket] = useState(null);
    const [detailsLoading, setDetailsLoading] = useState(false);
    const [detailsError, setDetailsError] = useState(null);

    // صندلی‌های بلیط انتخاب شده
    const [seats, setSeats] = useState([]);

    // صندلی انتخاب شده برای رزرو موقت
    const [selectedSeat, setSelectedSeat] = useState(null);
    const [tempReservations, setTempReservations] = useState([]);


    // وضعیت رزرو و پرداخت
    const [reservationLoading, setReservationLoading] = useState(false);
    const [reservationError, setReservationError] = useState(null);
    const [tempReservationId, setTempReservationId] = useState('');
    const [paymentMethod, setPaymentMethod] = useState('');
    const [paymentLoading, setPaymentLoading] = useState(false);
    const [paymentMessage, setPaymentMessage] = useState(null);
    const [paymentError, setPaymentError] = useState(null);


    // وضعیت ورود کاربر
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [accessToken, setAccessToken] = useState(null);
    const [userInfo, setUserInfo] = useState(null);


    // بارگذاری وضعیت کاربر از localStorage هنگام بارگذاری اولیه کامپوننت
    useEffect(() => {
        const token = localStorage.getItem('accessToken');
        const user = JSON.parse(localStorage.getItem('userInfo'));

        if (token && user) {
            if (user.user_role === 'ADMIN') {
                navigate('/admin/dashboard');
                return;
            }

            setIsLoggedIn(true);
            setAccessToken(token);
            setUserInfo(user);
        } else {
            setIsLoggedIn(false);
            setAccessToken(null);
            setUserInfo(null);
        }
    }, []);

    // ⭐️⭐️⭐️ تغییرات اینجا اعمال شده است ⭐️⭐️⭐️
    // بارگذاری رزروهای موقت کاربر پس از تغییر وضعیت userInfo
    useEffect(() => {
        if (userInfo) {
            const storedReservations = JSON.parse(localStorage.getItem('tempReservations') || '[]');
            const userTempReservations = storedReservations.filter(res => res.username === userInfo.username);
            setTempReservations(userTempReservations);
        } else {
            // این بخش حذف شده تا پس از خروج، رزروها پاک نشوند.
            // setTempReservations([]);
        }
    }, [userInfo]);

    // بررسی رزروهای موقت منقضی شده هر دقیقه
    useEffect(() => {
        const checkExpiry = () => {
            const storedReservations = JSON.parse(localStorage.getItem('tempReservations') || '[]');
            const now = Date.now();
            const nonExpiredReservations = storedReservations.filter(res => {
                const expiryTime = new Date(res.reserved_at).getTime() + (res.expires_in_minutes * 60 * 1000);
                return expiryTime > now;
            });

            if (nonExpiredReservations.length !== storedReservations.length) {
                localStorage.setItem('tempReservations', JSON.stringify(nonExpiredReservations));
                if (userInfo) {
                    setTempReservations(nonExpiredReservations.filter(res => res.username === userInfo.username));
                }
            }
        };
        checkExpiry();
        const interval = setInterval(checkExpiry, 60000); // Check every minute
        return () => clearInterval(interval);
    }, [userInfo]);


    // تابع برای دریافت لیست بلیط‌های موجود
    const fetchAvailableTickets = async () => {
        try {
            const res = await fetch('http://localhost:8000/api-test/available-tickets/');
            const data = await res.json();
            if (res.ok && data.status === 'success') {
                setAvailableTickets(data.data);
            } else {
                console.error('Error fetching tickets:', data.message);
            }
        } catch (error) {
            console.error('Network error:', error);
        }
    };

    // بارگذاری اولیه بلیط‌ها
    useEffect(() => {
        fetchAvailableTickets();
    }, []);

    // جستجو
    const handleSearch = async (e) => {
        e.preventDefault();

        if (!origin || !destination || !travelDate) {
            setSearchError('لطفا مبدا، مقصد و تاریخ سفر را وارد کنید.');
            return;
        }

        setSearchLoading(true);
        setSearchError(null);
        setSearchResults([]);

        const requestBody = {
            origin_city: origin,
            destination_city: destination,
            departure_date: travelDate,
            vehicle_type: vehicleType,
        };
        if (minPrice) requestBody.min_price = Number(minPrice);
        if (maxPrice) requestBody.max_price = Number(maxPrice);
        if (companyName.trim()) requestBody.company_name = companyName.trim();
        if (flightClass) requestBody.flight_class = flightClass;
        if (trainStars) requestBody.train_stars = Number(trainStars);
        if (busType) requestBody.bus_type = busType;

        try {
            const response = await fetch('http://localhost:8000/api-test/search-tickets/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(requestBody),
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                setSearchResults(data.data);
            } else {
                setSearchError(data.message || 'خطا در جستجو');
            }
        } catch (err) {
            setSearchError('ارتباط با سرور برقرار نشد.');
        } finally {
            setSearchLoading(false);
        }
    };

    const fetchTicketDetails = async (ticketId) => {
        try {
            const response = await axios.get(`http://localhost:8000/api-test/ticket-details/${ticketId}/`);
            const details = response.data.data;
            setSelectedTicket(details);
            setTicketReservations(details.reservations);
            setError(null);
        } catch (err) {
            console.error("Error fetching ticket details:", err);
            setError("خطا در دریافت جزئیات بلیط.");
        }
    };

    const colorByStatus = (normalized) => {
        switch (normalized) {
            case "AVAILABLE":
                return "success";
            case "TEMPORARY":
                return "warning";
            case "OCCUPIED":
                return "error";
            default:
                return "primary";
        }
    };
    const normalizeSeatStatus = (status) => {
        if (!status) return "AVAILABLE";
        const s = String(status).toUpperCase();

        if (s === "NOT_RESERVED" || s === "AVAILABLE") return "AVAILABLE";
        if (s.includes("TEMP")) return "TEMPORARY";
        if (["PAYED", "PAID", "RESERVED", "OCCUPIED"].includes(s)) return "OCCUPIED";

        return "AVAILABLE";
    };

    const handleReserveSeat = async (seatNumber) => {
        // فرض می کنیم accessToken اینجا در دسترس است
        const token = accessToken;

        try {
            const response = await axios.post(
                `http://localhost:8000/api-test/reserve-ticket/`,
                {ticket_id: selectedTicket.ticket_id, seat_number: seatNumber},
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );
            console.log("Reservation successful:", response.data);
            alert("صندلی با موفقیت رزرو شد!");
            fetchTicketDetails(selectedTicket.ticket_id);
        } catch (err) {
            console.error("Error reserving seat:", err.response?.data || err);
            alert(err.response?.data?.message || "خطا در رزرو صندلی.");
            setError(err.response?.data?.message || "خطا در رزرو صندلی.");
        }
    };
    // رزرو موقت صندلی
    const handleSeatSelection = async (seat_number) => {
        if (!isLoggedIn) {
            alert('برای رزرو بلیط ابتدا باید وارد شوید.');
            return;
        }
        setReservationLoading(true);
        setReservationError(null);
        setPaymentMessage(null);
        setTempReservationId('');

        const requestBody = {
            ticket_id: selectedTicket.ticket_id,
            seat_number: seat_number,
        };

        try {
            const response = await fetch('http://localhost:8000/api-test/reserve-ticket/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`,
                },
                body: JSON.stringify(requestBody),
            });
            const data = await response.json();
            if (response.ok && data.status === 'success') {
                // Update the seats state to reflect the new reservation status
                setSeats(prevSeats =>
                    prevSeats.map(seat =>
                        seat.reservation_seat === seat_number
                            ? {
                                ...seat,
                                reservation_status: 'TEMPORARY',
                                reservation_id: data.reservation.reservation_id,
                                username: userInfo.username
                            }
                            : seat
                    )
                );
                // Update the selectedTicket to show the new temporary reservation
                setSelectedTicket(prevTicket => {
                    if (!prevTicket) return null;
                    const updatedReservations = prevTicket.reservations.map(res =>
                        res.reservation_seat === seat_number
                            ? {
                                ...res,
                                reservation_status: 'TEMPORARY',
                                reservation_id: data.reservation.reservation_id,
                                username: userInfo.username
                            }
                            : res
                    );
                    return {...prevTicket, reservations: updatedReservations};
                });

                // Add the new temporary reservation to localStorage
                const storedReservations = JSON.parse(localStorage.getItem('tempReservations') || '[]');
                const updatedStoredReservations = [...storedReservations, data.reservation];
                localStorage.setItem('tempReservations', JSON.stringify(updatedStoredReservations));

                // Add the new temporary reservation to the list for payment in local state
                setTempReservations(prevTempReservations => [...prevTempReservations, data.reservation]);
                setPaymentMessage(`صندلی شماره ${seat_number} به صورت موقت رزرو شد. لطفا برای پرداخت از لیست رزروهای موقت آن را انتخاب کنید.`);
                setSelectedSeat(null); // Reset selected seat for new reservation
            } else {
                setReservationError(data.message || 'خطا در رزرو موقت صندلی');
            }
        } catch (err) {
            setReservationError('ارتباط با سرور برقرار نشد.');
        } finally {
            setReservationLoading(false);
        }
    };

    // پرداخت بلیط
    const handlePayment = async (e) => {
        e.preventDefault();
        if (!paymentMethod) {
            setPaymentError('لطفا روش پرداخت را انتخاب کنید.');
            return;
        }
        if (!tempReservationId) {
            setPaymentError('لطفا یک رزرو موقت برای پرداخت انتخاب کنید.');
            return;
        }

        setPaymentLoading(true);
        setPaymentError(null);
        setPaymentMessage(null);

        const requestBody = {
            reservation_id: parseInt(tempReservationId),
            payment_method: paymentMethod,
            payment_status: paymentMethod === 'WALLET' ? undefined : 'SUCCESSFUL',
        };

        try {
            const response = await fetch('http://localhost:8000/api-test/pay-ticket/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`,
                },
                body: JSON.stringify(requestBody),
            });
            const data = await response.json();
            if (response.ok && data.status === 'success') {
                setPaymentMessage('پرداخت با موفقیت انجام شد. بلیط شما رزرو نهایی شد!');
                setSelectedTicket(null);
                fetchAvailableTickets();

                // Remove the paid reservation from localStorage
                const storedReservations = JSON.parse(localStorage.getItem('tempReservations') || '[]');
                const updatedStoredReservations = storedReservations.filter(res => res.reservation_id !== parseInt(tempReservationId));
                localStorage.setItem('tempReservations', JSON.stringify(updatedStoredReservations));

                setTempReservations(updatedStoredReservations.filter(res => res.username === userInfo.username));
                setTempReservationId('');
            } else {
                setPaymentError(data.message || 'خطا در پرداخت');
                setPaymentMessage(null);
            }
        } catch (err) {
            setPaymentError('ارتباط با سرور برقرار نشد.');
        } finally {
            setPaymentLoading(false);
        }
    };

    // در داخل کامپوننت Home، پس از تعریف سایر متدها
    const handleConfirmReservation = async () => {
        if (!isLoggedIn) {
            alert('برای تأیید رزرو ابتدا باید وارد شوید.');
            return;
        }

        if (!selectedSeat) {
            alert('لطفاً یک صندلی انتخاب کنید.');
            return;
        }

        setReservationLoading(true);
        setReservationError(null);
        setPaymentMessage(null);

        try {
            // فرض می‌کنیم اینجا باید رزرو موقت را به رزرو نهایی تبدیل کنیم
            const requestBody = {
                ticket_id: selectedTicket.ticket_id,
                seat_number: selectedSeat,
                reservation_id: tempReservationId, // اگر رزرو موقت قبلاً ایجاد شده باشد
            };

            const response = await fetch('http://localhost:8000/api-test/confirm-reservation/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`,
                },
                body: JSON.stringify(requestBody),
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                setPaymentMessage('رزرو با موفقیت تأیید شد. لطفاً برای پرداخت اقدام کنید.');
                // به‌روزرسانی وضعیت صندلی‌ها
                setTicketReservations(prevReservations =>
                    prevReservations.map(res =>
                        res.reservation_seat === selectedSeat
                            ? {...res, reservation_status: 'OCCUPIED'}
                            : res
                    )
                );
                setSelectedSeat(null); // ریست کردن صندلی انتخاب‌شده
                // انتقال به بخش پرداخت (اختیاری)
                setTempReservationId(data.reservation_id); // ذخیره ID رزرو برای پرداخت
            } else {
                setReservationError(data.message || 'خطا در تأیید رزرو');
            }
        } catch (err) {
            setReservationError('ارتباط با سرور برقرار نشد.');
        } finally {
            setReservationLoading(false);
        }
    };

    return (
        <div className="home-container">

            <header className="main-header">
                <div className="logo">
                    <img src="/logo512.png" alt="Logo"/>
                    {isLoggedIn && userInfo && (
                        <span className="user-info">
                {userInfo.username}
            </span>
                    )}
                </div>

                <div className="header-actions">
                    {!isLoggedIn ? (
                        <>
                            <a href="/login" className="btn-auth">ورود</a>
                            <a href="/signup" className="btn-auth">ثبت‌نام</a>
                        </>
                    ) : (
                        <>
                            <a href="/cart" className="btn-auth">سبد خرید</a>
                            <a href="/history" className="btn-auth">تاریخچه رزروها</a>
                            <a href="/profile" className="btn-auth">پروفایل</a>
                            <button
                                className="btn-auth"
                                onClick={() => {
                                    localStorage.removeItem('accessToken');
                                    localStorage.removeItem('refreshToken');
                                    localStorage.removeItem('userInfo');
                                    setTempReservations([]);
                                    setIsLoggedIn(false);
                                    window.location.reload();
                                }}
                            >
                                خروج
                            </button>
                        </>
                    )}
                </div>
            </header>

            {/* فرم جستجو */}
            <main className="main-search-section">
                <div className="search-box-wrapper">
                    <div className="search-tabs">
                        <button
                            className={`tab-btn ${vehicleType === 'FLIGHT' ? 'active' : ''}`}
                            onClick={() => setVehicleType('FLIGHT')}
                            type="button"
                        >
                            پرواز
                        </button>
                        <button
                            className={`tab-btn ${vehicleType === 'TRAIN' ? 'active' : ''}`}
                            onClick={() => setVehicleType('TRAIN')}
                            type="button"
                        >
                            قطار
                        </button>
                        <button
                            className={`tab-btn ${vehicleType === 'BUS' ? 'active' : ''}`}
                            onClick={() => setVehicleType('BUS')}
                            type="button"
                        >
                            اتوبوس
                        </button>
                    </div>

                    <form className="search-form" onSubmit={handleSearch}>
                        <div className="input-group">
                            <label htmlFor="origin">مبدا</label>
                            <input
                                id="origin"
                                type="text"
                                placeholder="شهری که از آن سفر می‌کنید"
                                value={origin}
                                onChange={e => setOrigin(e.target.value)}
                                required
                            />
                        </div>

                        <div className="input-group">
                            <label htmlFor="destination">مقصد</label>
                            <input
                                id="destination"
                                type="text"
                                placeholder="شهری که به آن سفر می‌کنید"
                                value={destination}
                                onChange={e => setDestination(e.target.value)}
                                required
                            />
                        </div>

                        <div className="input-group">
                            <label htmlFor="travelDate">تاریخ سفر</label>
                            <input
                                id="travelDate"
                                type="date"
                                value={travelDate}
                                onChange={e => setTravelDate(e.target.value)}
                                required
                            />
                        </div>

                        {/* فیلدهای اختیاری */}
                        <div className="input-group">
                            <label>حداقل قیمت (تومان)</label>
                            <input
                                type="number"
                                min="0"
                                value={minPrice}
                                onChange={e => setMinPrice(e.target.value)}
                                placeholder="اختیاری"
                            />
                        </div>

                        <div className="input-group">
                            <label>حداکثر قیمت (تومان)</label>
                            <input
                                type="number"
                                min="0"
                                value={maxPrice}
                                onChange={e => setMaxPrice(e.target.value)}
                                placeholder="اختیاری"
                            />
                        </div>

                        <div className="input-group">
                            <label>نام شرکت</label>
                            <input
                                type="text"
                                value={companyName}
                                onChange={e => setCompanyName(e.target.value)}
                                placeholder="اختیاری"
                            />
                        </div>

                        {/* فیلدهای مربوط به نوع وسیله نقلیه */}
                        {vehicleType === 'FLIGHT' && (
                            <div className="input-group">
                                <label>کلاس پرواز</label>
                                <select
                                    value={flightClass}
                                    onChange={e => setFlightClass(e.target.value)}
                                >
                                    <option value="">انتخاب کنید</option>
                                    <option value="Economy">اکونومی</option>
                                    <option value="Business">بیزینس</option>
                                    <option value="First">فرست کلاس</option>
                                </select>
                            </div>
                        )}

                        {vehicleType === 'TRAIN' && (
                            <div className="input-group">
                                <label>ستاره قطار</label>
                                <select
                                    value={trainStars}
                                    onChange={e => setTrainStars(e.target.value)}
                                >
                                    <option value="">انتخاب کنید</option>
                                    <option value="1">1 ستاره</option>
                                    <option value="2">2 ستاره</option>
                                    <option value="3">3 ستاره</option>
                                    <option value="4">4 ستاره</option>
                                    <option value="5">5 ستاره</option>
                                </select>
                            </div>
                        )}

                        {vehicleType === 'BUS' && (
                            <div className="input-group">
                                <label>نوع اتوبوس</label>
                                <select
                                    value={busType}
                                    onChange={e => setBusType(e.target.value)}
                                >
                                    <option value="">انتخاب کنید</option>
                                    <option value="VIP">ویژه</option>
                                    <option value="Normal">معمولی</option>
                                </select>
                            </div>
                        )}

                        <button type="submit" className="search-btn" disabled={searchLoading}>
                            {searchLoading ? 'در حال جستجو...' : 'جستجو'}
                        </button>
                    </form>

                    {/* نتایج جستجو */}
                    <section className="search-results-section">
                        {searchLoading && <p className="loading-message">در حال جستجوی بلیط‌ها...</p>}
                        {searchError && <p className="error-message">خطا: {searchError}</p>}
                        {searchResults.length > 0 && (
                            <div>
                                <h2>نتایج جستجو</h2>
                                <div className="results-list">
                                    {searchResults.map(ticket => (
                                        <div key={ticket.ticket_id} className="ticket-card"
                                             onClick={() => fetchTicketDetails(ticket.ticket_id)}>
                                            <h3>{ticket.origin_city} به {ticket.destination_city}</h3>
                                            <p>شرکت: {ticket.company_name || ticket.airline_name || '-'}</p>
                                            <p>تاریخ
                                                حرکت: {ticket.departure_start?.slice(0, 10) || ticket.departure_date || '-'}</p>
                                            <p>قیمت: {ticket.price} تومان</p>
                                            <p>نوع وسیله: {ticket.vehicle_type}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </section>
                </div>
            </main>

            {/* لیست بلیط‌های فروخته نشده (طراحی جدید) */}
            <section className="available-tickets-section">
                <h2>بلیط‌های فروخته نشده</h2>
                {availableTickets.length === 0 && <p className="no-tickets-message">بلیط فروخته نشده‌ای موجود نیست.</p>}
                <div className="available-tickets-grid">
                    {availableTickets.map(ticket => (
                        <div
                            key={ticket.ticket_id}
                            className="available-ticket-card"
                            onClick={() => fetchTicketDetails(ticket.ticket_id)}
                        >
                            <div className="ticket-header">
                                <span
                                    className="ticket-type">{ticket.vehicle_type === 'FLIGHT' ? '✈️ پرواز' : ticket.vehicle_type === 'TRAIN' ? '🚆 قطار' : '🚌 اتوبوس'}</span>
                                <span className="ticket-price">
                  <strong>{ticket.price.toLocaleString()}</strong> تومان
                </span>
                            </div>
                            <div className="ticket-body">
                                <div className="ticket-route">
                                    <div className="ticket-city">{ticket.destination_city}</div>
                                    <span className="route-icon">➡️</span>
                                    <div className="ticket-city">{ticket.origin_city}</div>
                                </div>
                                <div className="info-item">
                                    <span>تاریخ حرکت:</span>
                                    <strong>{ticket.departure_start?.slice(0, 10)}</strong>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {selectedTicket && (
                <Dialog
                    open={Boolean(selectedTicket)}
                    onClose={() => setSelectedTicket(null)}
                    maxWidth="md"
                    fullWidth
                    PaperProps={{sx: {borderRadius: 2, boxShadow: '0 4px 12px rgba(0,0,0,0.1)'}}}
                >
                    {/* هدر */}
                    <DialogTitle
                        sx={{fontWeight: "bold", backgroundColor: "#f0f4f8", textAlign: "center", color: "#333"}}>
                        🎫 جزئیات بلیط
                    </DialogTitle>

                    {/* محتوای اصلی */}
                    <DialogContent dividers sx={{padding: "24px"}}>
                        {/* اطلاعات کلی */}
                        <Grid container spacing={3} sx={{backgroundColor: "#fff", borderRadius: 1, p: 2}}>
                            <Grid item xs={12} sm={6}>
                                <Typography sx={{
                                    fontSize: "1rem",
                                    color: "#555"
                                }}><strong>مبدا:</strong> {selectedTicket.origin_city}</Typography>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Typography sx={{
                                    fontSize: "1rem",
                                    color: "#555"
                                }}><strong>مقصد:</strong> {selectedTicket.destination_city}</Typography>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Typography sx={{fontSize: "1rem", color: "#555"}}><strong>تاریخ
                                    حرکت:</strong> {selectedTicket.departure_start?.slice(0, 10)}</Typography>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Typography sx={{fontSize: "1rem", color: "#555"}}><strong>تاریخ
                                    رسیدن:</strong> {selectedTicket.departure_end?.slice(0, 10) || "-"}</Typography>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Typography sx={{
                                    fontSize: "1rem",
                                    color: "#555"
                                }}><strong>قیمت:</strong> {Number(selectedTicket.price || 0).toLocaleString()} تومان</Typography>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Typography sx={{fontSize: "1rem", color: "#555"}}><strong>ظرفیت
                                    باقی‌مانده:</strong> {selectedTicket.remaining_capacity}</Typography>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Typography sx={{fontSize: "1rem", color: "#555"}}><strong>نوع
                                    وسیله:</strong> {selectedTicket.vehicle_type}</Typography>
                            </Grid>
                        </Grid>

                        {/* جزئیات وسیله نقلیه */}
                        {selectedTicket.vehicle_type === "FLIGHT" && selectedTicket.vehicle_details && (
                            <>
                                <Divider sx={{my: 3}}/>
                                <Typography variant="h6" sx={{paddingLeft: "20px", color: "#1976d2"}}>✈️ اطلاعات
                                    پرواز</Typography>
                                <Grid container spacing={2}
                                      sx={{padding: "20px", backgroundColor: "#f9f9f9", borderRadius: 1}}>
                                    <Grid item xs={6}><Typography sx={{fontSize: "1rem", color: "#555"}}>خط
                                        هوایی: {selectedTicket.vehicle_details.airline_name}</Typography></Grid>
                                    <Grid item xs={6}><Typography sx={{fontSize: "1rem", color: "#555"}}>کلاس
                                        پرواز: {selectedTicket.vehicle_details.flight_class}</Typography></Grid>
                                    <Grid item xs={6}><Typography sx={{
                                        fontSize: "1rem",
                                        color: "#555"
                                    }}>توقف‌ها: {selectedTicket.vehicle_details.number_of_stop}</Typography></Grid>
                                    <Grid item xs={6}><Typography sx={{fontSize: "1rem", color: "#555"}}>کد
                                        پرواز: {selectedTicket.vehicle_details.flight_code}</Typography></Grid>
                                </Grid>
                            </>
                        )}

                        {selectedTicket.vehicle_type === "TRAIN" && selectedTicket.vehicle_details && (
                            <>
                                <Divider sx={{my: 3}}/>
                                <Typography variant="h6" sx={{paddingLeft: "20px", color: "#1976d2"}}>🚆 اطلاعات
                                    قطار</Typography>
                                <Grid container spacing={2}
                                      sx={{padding: "20px", backgroundColor: "#f9f9f9", borderRadius: 1}}>
                                    <Grid item xs={6}><Typography sx={{fontSize: "1rem", color: "#555"}}>ستاره
                                        قطار: {selectedTicket.vehicle_details.train_stars}</Typography></Grid>
                                    <Grid item xs={6}><Typography sx={{fontSize: "1rem", color: "#555"}}>کوپه
                                        بسته: {selectedTicket.vehicle_details.choosing_a_closed_coupe ? "بله" : "خیر"}</Typography></Grid>
                                </Grid>
                            </>
                        )}

                        {selectedTicket.vehicle_type === "BUS" && selectedTicket.vehicle_details && (
                            <>
                                <Divider sx={{my: 3}}/>
                                <Typography variant="h6" sx={{paddingLeft: "20px", color: "#1976d2"}}>🚌 اطلاعات
                                    اتوبوس</Typography>
                                <Grid container spacing={2}
                                      sx={{padding: "20px", backgroundColor: "#f9f9f9", borderRadius: 1}}>
                                    <Grid item xs={6}><Typography sx={{
                                        fontSize: "1rem",
                                        color: "#555"
                                    }}>شرکت: {selectedTicket.vehicle_details.company_name}</Typography></Grid>
                                    <Grid item xs={6}><Typography sx={{fontSize: "1rem", color: "#555"}}>نوع
                                        اتوبوس: {selectedTicket.vehicle_details.bus_type}</Typography></Grid>
                                </Grid>
                            </>
                        )}

                        <Divider sx={{my: 3}}/>

                        {/* انتخاب صندلی */}
                        <Typography variant="h6" gutterBottom sx={{paddingLeft: "20px", color: "#1976d2"}}>🪑 انتخاب
                            صندلی</Typography>

                        <Box sx={{display: "flex", gap: 2, mb: 2, paddingLeft: "20px", alignItems: "center"}}>
                            <Chip label="در دسترس" color="success" sx={{fontSize: "0.9rem"}}/>
                            <Chip label="رزرو موقت" color="warning" sx={{fontSize: "0.9rem"}}/>
                            <Chip label="رزرو شده" color="error" sx={{fontSize: "0.9rem"}}/>
                        </Box>

                        <Grid container spacing={1} sx={{padding: "20px", justifyContent: "center"}}>
                            {ticketReservations.sort((a, b) => a.reservation_seat - b.reservation_seat).map((res) => {
                                const norm = normalizeSeatStatus(res.reservation_status);
                                const muiColor = colorByStatus(norm);
                                const buttonColor = norm === "AVAILABLE" ? "#4caf50" : norm === "TEMPORARY" ? "#ff9800" : "#f44336";
                                return (
                                    <Button

                                        size="medium"
                                        variant="contained"
                                        disabled={norm !== "AVAILABLE"}
                                        onClick={() => handleReserveSeat(res.reservation_seat)}
                                        sx={{
                                            backgroundColor: buttonColor,
                                            color: "#fff",
                                            borderRadius: 1,
                                            boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
                                            "&:hover": {
                                                backgroundColor: norm === "AVAILABLE" ? "#45a049" : buttonColor,
                                            },
                                            fontSize: "1rem",
                                            padding: "8px",

                                            "&.Mui-disabled": {
                                                backgroundColor: buttonColor,
                                                color: "rgba(255, 255, 255, 0.7)",
                                            },
                                        }}
                                    >
                                        {res.reservation_seat}
                                    </Button>
                                );
                            })}
                        </Grid>

                        {/* پیام‌ها */}
                        {reservationLoading && <Typography sx={{mt: 2, paddingLeft: "20px", color: "#757575"}}>⏳ در حال
                            رزرو...</Typography>}
                        {reservationError && <Typography color="error" sx={{mt: 2, paddingLeft: "20px"}}>⚠️
                            خطا: {reservationError}</Typography>}
                        {paymentMessage && <Typography color="success.main"
                                                       sx={{mt: 2, paddingLeft: "20px"}}>{paymentMessage}</Typography>}
                    </DialogContent>

                    {/* دکمه‌های پایین */}
                    <DialogActions sx={{padding: "20px", justifyContent: "flex-end"}}>
                        <Button onClick={() => setSelectedTicket(null)} color="error" variant="contained"
                                sx={{backgroundColor: "#f44336", "&:hover": {backgroundColor: "#d32f2f"}}}>
                            بستن
                        </Button>
                    </DialogActions>
                </Dialog>
            )}

            {/* بخش پرداخت به خارج از شرط selectedTicket منتقل شد */}
            <section className="payment-section-container">
                {isLoggedIn && tempReservations.length > 0 && (
                    <div className="payment-section">
                        <form onSubmit={handlePayment} className="payment-form">
                            <h3>پرداخت رزروهای موقت من</h3>
                            <p>شما **{tempReservations.length}** رزرو موقت دارید. لطفا یکی را برای پرداخت انتخاب
                                کنید.</p>
                            <div className="input-group">
                                <label htmlFor="temp-reservation-select">انتخاب رزرو</label>
                                <select
                                    id="temp-reservation-select"
                                    value={tempReservationId}
                                    onChange={e => setTempReservationId(e.target.value)}
                                    required
                                    disabled={paymentLoading}
                                >
                                    <option value="">انتخاب کنید</option>
                                    {tempReservations.map(res => (
                                        <option key={res.reservation_id} value={res.reservation_id}>
                                            صندلی {res.reservation_seat} (رزرو موقت: {res.reservation_id})
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="input-group">
                                <label>روش پرداخت</label>
                                <select
                                    value={paymentMethod}
                                    onChange={e => setPaymentMethod(e.target.value)}
                                    required
                                    disabled={paymentLoading}
                                >
                                    <option value="">انتخاب کنید</option>
                                    <option value="WALLET">کیف پول</option>
                                    <option value="CREDIT_CARD">کارت اعتباری</option>
                                    <option value="CRYPTOCURRENCY">ارز دیجیتال</option>
                                </select>
                            </div>

                            <button type="submit" className="pay-btn"
                                    disabled={paymentLoading || !tempReservationId || !paymentMethod}>
                                {paymentLoading ? 'در حال پرداخت...' : 'پرداخت نهایی'}
                            </button>
                            {paymentError && <p className="error-message">{paymentError}</p>}
                            {paymentMessage && <p className="success-message">{paymentMessage}</p>}
                        </form>
                    </div>
                )}
            </section>


            <footer className="main-footer">
                <div className="footer-links">
                    <a href="/about">درباره ما</a>
                    <a href="/contact">تماس با ما</a>
                    <a href="/terms">قوانین و مقررات</a>
                </div>
                <div className="footer-info">
                    <span>نماد اعتماد الکترونیک</span>
                    <span>آیکون‌های شبکه‌های اجتماعی</span>
                </div>
            </footer>
        </div>
    );
};

export default Home;
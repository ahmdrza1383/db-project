import React, { useState, useEffect } from 'react';
import './Home.css';

const Home = () => {
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
        headers: { 'Content-Type': 'application/json' },
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

  // گرفتن جزییات بلیط فروخته نشده روی کلیک
  const fetchTicketDetails = async (ticket_id) => {
    setDetailsLoading(true);
    setDetailsError(null);
    setSelectedSeat(null);
    setPaymentMethod('');
    setPaymentMessage(null);
    setPaymentError(null);
    setTempReservationId('');

    try {
      const res = await fetch(`http://localhost:8000/api-test/ticket-details/${ticket_id}/`);
      const data = await res.json();
      if (res.ok && data.status === 'success') {
        setSelectedTicket(data.data);
        setSeats(data.data.reservations.sort((a, b) => a.reservation_seat - b.reservation_seat));
      } else {
        setDetailsError(data.message || 'خطا در دریافت جزییات بلیط');
      }
    } catch (error) {
      setDetailsError('خطا در ارتباط با سرور');
    } finally {
      setDetailsLoading(false);
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
              ? { ...seat, reservation_status: 'TEMPORARY', reservation_id: data.reservation.reservation_id, username: userInfo.username }
              : seat
          )
        );
        // Update the selectedTicket to show the new temporary reservation
        setSelectedTicket(prevTicket => {
          if (!prevTicket) return null;
          const updatedReservations = prevTicket.reservations.map(res =>
            res.reservation_seat === seat_number
              ? { ...res, reservation_status: 'TEMPORARY', reservation_id: data.reservation.reservation_id, username: userInfo.username }
              : res
          );
          return { ...prevTicket, reservations: updatedReservations };
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

  return (
    <div className="home-container">

      <header className="main-header">
        <div className="logo">
          <img src="https://images.unsplash.com/photo-1542454655-cfb29b67484b?q=80&w=2070" alt="Logo" />
        </div>

        <div className="header-actions">
          {!isLoggedIn ? (
            <>
              <a href="/login" className="btn-auth">ورود</a>
              <a href="/signup" className="btn-auth">ثبت‌نام</a>
            </>
          ) : (
            <>
              <a href="/profile" className="btn-auth">پروفایل</a>
              <button
                className="btn-auth"
                onClick={() => {
                  localStorage.removeItem('accessToken');
                  localStorage.removeItem('refreshToken');
                  localStorage.removeItem('userInfo');
                  // ⭐️⭐️⭐️ این خط که باعث پاک شدن رزروها می‌شد، حذف شد.
                  // localStorage.removeItem('tempReservations');
                  // ⭐️⭐️⭐️ برای حل مشکل، این خط را اضافه کنید تا وضعیت محلی نیز خالی شود.
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
                    <div key={ticket.ticket_id} className="ticket-card">
                      <h3>{ticket.origin_city} به {ticket.destination_city}</h3>
                      <p>شرکت: {ticket.company_name || ticket.airline_name || '-'}</p>
                      <p>تاریخ حرکت: {ticket.departure_start?.slice(0, 10) || ticket.departure_date || '-'}</p>
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
                <span className="ticket-type">{ticket.vehicle_type === 'FLIGHT' ? '✈️ پرواز' : ticket.vehicle_type === 'TRAIN' ? '🚆 قطار' : '🚌 اتوبوس'}</span>
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

      {/* نمایش جزئیات بلیط فروخته نشده انتخاب شده (طراحی جدید) */}
      {selectedTicket && (
        <section className="ticket-details-popup">
          {detailsLoading && <p>در حال بارگذاری جزئیات...</p>}
          {detailsError && <p style={{ color: 'red' }}>خطا: {detailsError}</p>}
          {!detailsLoading && !detailsError && (
            <>
              <div className="details-header">
                <h2>جزئیات بلیط</h2>
                <button className="close-btn" onClick={() => setSelectedTicket(null)}>
                  ✖️
                </button>
              </div>
              <div className="details-body">
                <div className="detail-row">
                  <span>مبدا:</span>
                  <strong>{selectedTicket.origin_city}</strong>
                </div>
                <div className="detail-row">
                  <span>مقصد:</span>
                  <strong>{selectedTicket.destination_city}</strong>
                </div>
                <div className="detail-row">
                  <span>تاریخ حرکت:</span>
                  <strong>{selectedTicket.departure_start?.slice(0, 10)}</strong>
                </div>
                <div className="detail-row">
                  <span>قیمت:</span>
                  <strong>{selectedTicket.price.toLocaleString()} تومان</strong>
                </div>
                <div className="detail-row">
                  <span>ظرفیت باقی‌مانده:</span>
                  <strong>{selectedTicket.remaining_capacity}</strong>
                </div>
                <div className="detail-row">
                  <span>نوع وسیله نقلیه:</span>
                  <strong>{selectedTicket.vehicle_type}</strong>
                </div>
              </div>

              {selectedTicket.vehicle_type === 'FLIGHT' && selectedTicket.vehicle_details && (
                <>
                  <div className="detail-row">
                    <span>خط هوایی:</span>
                    <strong>{selectedTicket.vehicle_details.airline_name}</strong>
                  </div>
                  <div className="detail-row">
                    <span>کلاس پرواز:</span>
                    <strong>{selectedTicket.vehicle_details.flight_class}</strong>
                  </div>
                  <div className="detail-row">
                    <span>تعداد توقف:</span>
                    <strong>{selectedTicket.vehicle_details.number_of_stop}</strong>
                  </div>
                  <div className="detail-row">
                    <span>کد پرواز:</span>
                    <strong>{selectedTicket.vehicle_details.flight_code}</strong>
                  </div>
                  <div className="detail-row">
                    <span>فرودگاه مبدا:</span>
                    <strong>{selectedTicket.vehicle_details.origin_airport}</strong>
                  </div>
                  <div className="detail-row">
                    <span>فرودگاه مقصد:</span>
                    <strong>{selectedTicket.vehicle_details.destination_airport}</strong>
                  </div>
                  <div className="detail-row">
                    <span>امکانات:</span>
                    <strong>{JSON.stringify(selectedTicket.vehicle_details.facility)}</strong>
                  </div>
                </>
              )}
              {selectedTicket.vehicle_type === 'TRAIN' && selectedTicket.vehicle_details && (
                <>
                  <div className="detail-row">
                    <span>ستاره قطار:</span>
                    <strong>{selectedTicket.vehicle_details.train_stars}</strong>
                  </div>
                  <div className="detail-row">
                    <span>انتخاب کوپه بسته:</span>
                    <strong>{selectedTicket.vehicle_details.choosing_a_closed_coupe ? 'بله' : 'خیر'}</strong>
                  </div>
                  <div className="detail-row">
                    <span>امکانات:</span>
                    <strong>{JSON.stringify(selectedTicket.vehicle_details.facility)}</strong>
                  </div>
                </>
              )}
              {selectedTicket.vehicle_type === 'BUS' && selectedTicket.vehicle_details && (
                <>
                  <div className="detail-row">
                    <span>نام شرکت:</span>
                    <strong>{selectedTicket.vehicle_details.company_name}</strong>
                  </div>
                  <div className="detail-row">
                    <span>نوع اتوبوس:</span>
                    <strong>{selectedTicket.vehicle_details.bus_type}</strong>
                  </div>
                  <div className="detail-row">
                    <span>تعداد صندلی‌ها:</span>
                    <strong>{selectedTicket.vehicle_details.number_of_chairs}</strong>
                  </div>
                  <div className="detail-row">
                    <span>امکانات:</span>
                    <strong>{JSON.stringify(selectedTicket.vehicle_details.facility)}</strong>
                  </div>
                </>
              )}
              <h3>رزروها</h3>
              <ul className="reservation-list">
                {selectedTicket.reservations
                  .sort((a, b) => a.reservation_id - b.reservation_id)
                  .map(res => (
                  <li key={res.reservation_id}>
                    <strong>شماره رزرو:</strong> {res.reservation_id}
                    <span>-</span>
                    <strong>وضعیت:</strong> {res.reservation_status}
                    <span>-</span>
                    <strong>صندلی:</strong> {res.reservation_seat}
                  </li>
                ))}
              </ul>

              {/* نمایش صندلی‌ها برای انتخاب */}
              <h3>انتخاب صندلی</h3>
              <div className="seats-container">
                {seats.map(seat => (
                  <button
                    key={seat.reservation_id}
                    className={`seat-btn ${seat.reservation_status !== 'NOT_RESERVED' ? 'reserved' : ''} ${selectedSeat === seat.reservation_seat ? 'selected' : ''}`}
                    disabled={seat.reservation_status !== 'NOT_RESERVED' || reservationLoading}
                    onClick={() => handleSeatSelection(seat.reservation_seat)}
                  >
                    {seat.reservation_seat}
                  </button>
                ))}
              </div>

              {/* پیام رزرو */}
              {reservationLoading && <p>در حال رزرو صندلی...</p>}
              {reservationError && <p className="error-message">خطا در رزرو: {reservationError}</p>}
              {paymentMessage && <p className="success-message">{paymentMessage}</p>}
            </>
          )}
        </section>
      )}

      {/* بخش پرداخت به خارج از شرط selectedTicket منتقل شد */}
      <section className="payment-section-container">
        {isLoggedIn && tempReservations.length > 0 && (
          <div className="payment-section">
            <form onSubmit={handlePayment} className="payment-form">
              <h3>پرداخت رزروهای موقت من</h3>
              <p>شما **{tempReservations.length}** رزرو موقت دارید. لطفا یکی را برای پرداخت انتخاب کنید.</p>
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

              <button type="submit" className="pay-btn" disabled={paymentLoading || !tempReservationId || !paymentMethod}>
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
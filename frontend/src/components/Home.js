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

  // وضعیت ورود
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    setIsLoggedIn(!!token);
  }, []);

  // بارگذاری بلیط‌های فروخته نشده
  useEffect(() => {
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
    try {
      const res = await fetch(`http://localhost:8000/api-test/ticket-details/${ticket_id}/`);
      const data = await res.json();
      if (res.ok && data.status === 'success') {
        setSelectedTicket(data.data);
      } else {
        setDetailsError(data.message || 'خطا در دریافت جزییات بلیط');
      }
    } catch (error) {
      setDetailsError('خطا در ارتباط با سرور');
    } finally {
      setDetailsLoading(false);
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
                  <div className="ticket-city">{ticket.origin_city}</div>
                  <span className="route-icon">➡️</span>
                  <div className="ticket-city">{ticket.destination_city}</div>
                </div>
                <div className="ticket-info">
                  <div className="info-item">
                    <span>تاریخ حرکت:</span>
                    <strong>{ticket.departure_start?.slice(0, 10)}</strong>
                  </div>
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
                {selectedTicket.reservations.map(res => (
                  <li key={res.reservation_id}>
                    <strong>شماره رزرو:</strong> {res.reservation_id}
                    <span>-</span>
                    <strong>وضعیت:</strong> {res.reservation_status}
                    <span>-</span>
                    <strong>صندلی:</strong> {res.reservation_seat}
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>
      )}



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
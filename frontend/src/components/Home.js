import React, { useState, useEffect } from 'react';
import './Home.css';

const popularDestinations = [
  { id: 1, name: 'استانبول', image: 'https://images.unsplash.com/photo-1542454655-cfb29b67484b?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3', price: '۳,۰۰۰,۰۰۰ تومان' },
  { id: 2, name: 'دبی', image: 'https://images.unsplash.com/photo-1542454655-cfb29b67484b?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3', price: '۴,۵۰۰,۰۰۰ تومان' },
  { id: 3, name: 'کیش', image: 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.iranhotelonline.com%2Fblog%2Fpost-511%2F%25D8%25AC%25D8%25A7%25D9%2587%25D8%25A7%25DB%258C-%25D8%25AF%25DB%258C%25D8%25AF%25D9%2586%25DB%258C-%25DA%25A9%25DB%258C%25D8%25B4-%25D8%25AF%25DB%258C%25D8%25AF%25D9%2586%25DB%258C-%25D9%2587%25D8%25A7%25DB%258C-%25DA%25A9%25DB%258C%25D8%25B4-%25D8%25A8%25D8%25A7-%25D8%25B9%25DA%25A9%25D8%25B3-%25D9%2588-%25D8%25A2%25D8%25AF%25D8%25B1%25D8%25B3%2F&psig=AOvVaw2idMA5kWk4ICn5w3CM9_hL&ust=1754650582684000&source=images&cd=vfe&opi=89978449&ved=0CBUQjRxqFwoTCKiM8vfE-I4DFQAAAAAdAAAAABAE', price: '۱,۵۰۰,۰۰۰ تومان' },
  { id: 4, name: 'شیراز', image: 'https://images.unsplash.com/photo-1542454655-cfb29b67484b?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3', price: '۹۰۰,۰۰۰ تومان' },
];

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

      {/* لیست بلیط‌های فروخته نشده */}
      <section className="available-tickets-section">
        <h2>بلیط‌های فروخته نشده</h2>
        {availableTickets.length === 0 && <p>بلیط فروخته نشده‌ای موجود نیست.</p>}
        <div className="results-list">
          {availableTickets.map(ticket => (
            <div
              key={ticket.ticket_id}
              className="ticket-card"
              style={{cursor: 'pointer'}}
              onClick={() => fetchTicketDetails(ticket.ticket_id)}
            >
              <h3>{ticket.origin_city} به {ticket.destination_city}</h3>
              <p>تاریخ حرکت: {ticket.departure_start?.slice(0, 10)}</p>
              <p>قیمت: {ticket.price.toLocaleString()} تومان</p>
              <p>نوع وسیله: {ticket.vehicle_type}</p>
            </div>
          ))}
        </div>
      </section>

      {/* نمایش جزئیات بلیط فروخته نشده انتخاب شده */}
      {selectedTicket && (
        <section className="ticket-details-popup">
          {detailsLoading && <p>در حال بارگذاری جزئیات...</p>}
          {detailsError && <p style={{color: 'red'}}>خطا: {detailsError}</p>}
          {!detailsLoading && !detailsError && (
            <>
              <h2>جزئیات بلیط</h2>
              <p>مبدا: {selectedTicket.origin_city}</p>
              <p>مقصد: {selectedTicket.destination_city}</p>
              <p>تاریخ حرکت: {selectedTicket.departure_start?.slice(0, 10)}</p>
              <p>قیمت: {selectedTicket.price.toLocaleString()} تومان</p>
              <p>ظرفیت کل: {selectedTicket.total_capacity}</p>
              <p>ظرفیت باقی‌مانده: {selectedTicket.remaining_capacity}</p>
              <p>وضعیت بلیط: {selectedTicket.ticket_status ? 'فروخته شده' : 'فروخته نشده'}</p>
              <p>نوع وسیله نقلیه: {selectedTicket.vehicle_type}</p>

              {selectedTicket.vehicle_type === 'FLIGHT' && selectedTicket.vehicle_details && (
                <>
                  <p>خط هوایی: {selectedTicket.vehicle_details.airline_name}</p>
                  <p>کلاس پرواز: {selectedTicket.vehicle_details.flight_class}</p>
                  <p>تعداد توقف: {selectedTicket.vehicle_details.number_of_stop}</p>
                  <p>کد پرواز: {selectedTicket.vehicle_details.flight_code}</p>
                  <p>فرودگاه مبدا: {selectedTicket.vehicle_details.origin_airport}</p>
                  <p>فرودگاه مقصد: {selectedTicket.vehicle_details.destination_airport}</p>
                  <p>امکانات: {JSON.stringify(selectedTicket.vehicle_details.facility)}</p>
                </>
              )}

              {selectedTicket.vehicle_type === 'TRAIN' && selectedTicket.vehicle_details && (
                <>
                  <p>ستاره قطار: {selectedTicket.vehicle_details.train_stars}</p>
                  <p>انتخاب کوپه بسته: {selectedTicket.vehicle_details.choosing_a_closed_coupe ? 'بله' : 'خیر'}</p>
                  <p>امکانات: {JSON.stringify(selectedTicket.vehicle_details.facility)}</p>
                </>
              )}

              {selectedTicket.vehicle_type === 'BUS' && selectedTicket.vehicle_details && (
                <>
                  <p>نام شرکت: {selectedTicket.vehicle_details.company_name}</p>
                  <p>نوع اتوبوس: {selectedTicket.vehicle_details.bus_type}</p>
                  <p>تعداد صندلی‌ها: {selectedTicket.vehicle_details.number_of_chairs}</p>
                  <p>امکانات: {JSON.stringify(selectedTicket.vehicle_details.facility)}</p>
                </>
              )}

              <h3>رزروها</h3>
              <ul>
                {selectedTicket.reservations.map(res => (
                  <li key={res.reservation_id}>
                    شماره رزرو: {res.reservation_id} - وضعیت: {res.reservation_status} - صندلی: {res.reservation_seat}
                  </li>
                ))}
              </ul>

              <button onClick={() => setSelectedTicket(null)}>بستن جزئیات</button>
            </>
          )}
        </section>
      )}

      <section className="popular-section">
        <h2>مقاصد پرطرفدار</h2>
        <div className="destination-cards">
          {popularDestinations.map(dest => (
            <div key={dest.id} className="destination-card">
              <img src={dest.image} alt={dest.name} className="card-image" />
              <div className="card-info">
                <h3>{dest.name}</h3>
                <p>{dest.price}</p>
              </div>
            </div>
          ))}
        </div>
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


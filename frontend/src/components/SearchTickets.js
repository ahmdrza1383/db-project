// frontend/src/components/SearchTickets.js

import React, { useState } from 'react';
import { Container, TextField, Button, Box, Typography, Card, CardContent, CircularProgress, Alert, FormControl, InputLabel, Select, MenuItem, Divider } from '@mui/material';
import { Link } from 'react-router-dom';
import axios from 'axios';

const SearchTickets = () => {
  const [searchParams, setSearchParams] = useState({
    origin_city: '',
    destination_city: '',
    departure_date: '',
    vehicle_type: '',
    min_price: '',
    max_price: '',
    company_name: '',
    flight_class: '',
    train_stars: '',
    bus_type: ''
  });
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setSearchParams({ ...searchParams, [e.target.name]: e.target.value });
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const token = localStorage.getItem('accessToken');

    // Create the payload by filtering out empty fields
    const payload = Object.fromEntries(
      Object.entries(searchParams).filter(([_, v]) => v != null && v !== '')
    );

    try {
      const response = await axios.post('http://localhost:8000/api-test/search-tickets/', payload, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setTickets(response.data.data);
      setLoading(false);
    } catch (err) {
      const errorMessage = err.response?.data?.message || 'خطای ناشناخته در جستجو.';
      setError(errorMessage);
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 5 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>جستجوی بلیط</Typography>
        <Button component={Link} to="/dashboard" variant="outlined">
          بازگشت به داشبورد
        </Button>
      </Box>

      {error && <Alert severity="error">{error}</Alert>}

      <Box component="form" onSubmit={handleSearch} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Typography variant="h6" sx={{ mt: 2 }}>فیلترهای الزامی</Typography>
        <TextField
          name="origin_city"
          label="مبدا"
          value={searchParams.origin_city}
          onChange={handleChange}
          required
        />
        <TextField
          name="destination_city"
          label="مقصد"
          value={searchParams.destination_city}
          onChange={handleChange}
          required
        />
        <TextField
          name="departure_date"
          label="تاریخ حرکت"
          type="date"
          value={searchParams.departure_date}
          onChange={handleChange}
          InputLabelProps={{ shrink: true }}
          required
        />

        <Divider sx={{ my: 2 }} />

        <Typography variant="h6">فیلترهای اختیاری</Typography>
        <FormControl fullWidth>
          <InputLabel>نوع وسیله نقلیه</InputLabel>
          <Select
            name="vehicle_type"
            value={searchParams.vehicle_type}
            onChange={handleChange}
            label="نوع وسیله نقلیه"
          >
            <MenuItem value="">_</MenuItem>
            <MenuItem value="FLIGHT">پرواز</MenuItem>
            <MenuItem value="TRAIN">قطار</MenuItem>
            <MenuItem value="BUS">اتوبوس</MenuItem>
          </Select>
        </FormControl>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            name="min_price"
            label="حداقل قیمت"
            type="number"
            value={searchParams.min_price}
            onChange={handleChange}
            fullWidth
          />
          <TextField
            name="max_price"
            label="حداکثر قیمت"
            type="number"
            value={searchParams.max_price}
            onChange={handleChange}
            fullWidth
          />
        </Box>

        <TextField
          name="company_name"
          label="نام شرکت"
          value={searchParams.company_name}
          onChange={handleChange}
        />

        <FormControl fullWidth>
          <InputLabel>کلاس پرواز</InputLabel>
          <Select
            name="flight_class"
            value={searchParams.flight_class}
            onChange={handleChange}
            label="کلاس پرواز"
          >
            <MenuItem value="">_</MenuItem>
            <MenuItem value="Economy">اکونومی</MenuItem>
            <MenuItem value="Business">بیزینس</MenuItem>
            <MenuItem value="First">فرست کلاس</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth>
          <InputLabel>ستاره قطار</InputLabel>
          <Select
            name="train_stars"
            value={searchParams.train_stars}
            onChange={handleChange}
            label="ستاره قطار"
          >
            <MenuItem value="">_</MenuItem>
            <MenuItem value={3}>3 ستاره</MenuItem>
            <MenuItem value={4}>4 ستاره</MenuItem>
            <MenuItem value={5}>5 ستاره</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth>
          <InputLabel>نوع اتوبوس</InputLabel>
          <Select
            name="bus_type"
            value={searchParams.bus_type}
            onChange={handleChange}
            label="نوع اتوبوس"
          >
            <MenuItem value="">_</MenuItem>
            <MenuItem value="VIP">VIP</MenuItem>
            <MenuItem value="Normal">معمولی</MenuItem>
          </Select>
        </FormControl>

        <Button type="submit" variant="contained" disabled={loading} sx={{ mt: 3 }}>
          {loading ? <CircularProgress size={24} /> : 'جستجوی بلیط'}
        </Button>
      </Box>

      <Box mt={4}>
        <Typography variant="h5" gutterBottom>نتایج جستجو</Typography>
        {tickets.length > 0 ? (
          tickets.map((ticket, index) => (
            <Card key={index} sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6">{ticket.origin_city} ➡️ {ticket.destination_city}</Typography>
                <Typography>تاریخ حرکت: {ticket.departure_date}</Typography>
                <Typography>قیمت: {ticket.price} تومان</Typography>
                <Typography>نوع وسیله: {ticket.vehicle_type}</Typography>
                {/* دکمه رزرو را اضافه کنید که به صفحه جزئیات بلیط هدایت کند */}
                <Button
                    variant="contained"
                    sx={{ mt: 2 }}
                    component={Link}
                    to={`/tickets/${ticket.ticket_id}`}
                >
                    رزرو
                </Button>
              </CardContent>
            </Card>
          ))
        ) : (
          !loading && <Alert severity="info">نتیجه‌ای یافت نشد.</Alert>
        )}
      </Box>
    </Container>
  );
};

export default SearchTickets;
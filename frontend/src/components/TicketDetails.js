// frontend/src/components/TicketDetails.js

import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Container, Typography, Button, Box, CircularProgress, Alert, Grid, Paper } from '@mui/material';
import axios from 'axios';

const TicketDetails = () => {
  const { id } = useParams();
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedSeat, setSelectedSeat] = useState(null);

  useEffect(() => {
    const fetchTicketDetails = async () => {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        setError('برای مشاهده جزئیات بلیط، باید وارد شوید.');
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`http://localhost:8000/api-test/ticket-details/${id}/`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        setTicket(response.data.data);
        setLoading(false);
      } catch (err) {
        const errorMessage = err.response?.data?.message || 'خطا در دریافت جزئیات بلیط.';
        setError(errorMessage);
        setLoading(false);
      }
    };
    fetchTicketDetails();
  }, [id]);

  const handleReserve = async () => {
    // This is a placeholder for the actual reservation logic
    const token = localStorage.getItem('accessToken');
    if (!selectedSeat) {
      alert('لطفاً یک صندلی را انتخاب کنید.');
      return;
    }

    try {
      // Assuming a POST endpoint exists for reserving a ticket
      await axios.post('http://localhost:8000/api-test/reserve-ticket/', {
        ticket_id: id,
        seat_number: selectedSeat
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      alert(`صندلی ${selectedSeat} با موفقیت رزرو شد!`);
      // You should update the UI or redirect the user here
    } catch (err) {
      alert('خطا در رزرو بلیط. لطفا دوباره تلاش کنید.');
    }
  };

  const getSeatStatus = (seatNumber) => {
    if (!ticket || !ticket.reservations) return 'available';

    const reservation = ticket.reservations.find(res => res.reservation_seat === seatNumber);
    if (reservation) {
      if (reservation.reservation_status === 'PAYED') return 'occupied';
      if (reservation.reservation_status === 'TEMPORARY') return 'reserved';
    }
    return 'available';
  };

  const renderSeats = () => {
    if (!ticket) return null;
    const seats = Array.from({ length: ticket.total_capacity }, (_, i) => i + 1);

    return (
      <Grid container spacing={1}>
        {seats.map(seatNumber => {
          const status = getSeatStatus(seatNumber);
          const isSelected = selectedSeat === seatNumber;
          return (
            <Grid item key={seatNumber}>
              <Paper
                onClick={() => status === 'available' && setSelectedSeat(seatNumber)}
                sx={{
                  width: 40,
                  height: 40,
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  cursor: status === 'available' ? 'pointer' : 'not-allowed',
                  backgroundColor: status === 'available' ? (isSelected ? '#1976d2' : '#f0f0f0') : (status === 'occupied' ? 'red' : 'orange'),
                  color: status === 'available' ? 'black' : 'white',
                  '&:hover': {
                    backgroundColor: status === 'available' && !isSelected ? '#ddd' : null,
                  }
                }}
              >
                {seatNumber}
              </Paper>
            </Grid>
          );
        })}
      </Grid>
    );
  };

  if (loading) return <Container sx={{ textAlign: 'center', mt: 5 }}><CircularProgress /><Typography>در حال بارگذاری...</Typography></Container>;
  if (error) return <Container sx={{ mt: 5 }}><Alert severity="error">{error}</Alert></Container>;
  if (!ticket) return <Container sx={{ mt: 5 }}><Alert severity="info">بلیط یافت نشد.</Alert></Container>;

  return (
    <Container maxWidth="md" sx={{ mt: 5 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>جزئیات بلیط</Typography>
        <Button component={Link} to="/search" variant="outlined">
          بازگشت به جستجو
        </Button>
      </Box>
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6">اطلاعات کلی بلیط</Typography>
            <Divider sx={{ my: 1 }} />
            <Typography>مبدا: {ticket.origin_city}, {ticket.origin_province}</Typography>
            <Typography>مقصد: {ticket.destination_city}, {ticket.destination_province}</Typography>
            <Typography>تاریخ حرکت: {new Date(ticket.departure_start).toLocaleString('fa-IR')}</Typography>
            <Typography>تاریخ رسیدن: {new Date(ticket.departure_end).toLocaleString('fa-IR')}</Typography>
            <Typography>قیمت: {ticket.price} تومان</Typography>
            <Typography>ظرفیت کل: {ticket.total_capacity}</Typography>
            <Typography>ظرفیت باقی‌مانده: {ticket.remaining_capacity}</Typography>
            <Typography>نوع وسیله: {ticket.vehicle_type}</Typography>

            <Box mt={3}>
              <Typography variant="h6">جزئیات وسیله نقلیه</Typography>
              <Divider sx={{ my: 1 }} />
              {ticket.vehicle_type === 'FLIGHT' && (
                <>
                  <Typography>نام ایرلاین: {ticket.vehicle_details.airline_name}</Typography>
                  <Typography>کلاس پرواز: {ticket.vehicle_details.flight_class}</Typography>
                  <Typography>کد پرواز: {ticket.vehicle_details.flight_code}</Typography>
                </>
              )}
              {ticket.vehicle_type === 'TRAIN' && (
                <>
                  <Typography>ستاره قطار: {ticket.vehicle_details.train_stars}</Typography>
                  <Typography>کوپه دربست: {ticket.vehicle_details.choosing_a_closed_coupe ? 'دارد' : 'ندارد'}</Typography>
                </>
              )}
              {ticket.vehicle_type === 'BUS' && (
                <>
                  <Typography>نام شرکت: {ticket.vehicle_details.company_name}</Typography>
                  <Typography>نوع اتوبوس: {ticket.vehicle_details.bus_type}</Typography>
                </>
              )}
              {ticket.vehicle_details?.facility && (
                <Box mt={1}>
                  <Typography>امکانات:</Typography>
                  <ul>
                    {Object.entries(ticket.vehicle_details.facility).map(([key, value]) => (
                      <li key={key}>{key}: {value ? 'دارد' : 'ندارد'}</li>
                    ))}
                  </ul>
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>انتخاب صندلی</Typography>
            <Typography>
              صندلی انتخاب شده: **{selectedSeat || 'هیچ'}**
            </Typography>
            <Box sx={{ my: 2 }}>
              {renderSeats()}
            </Box>
            <Button
              variant="contained"
              color="primary"
              onClick={handleReserve}
              disabled={!selectedSeat || ticket.remaining_capacity === 0}
              sx={{ mt: 2 }}
            >
              رزرو صندلی {selectedSeat}
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default TicketDetails;
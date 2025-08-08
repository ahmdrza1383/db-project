from django.urls import path

from . import views
from .views import available_tickets_view, get_user_temp_reservations_sql

app_name = 'api-test'

urlpatterns = [
    path('request-otp/', views.request_otp_view, name='request_otp'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('user-signup/', views.user_signup_view, name='user-signup'),
    path('user-update-profile/', views.update_user_profile_view, name='user-update-profile'),
    path('ticket-details/<int:ticket_id>/', views.get_ticket_details_view, name='ticket-details'),
    path('available-tickets/', available_tickets_view, name='available-tickets'),
    path('cities-list/', views.get_cities_list_view, name='cities-list'),
    path('search-tickets/', views.search_tickets_view, name='search-tickets'),
    path('reserve-ticket/', views.reserve_ticket_view, name='reserve-ticket'),
    path('reservations/<int:reservation_id>/cancel/', views.CancelReservationView.as_view(), name='cancel-reservation'),
    path('reservations/<int:reservation_id>/requests/', views.CreateRequestView.as_view(), name='create_request'),
    path('pay-tickets/', views.pay_ticket_view, name='pay-ticket'),
    path('admin/cancelled-reservations/', views.admin_cancelled_reservations_view, name='admin_cancelled_reservations'),
    path('admin/requests/', views.admin_request_list_view, name='admin_request_list'),
    path('admin/requests/<int:request_id>/approve/', views.admin_approve_request_view, name='admin_approve_request'),
    path('admin/requests/<int:request_id>/reject/', views.admin_reject_request_view, name='admin_reject_request'),
    path('user-bookings/', views.get_user_bookings_view, name='user-bookings'),
    path('report-issue/', views.report_ticket_issue_view, name='report-issue'),
    path('admin/reports/<int:report_id>/manage/', views.admin_manage_report_view, name='admin-manage-report'),
    path('admin/reports/', views.admin_get_reports_view, name='admin-get-reports'),
    path('user-profile/', views.get_user_profile_view, name='user-profile'),
    path('temporary-reservations/', get_user_temp_reservations_sql, name='temporary-reservations'),
]

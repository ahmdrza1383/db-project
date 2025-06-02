from django.urls import path

from . import views

app_name = 'api-test'

urlpatterns = [
    path('request-otp/', views.request_otp_view, name='request_otp'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('user-signup/', views.user_signup_view, name='user-signup'),
    path('user-update-profile/', views.update_user_profile_view, name='user-update-profile'),
    path('ticket-details/<int:ticket_id>/', views.get_ticket_details_view, name='ticket-details'),
    path('cities-list/', views.get_cities_list_view, name='cities-list'),
    path('search-tickets/', views.search_tickets_view, name='search-tickets'),
]

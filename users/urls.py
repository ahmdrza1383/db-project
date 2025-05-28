from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('profile/<str:username>/', views.UserView.as_view(), name='user_profile'),
]

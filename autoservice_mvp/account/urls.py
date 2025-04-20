from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import UserRegisterView, ServiceRegisterView, UserLoginView

app_name = 'account'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='user_register'),
    path('register/service/', ServiceRegisterView.as_view(), name='service_register'),
]
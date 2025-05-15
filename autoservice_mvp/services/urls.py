from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('profile/', views.service_profile, name='service_profile'),
    path('responses/', views.my_responses, name='my_responses'),
    path('service/<int:pk>/', views.service_detail, name='service_detail'),
    path('my/', views.my_services, name='my_services'),
    path('add/', views.add_service, name='add_service'),
    path('service/<int:pk>/edit/', views.edit_service, name='edit_service'),
    path('service/<int:pk>/delete/', views.delete_service, name='delete_service'),
    # path('service/<int:pk>/booking/', views.booking_create, name='booking_create'),
    # path('service/<int:pk>/booking/success/', views.booking_success, name='booking_success'),
    # path('service/<int:pk>/bookings/', views.service_bookings, name='service_bookings'),
    # path('service/<int:pk>/booking/available_slots/', views.available_slots, name='available_slots'),
    # path('service/<int:pk>/available-times/', views.get_available_times, name='available_times'),
    # path('available-times/<int:pk>/', views.get_available_times, name='available_times'),
]

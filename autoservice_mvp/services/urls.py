from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('profile/', views.service_profile, name='service_profile'),
    path('responses/', views.my_responses, name='my_responses'),
]

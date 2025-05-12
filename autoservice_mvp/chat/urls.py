from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('chat/<int:request_id>/', views.chat_between_users, name='chat_between_users'),
    path('chat/<int:request_id>/fetch/', views.fetch_messages, name='fetch_messages'),
    path('chat/<int:request_id>/service/<int:response_id>/', views.chat_with_service, name='chat_with_service'),
]
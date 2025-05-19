from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Основной чат между клиентом и сервисом по конкретному отклику
    path('chat/<int:request_id>/response/<int:response_id>/', views.chat_with_response, name='chat_with_response'),

    # Получение сообщений по этому отклику
    path('chat/<int:request_id>/response/<int:response_id>/fetch/', views.fetch_messages, name='fetch_messages'),
]

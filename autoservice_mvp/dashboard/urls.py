from django.urls import path
from . import views



urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('users/', views.user_list, name='admin_users'),
    path('users/<int:user_id>/block/', views.block_user, name='block_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/<int:user_id>/change_role/', views.change_user_role, name='change_user_role'),
    path('services/', views.service_list, name='admin_services'),
    path('services/', views.service_list, name='admin_services'),
    path('services/block/<int:service_id>/', views.block_service, name='block_service'),
    path('services/delete/<int:service_id>/', views.delete_service, name='delete_service'),
    path('requests/', views.request_list, name='admin_requests'),
    path('requests/', views.request_list, name='admin_requests'),
    path('requests/change_status/<int:request_id>/', views.change_request_status, name='change_request_status'),
    path('requests/delete/<int:request_id>/', views.delete_request, name='delete_request'),
    path('car/', views.carbase_create_view, name='car'),
]

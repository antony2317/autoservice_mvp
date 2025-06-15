from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'repairs'

urlpatterns = [

    path('dashboard/', views.service_dashboard, name='service_dashboard'),
    path('respond/<int:request_id>/', views.respond_to_request, name='respond_to_request'),
    #path('updates/', views.request_updates, name='request_updates'),
    path('create/', views.create_request, name='create_request'),
    path('accepted/', views.service_accepted_requests, name='accepted_requests'),
    path('confirm/<int:response_id>/', views.confirm_response, name='confirm_response'),
    path('confirm-response/<int:response_id>/', views.confirm_response, name='confirm_response'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('accept/<int:response_id>/', views.accept_response, name='accept_response'),
    path('response/<int:request_id>/change-status/', views.change_request_status, name='change_status'),
    path('requests/<int:request_id>/responses/', views.request_responses, name='request_responses'),
path('responses/<int:response_id>/reject/', views.reject_response, name='reject_response'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

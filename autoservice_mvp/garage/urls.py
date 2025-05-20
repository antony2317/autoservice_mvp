from django.urls import path
from .views import GarageView, CarDetailView, AddServiceRecordView, garage_search, EditServiceRecordView, \
    DeleteServiceRecordView
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('garage/', GarageView.as_view(), name='garage'),
    path('garage/add/', views.add_car, name='add_car'),
    path('ajax/get-models/', views.get_models, name='get_models'),
    path('garage/<int:pk>/', CarDetailView.as_view(), name='car_detail'),
    path('garage/<int:pk>/add-service/', AddServiceRecordView.as_view(), name='add_service_record'),
    path('api/garages/', garage_search, name='garage_search'),
    path('garage/<int:pk>/edit/', EditServiceRecordView.as_view(), name='edit_service_record'),
    path('garage/<int:pk>/delete/', DeleteServiceRecordView.as_view(), name='delete_service_record'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

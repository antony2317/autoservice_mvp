

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('account/', include('account.urls', namespace='account')),  # Все URL account
    path('garage/', include('garage.urls')),  # Все URL garage
    path('services/', include('services.urls')),   # Все URL services
    path('repairs/', include('repairs.urls')),
    path('chat/', include('chat.urls')),
]

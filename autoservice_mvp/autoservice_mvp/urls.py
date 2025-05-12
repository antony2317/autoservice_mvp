

from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('account/', include('account.urls', namespace='account')),
    path('garage/', include('garage.urls')),
    path('services/', include('services.urls')),
    path('repairs/', include('repairs.urls')),
    path('chat/', include('chat.urls', namespace='chat')),
    path('dashboard/', include(('dashboard.urls', 'dashboard'))),
    path('api/', include('api.urls')),

]

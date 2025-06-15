

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from main import views as error_views

handler404 = error_views.custom_404_view
handler500 = error_views.custom_500_view


def superuser_only(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect('home')  # Или вернуть 403, если хочешь
        return view_func(request, *args, **kwargs)
    return _wrapped_view

admin.site.login = superuser_only(admin.site.login)
admin.site.has_permission = lambda request: request.user.is_active and request.user.is_superuser


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
    path('reviews/', include('reviews.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

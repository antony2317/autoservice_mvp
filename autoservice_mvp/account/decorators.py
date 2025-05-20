from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from functools import wraps
from account.models import AutoService

def service_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_service:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                messages.error(request, "У вас нет доступа к этой странице")

                # Разный редирект по ролям
                if request.user.role in ['admin', 'manager']:
                    return redirect('dashboard:dashboard')
                elif request.user.role == 'service':
                    service = get_object_or_404(AutoService, user=request.user)
                    return redirect('services:service_detail', pk=service.pk)
                elif request.user.role == 'customer':
                    return redirect('home')
                else:
                    return redirect('home')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator



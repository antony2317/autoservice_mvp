from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from account.models import AutoService



class RoleRequiredMixin:
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Пожалуйста, войдите в систему")
            return redirect('login')

        if request.user.role not in self.allowed_roles:
            messages.error(request, "У вас нет доступа к этой странице")

            if request.user.role in ['admin', 'manager']:
                return redirect('dashboard:dashboard')
            elif request.user.role == 'service':
                service = get_object_or_404(AutoService, user=request.user)
                return redirect('services:service_detail', pk=service.pk)
            elif request.user.role == 'customer':
                return redirect('home')
            else:
                return redirect('home')

        return super().dispatch(request, *args, **kwargs)

        return super().dispatch(request, *args, **kwargs)



class AnonymousRequiredMixin:
    redirect_url = 'home'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.redirect_url)
        return super().dispatch(request, *args, **kwargs)

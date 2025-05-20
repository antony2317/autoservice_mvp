from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from account.models import User, AutoService
from repairs.models import RepairRequest
from django.contrib.auth import get_user_model
from django.db.models import Case, When, Value, IntegerField

from account.decorators import role_required


def is_admin(user):
    return user.is_superuser or user.is_staff

@role_required(['admin', 'manager'])
def dashboard(request):
    User = get_user_model()
    users_count = User.objects.filter(role='customer').exclude(is_superuser=True).count()

    context = {
        'users_count': users_count,
        'services_count': AutoService.objects.count(),
        'requests_count': RepairRequest.objects.count(),
    }
    return render(request, 'dashboard/dashboard.html', context)
@role_required(['admin', 'manager'])
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.filter(role__in=['manager', 'customer']).exclude(is_superuser=True).annotate(
        role_priority=Case(
            When(role='manager', then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        )
    ).order_by('role_priority', 'username')

    return render(request, 'dashboard/users.html', {'users': users})

@role_required(['admin', 'manager'])
@user_passes_test(is_admin)
def block_user(request, user_id):
    user = get_object_or_404(User, id=user_id, role='customer')  # Добавляем проверку роли
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        msg = "Пользователь заблокирован" if not user.is_active else "Пользователь разблокирован"
        messages.success(request, msg)
    return redirect('dashboard:admin_users')

@role_required(['admin', 'manager'])
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id, role='customer')  # Добавляем проверку роли
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Пользователь удалён")
    return redirect('dashboard:admin_users')

@role_required(['admin', 'manager'])
@user_passes_test(is_admin)
def change_user_role(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        new_role = request.POST.get('new_role')
        if new_role in ['customer', 'service', 'manager']:
            user.role = new_role
            user.save()

            if new_role == 'service':
                AutoService.objects.get_or_create(user=user, defaults={'name': f"Сервис {user.username}"})

            messages.success(request, f"Роль пользователя изменена на {new_role}")

    return redirect('dashboard:admin_users')

@role_required(['admin', 'manager'])
@user_passes_test(is_admin)
def service_list(request):
    search_query = request.GET.get('search', '')

    services = AutoService.objects.select_related('user').all()

    if search_query:
        services = services.filter(name__icontains=search_query)

    return render(request, 'dashboard/services.html', {
        'services': services,
        'search_query': search_query
    })

@role_required(['admin', 'manager'])
@user_passes_test(is_admin)
def block_service(request, service_id):
    service = get_object_or_404(AutoService, id=service_id)
    if request.method == 'POST':
        service.user.is_active = not service.user.is_active
        service.user.save()
        msg = "Сервис заблокирован" if not service.user.is_active else "Сервис разблокирован"
        messages.success(request, msg)
    return redirect('dashboard:admin_services')

@role_required(['admin', 'manager'])
@user_passes_test(is_admin)
def delete_service(request, service_id):
    service = get_object_or_404(AutoService, id=service_id)
    if request.method == 'POST':
        service.user.delete()  # Удаляем связанного пользователя
        messages.success(request, "Сервис удалён")
    return redirect('dashboard:admin_services')

@role_required(['admin', 'manager'])
@user_passes_test(is_admin)
def request_list(request):
    requests = RepairRequest.objects.select_related('executor', 'user', 'car').all()
    executors = {r.executor for r in requests if r.executor}
    return render(request, 'dashboard/requests.html', {
        'requests': requests,
        'executors': executors
    })

@role_required(['admin', 'manager'])
@user_passes_test(is_admin)
def change_request_status(request, request_id):
    req = get_object_or_404(RepairRequest, id=request_id)
    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        if new_status in dict(RepairRequest.STATUS_CHOICES):
            req.status = new_status
            req.save()
            messages.success(request, f'Статус заявки #{req.id} изменен на {req.get_status_display()}')
    return redirect('dashboard:admin_requests')

@role_required(['admin', 'manager'])
@user_passes_test(is_admin)
def delete_request(request, request_id):
    req = get_object_or_404(RepairRequest, id=request_id)
    if request.method == 'POST':
        req.delete()
        messages.success(request, f'Заявка #{request_id} удалена')
    return redirect('dashboard:admin_requests')

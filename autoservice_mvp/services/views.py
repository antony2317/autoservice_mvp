from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from .forms import AutoServiceProfileForm, ServiceForm, MasterForm
from account.models import AutoService
from repairs.models import RepairResponse, RepairRequest
from .models import Service
from reviews.models import Review
from django.http import JsonResponse
from datetime import datetime, timedelta, time
from django.db.models import F, ExpressionWrapper, DateTimeField
from django.db.models.functions import Cast

from reviews.forms import ReviewForm


@login_required
def service_profile(request):
    if not request.user.is_service:
        return redirect('home')


    auto_service = get_object_or_404(AutoService, user=request.user)

    if request.method == 'POST':
        form = AutoServiceProfileForm(request.POST, instance=auto_service)
        if form.is_valid():
            form.save()
            return redirect('services:service_profile')
    else:
        form = AutoServiceProfileForm(instance=auto_service)

    return render(request, 'services/service_profile.html', {'form': form, 'auto_service': auto_service})



def my_responses(request):
    all_responses = RepairResponse.objects.filter(
        service=request.user,
        is_accepted=False
    ).select_related('repair_request')


    responses = [r for r in all_responses if not r.repair_request.has_accepted_response]

    return render(request, 'services/my_responses.html', {'responses': responses})


def service_detail(request, pk):
    service = get_object_or_404(AutoService, pk=pk)
    services = service.services.all()
    masters = service.masters.all()
    is_user = request.user == service.user

    can_leave_review = request.user.is_authenticated and request.user != service.user

    # Отзывы для данного сервиса (через user-сервис)
    reviews = Review.objects.filter(service=service.user).order_by('-created_at')

    if request.user.is_authenticated:
        has_reviewed = Review.objects.filter(user=request.user, service=service.user).exists()
    else:
        has_reviewed = False

    can_leave_review = request.user.is_authenticated and request.user != service.user and not has_reviewed

    # Инициализируем формы по умолчанию
    service_form = ServiceForm()
    master_form = MasterForm()
    review_form = ReviewForm(user=request.user, service=service.user)

    if request.method == 'POST':
        if is_user:
            # владельцу не нужно обрабатывать отзывы
            if 'add_service' in request.POST:
                service_form = ServiceForm(request.POST)
                if service_form.is_valid():
                    new_service = service_form.save(commit=False)
                    new_service.autoservice = service
                    new_service.save()
                    return redirect('services:service_detail', pk=pk)
            elif 'add_master' in request.POST:
                master_form = MasterForm(request.POST)
                if master_form.is_valid():
                    new_master = master_form.save(commit=False)
                    new_master.autoservice = service
                    new_master.save()
                    return redirect('services:service_detail', pk=pk)
        else:
            # пользователь оставляет отзыв
            if 'add_review' in request.POST:
                review_form = ReviewForm(request.POST, user=request.user, service=service.user)
                if review_form.is_valid():
                    review = review_form.save(commit=False)
                    review.service = service.user
                    review.user = request.user
                    review.save()
                    return redirect('services:service_detail', pk=pk)

    context = {
        'service': service,
        'services': services,
        'masters': masters,
        'service_form': service_form,
        'master_form': master_form,
        'is_user': is_user,
        'reviews': reviews,
        'review_form': review_form,
        'can_leave_review': can_leave_review,
        'has_reviewed': has_reviewed,
    }
    return render(request, 'services/index.html', context)



@login_required
def add_service(request):
    autoservice = get_object_or_404(AutoService, user=request.user)

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.autoservice = autoservice
            service.save()
            return redirect('services:my_services')
    else:
        form = ServiceForm()

    return render(request, 'services/edit_service.html', {'form': form})


@login_required
def my_services(request):
    autoservice = get_object_or_404(AutoService, user=request.user)
    services = autoservice.services.all()
    return render(request, 'services/my_services.html', {'services': services})


def edit_service(request, pk):
    service = get_object_or_404(Service, pk=pk)

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('services:service_detail', pk=service.autoservice.pk)
    else:
        form = ServiceForm(instance=service)

    return render(request, 'services/edit_service.html', {'form': form, 'service': service})

def delete_service(request, pk):
    service = get_object_or_404(Service, pk=pk)

    # Проверяем, что текущий пользователь является владельцем автосервиса
    if service.autoservice.user != request.user:
        return redirect('unauthorized')  # или 403, в зависимости от вашей логики

    if request.method == 'POST':
        service.delete()
        return redirect('services:service_detail', pk=service.autoservice.pk)


def masters_list(request):
    service = get_object_or_404(AutoService, user=request.user)
    masters = service.masters.all()

    if request.method == 'POST':
        form = MasterForm(request.POST)
        if form.is_valid():
            master = form.save(commit=False)
            master.autoservice = service
            master.save()
            return redirect('services:masters_list')
    else:
        form = MasterForm()

    return render(request, 'services/masters_list.html', {
        'masters': masters,
        'form': form
    })
# @login_required
# def booking_create(request, pk):
#     service_center = get_object_or_404(AutoService, pk=pk)
#
#     if request.method == 'POST':
#         form = BookingForm(request.POST, autoservice=service_center)
#         if form.is_valid():
#             booking = Booking(
#                 user=request.user,
#                 service=form.cleaned_data['service'],
#                 date=form.cleaned_data['date'],
#                 time=form.cleaned_data['time']
#             )
#             booking.save()
#             return redirect('services:booking_success', pk=booking.pk)
#     else:
#         form = BookingForm(autoservice=service_center)
#
#     return render(request, 'services/booking_create.html', {
#         'form': form,
#         'service_center': service_center
#     })


# def booking_success(request, pk):
#     booking = get_object_or_404(Booking, pk=pk)
#     service = booking.service.autoservice  # или booking.service, если нужно
#
#     return render(request, 'services/booking_success.html', {
#         'booking': booking,
#         'service': service,  # ← добавили!
#     })


# @login_required

# def service_bookings(request, pk):
#     service = get_object_or_404(AutoService, pk=pk)
#
#     # Добавляем виртуальное поле date_time
#     bookings = Booking.objects.filter(service__autoservice=service)
#     bookings = bookings.annotate(
#         date_time=ExpressionWrapper(
#             Cast(F('date'), output_field=DateTimeField()) +
#             Cast(F('time'), output_field=DateTimeField()),
#             output_field=DateTimeField()
#         )
#     ).order_by('-date_time')
#
#     # Фильтрация
#     selected_service = request.GET.get('service')
#     selected_date = request.GET.get('date')
#
#     if selected_service:
#         bookings = bookings.filter(service_id=selected_service)
#
#     if selected_date:
#         try:
#             date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
#             bookings = bookings.filter(date=date_obj)
#         except ValueError:
#             pass  # некорректный формат даты
#
#     services = service.services.all()
#
#     context = {
#         'service': service,
#         'bookings': bookings,
#         'services': services,
#         'selected_service': selected_service,
#         'selected_date': selected_date,
#     }
#     return render(request, 'services/service_bookings.html', context)


# def get_available_slots(service, date):
#     start = time(9, 0)
#     end = time(18, 0)
#     slot_duration = timedelta(minutes=60)
#
#     bookings = Booking.objects.filter(service=service, date_time__date=date)
#     busy_times = set(b.date_time.time() for b in bookings)
#
#     slots = []
#     current = datetime.combine(date, start)
#     end_datetime = datetime.combine(date, end)
#
#     while current < end_datetime:
#         if current.time() not in busy_times:
#             slots.append(current.time().strftime('%H:%M'))
#         current += slot_duration
#
#     return slots


# def available_slots(request, pk):
#     autoservice = get_object_or_404(AutoService, pk=pk)
#     service_id = request.GET.get('service_id')
#     date_str = request.GET.get('date')
#
#     if not (service_id and date_str):
#         return JsonResponse({'slots': []})
#
#     try:
#         date = datetime.strptime(date_str, '%Y-%m-%d').date()
#         service = autoservice.services.get(id=service_id)
#     except Exception:
#         return JsonResponse({'slots': []})
#
#     slots = get_available_slots(service, date)
#     return JsonResponse({'slots': slots})



# def get_available_times(request, pk):
#     date_str = request.GET.get('date')
#     if not date_str:
#         return JsonResponse({'slots': []})
#
#     try:
#         selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
#     except ValueError:
#         return JsonResponse({'slots': []})
#
#     # Получаем сервис
#     try:
#         autoservice = AutoService.objects.get(pk=pk)
#     except AutoService.DoesNotExist:
#         return JsonResponse({'slots': []})
#
#     # Получаем день недели (0 = понедельник, 6 = воскресенье)
#     weekday = selected_date.weekday()
#
#     # Получаем рабочие часы на этот день
#     try:
#         work_hours = autoservice.working_hours.get(day_of_week=weekday)
#     except WorkingHours.DoesNotExist:
#         return JsonResponse({'slots': []})  # В этот день сервис не работает
#
#     # Генерируем возможные интервалы по 30 минут
#     start = datetime.combine(selected_date, work_hours.start_time)
#     end = datetime.combine(selected_date, work_hours.end_time)
#
#     slots = []
#     while start < end:
#         slots.append(start.time())
#         start += timedelta(minutes=30)
#
#     # Получаем уже занятые слоты именно в этом сервисе
#     booked_times = Booking.objects.filter(
#         service__autoservice=autoservice,
#         date=selected_date
#     ).values_list('time', flat=True)
#
#     # Фильтруем
#     available_slots = [t.strftime('%H:%M') for t in slots if t not in booked_times]
#
#     return JsonResponse({'slots': available_slots})

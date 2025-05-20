from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import RepairRequestForm, RepairResponseForm
from .models import RepairRequest, RepairResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from account.decorators import service_required, role_required
from .tasks import notify_user_about_response
from django.utils import timezone
from garage.models import ServiceRecord


@role_required(['service'])
@login_required
def service_dashboard(request):
    # Проверяем, что пользователь - сервис (новый вариант)
    if request.user.role != 'service':
        return redirect('home')

    new_requests = RepairRequest.objects.exclude(
        responses__service=request.user
    ).filter(status='new').select_related('user', 'car')

    accepted_requests = RepairResponse.objects.filter(
        service=request.user,
        is_accepted=True
    ).select_related('repair_request__user', 'repair_request__car')

    if request.user.role == 'customer':
        my_requests = RepairRequest.objects.filter(
            user=request.user
        ).prefetch_related('responses')
    else:
        my_requests = None

    return render(request, 'repairs/dashboard.html', {
        'new_requests': new_requests,
        'accepted_requests': accepted_requests,
        'my_requests': my_requests,
    })


@role_required(['service'])
@require_POST
@login_required
def respond_to_request(request, request_id):
    repair_request = get_object_or_404(RepairRequest, id=request_id)

    if request.method == 'POST':
        if not hasattr(request.user, 'is_service') or not request.user.is_service:
            messages.error(request, "Только сервисы могут отвечать на заявки")
            return redirect('repairs:service_dashboard')

        try:
            response = RepairResponse(
                repair_request=repair_request,
                service=request.user,
                proposed_price=request.POST.get('proposed_price'),
                proposed_date=request.POST.get('proposed_date'),
                is_accepted=False
            )
            response.full_clean()
            response.save()

            print("Email пользователя:", repair_request.user.email)

            notify_user_about_response.delay(
                user_email=repair_request.user.email,
                service_name=request.user.username,
                price=response.proposed_price,
                date=str(response.proposed_date)
            )


            messages.success(request, "Ваше предложение успешно отправлено!")
            return redirect('repairs:service_dashboard')

        except ValidationError as e:
            messages.error(request, f"Ошибка валидации: {e}")
        except Exception as e:
            messages.error(request, f"Произошла ошибка: {str(e)}")

    return redirect('repairs:service_dashboard')


@login_required
def accepted_responses_view(request):
    responses = RepairResponse.objects.filter(service=request.user, is_accepted=True)
    status_choices = RepairRequest.STATUS_CHOICES

    return render(request, 'repairs/accept_response.html', {
        'responses': responses,
        'status_choices': status_choices,
    })


@role_required(['service', 'admin', 'manager'])
def change_request_status(request, request_id):
    repair_request = get_object_or_404(RepairRequest, id=request_id)

    # Только автосервис может менять статус
    if not request.user.is_authenticated or not hasattr(request.user, 'autoservice'):
        messages.error(request, "Только авторизованный автосервис может менять статус.")
        return redirect('repairs:accepted_responses')

    new_status = request.POST.get('status')
    valid_statuses = dict(RepairRequest.STATUS_CHOICES)

    if new_status in valid_statuses:
        previous_status = repair_request.status
        repair_request.status = new_status
        repair_request.save()

        # Отправить email, если статус стал "Завершена"
        if new_status == 'completed' and previous_status != 'completed':
            # Создаем запись в истории обслуживания
            ServiceRecord.objects.create(
                car=repair_request.car,
                autoservice=getattr(request.user, 'autoservice', None),
                date=timezone.now().date(),
                mileage=repair_request.car.mileage,  # или пробег, если есть в заявке
                service_type=getattr(repair_request, 'service_type', 'Ремонт'),
                description=getattr(repair_request, 'description', ''),
                cost=None,  # Можно расширить форму, чтобы получать стоимость при закрытии
                created_by=request.user
            )

            send_mail(
                subject='Ваша заявка завершена',
                message=(
                    f'Здравствуйте, {repair_request.user.username}!\n\n'
                    f'Ваша заявка на ремонт автомобиля "{repair_request.car}" была завершена.\n'
                    f'Спасибо, что воспользовались нашим сервисом!'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[repair_request.user.email],
                fail_silently=False,
            )

        messages.success(request, "Статус успешно обновлён.")
    else:
        messages.error(request, "Недопустимый статус.")

    return redirect('repairs:accepted_requests')


@role_required(['customer'])
@login_required
def create_request(request):
    if request.method == 'POST':
        form = RepairRequestForm(request.POST, user=request.user)
        if form.is_valid():
            repair_request = form.save(commit=False)
            repair_request.user = request.user
            repair_request.save()
            return redirect('garage')
    else:
        form = RepairRequestForm(user=request.user)

    return render(request, 'repairs/create_request.html', {'form': form})


@role_required(['service'])
@login_required
@service_required
def service_accepted_requests(request):
    accepted_responses = RepairResponse.objects.filter(
        service=request.user,
        is_accepted=True
    ).select_related('repair_request__car', 'repair_request__user') \
     .order_by('-repair_request__created_at')  # Сортировка по дате создания заявки (новые — первыми)

    return render(request, 'repairs/service_accepted_requests.html', {
        'responses': accepted_responses
    })


@role_required(['customer'])
@login_required
def confirm_response(request, response_id):
    response = get_object_or_404(RepairResponse, id=response_id, repair_request__user=request.user)

    repair_request = response.repair_request
    repair_request.status = 'in_progress'
    repair_request.save()

    RepairResponse.objects.filter(repair_request=repair_request).update(is_accepted=False)

    response.is_accepted = True
    response.save()

    return redirect('garage')


@role_required(['service'])
@login_required
def user_requests(request):
    repair_requests = RepairRequest.objects.filter(user=request.user).prefetch_related('responses')
    return render(request, 'repairs/user_requests.html', {'repair_requests': repair_requests})



@require_POST
@login_required
def accept_response(request, response_id):
    response = get_object_or_404(RepairResponse, id=response_id)

    if request.user == response.repair_request.user:
        executor = getattr(response.service, 'autoservice', None)
        if executor is None:
            messages.error(request, 'Для сервиса не задан исполнитель (AutoService)')
        else:
            response.is_accepted = True
            response.save()

            repair_request = response.repair_request
            repair_request.status = 'in_progress'
            repair_request.executor = executor
            repair_request.save()

            messages.success(request, 'Предложение принято! Заявка в работе.')
    else:
        messages.error(request, 'Ошибка: у вас нет прав для этого действия')

    return redirect(request.META.get('HTTP_REFERER', '/'))

@role_required(['service'])
@login_required
def my_requests(request):
    repair_requests = RepairRequest.objects.filter(user=request.user).order_by('-created_at').prefetch_related('responses')
    return render(request, 'chat/chat_room.html', {'repair_requests': repair_requests})




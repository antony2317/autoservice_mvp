from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import RepairRequestForm, RepairResponseForm
from .models import RepairRequest, RepairResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

from account.decorators import service_required
from .tasks import notify_user_about_response





@login_required
def service_dashboard(request):
    new_requests = RepairRequest.objects.exclude(
        responses__service=request.user
    ).filter(status='new').select_related('user', 'car')

    accepted_requests = RepairResponse.objects.filter(
        service=request.user,
        is_accepted=True
    ).select_related('repair_request__user', 'repair_request__car')

    if hasattr(request.user, 'is_client') and request.user.is_client:
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


@require_POST
@login_required
def respond_to_request(request, request_id):
    repair_request = get_object_or_404(RepairRequest, id=request_id)

    if request.method == 'POST':
        if not hasattr(request.user, 'is_service') or not request.user.is_service:
            messages.error(request, "Только сервисы могут отвечать на заявки")
            return redirect('repairs:dashboard')

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
            return redirect('repairs:dashboard')

        except ValidationError as e:
            messages.error(request, f"Ошибка валидации: {e}")
        except Exception as e:
            messages.error(request, f"Произошла ошибка: {str(e)}")

    return redirect('repairs:service_dashboard')


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


@login_required
@service_required
def service_accepted_requests(request):
    accepted_responses = RepairResponse.objects.filter(
        service=request.user,
        is_accepted=True
    ).select_related('repair_request__car', 'repair_request__user')

    return render(request, 'repairs/service_accepted_requests.html', {
        'responses': accepted_responses
    })



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


@login_required
def user_requests(request):
    repair_requests = RepairRequest.objects.filter(user=request.user).prefetch_related('responses')
    return render(request, 'repairs/user_requests.html', {'repair_requests': repair_requests})



@require_POST
@login_required
def accept_response(request, response_id):
    response = get_object_or_404(RepairResponse, id=response_id)

    if request.user == response.repair_request.user:
        response.is_accepted = True
        response.save()
        response.repair_request.status = 'in_progress'
        response.repair_request.save()

        messages.success(request, 'Предложение принято! Заявка в работе.')
    else:
        messages.error(request, 'Ошибка: у вас нет прав для этого действия')

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def my_requests(request):
    repair_requests = RepairRequest.objects.filter(user=request.user).order_by('-created_at').prefetch_related('responses')
    return render(request, 'chat/chat_room.html', {'repair_requests': repair_requests})

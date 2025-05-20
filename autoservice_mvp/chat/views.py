from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from repairs.models import RepairRequest, RepairResponse
from .models import ChatMessage
from account.mixins import RoleRequiredMixin


@login_required
def chat_with_response(request, request_id, response_id):
    repair_request = get_object_or_404(RepairRequest, id=request_id)
    repair_response = get_object_or_404(RepairResponse, id=response_id, repair_request=repair_request)

    # Проверка доступа: либо клиент, либо сервис, ответивший на эту заявку
    if request.user != repair_request.user and request.user != repair_response.service:
        messages.error(request, "У вас нет доступа к этому чату.")
        return redirect('garage')

    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            ChatMessage.objects.create(
                repair_request=repair_request,
                response=repair_response,
                sender=request.user,
                receiver=repair_response.service if request.user == repair_request.user else repair_request.user,
                message=message_text
            )
            return redirect('chat:chat_with_response', request_id=request_id, response_id=response_id)

    chat_messages = ChatMessage.objects.filter(
        repair_request=repair_request,
        response=repair_response
    ).order_by('timestamp')

    receiver = repair_response.service if request.user == repair_request.user else repair_request.user

    return render(request, 'chat/chat_room.html', {
        'repair_request': repair_request,
        'repair_response': repair_response,
        'chat_messages': chat_messages,
        'receiver': receiver,
    })


@login_required
def fetch_messages(request, request_id, response_id):
    repair_request = get_object_or_404(RepairRequest, id=request_id)
    repair_response = get_object_or_404(RepairResponse, id=response_id, repair_request=repair_request)

    if request.user != repair_request.user and request.user != repair_response.service:
        return JsonResponse({'error': 'Access denied'}, status=403)

    messages = ChatMessage.objects.filter(
        repair_request=repair_request,
        response=repair_response
    ).order_by('timestamp')

    messages_data = [
        {
            'sender': message.sender.username,
            'message': message.message,
            'timestamp': message.timestamp.strftime('%H:%M %d.%m.%Y')
        }
        for message in messages
    ]

    return JsonResponse({'messages': messages_data})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from repairs.models import RepairRequest, RepairResponse
from .models import ChatMessage


@login_required
def chat_between_users(request, request_id):
    repair_request = get_object_or_404(RepairRequest, id=request_id)

    if not (
        request.user == repair_request.user or
        repair_request.responses.filter(service=request.user).exists()
    ):
        messages.error(request, "У вас нет доступа к этому чату.")
        return redirect('garage')

    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            ChatMessage.objects.create(
                repair_request=repair_request,
                sender=request.user,
                receiver=repair_request.user if request.user.is_service else repair_request.responses.first().service,
                message=message_text
            )
            return redirect('chat:chat_between_users', request_id=request_id)

    chat_messages = ChatMessage.objects.filter(repair_request=repair_request).order_by('timestamp')

    receiver = (
        repair_request.responses.first().service if request.user == repair_request.user
        else repair_request.user
    )

    return render(request, 'chat/chat_room.html', {
        'repair_request': repair_request,
        'chat_messages': chat_messages,
        'receiver': receiver,
    })


@login_required
def fetch_messages(request, request_id):
    repair_request = get_object_or_404(RepairRequest, id=request_id)

    if not (
        request.user == repair_request.user or
        repair_request.responses.filter(service=request.user).exists()
    ):
        return JsonResponse({'error': 'Access denied'}, status=403)

    messages = ChatMessage.objects.filter(
        repair_request=repair_request
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


def chat_with_service(request, repair_request_id, response_id):
    repair_request = get_object_or_404(RepairRequest, id=repair_request_id)

    response = get_object_or_404(RepairResponse, id=response_id)

    chat = ChatMessage.objects.filter(repair_request=repair_request, sender=request.user, receiver=response.service).first()

    if not chat:
        chat = ChatMessage.objects.create(
            repair_request=repair_request,
            sender=request.user,
            receiver=response.service,
            message="Начало общения в чате."
        )

    chat_messages = ChatMessage.objects.filter(repair_request=repair_request).order_by('timestamp')

    return render(request, 'chat/chat_room.html', {'chat': chat, 'messages': chat_messages})
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatMessage
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
@login_required
def chat_room(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    return render(request, 'chat/chat_room.html', {
        'receiver': receiver,
    })


@login_required
def send_message(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        message_text = request.POST.get('message')
        receiver = get_object_or_404(User, id=receiver_id)

        ChatMessage.objects.create(
            sender=request.user,
            receiver=receiver,
            message=message_text
        )
        return redirect('chat_room', sender_id=request.user.id, receiver_id=receiver_id)

    return redirect('chat_list')


@login_required
def chat_list(request):
    # Все пользователи, с которыми есть переписка
    users = User.objects.filter(
        Q(received_messages__sender=request.user) |
        Q(sent_messages__receiver=request.user)
    ).distinct()

    return render(request, 'chat/chat_list.html', {'users': users})
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from chat.models import ChatMessage
from repairs.models import RepairRequest  # Убедись, что путь к модели правильный

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]

        print(f"[WebSocket] Попытка подключения от: {self.user} в комнату: {self.room_name}")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"[WebSocket] Подключение принято: {self.user}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = self.user

        # Сохраняем сообщение в БД
        await save_message(self.room_name, message, sender)

        # Отправляем сообщение в группу
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': sender.username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username']
        }))


@sync_to_async
def save_message(room_id, message, sender):
    try:
        request = RepairRequest.objects.get(id=room_id)
    except RepairRequest.DoesNotExist:
        print(f"RepairRequest #{room_id} не найден.")
        return

    # Автосервис — это любой пользователь, кроме владельца заявки
    if sender == request.user:
        receiver = User.objects.filter(is_staff=True).first()
    else:
        receiver = request.user

    if not receiver:
        print("Не найден получатель для сообщения.")
        return

    ChatMessage.objects.create(
        repair_request=request,
        sender=sender,
        receiver=receiver,
        message=message
    )

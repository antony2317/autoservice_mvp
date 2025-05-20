import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from chat.models import ChatMessage
from repairs.models import RepairRequest, RepairResponse

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.request_id = self.scope['url_route']['kwargs']['request_id']
        self.response_id = self.scope['url_route']['kwargs']['response_id']
        self.room_group_name = f"chat_{self.request_id}_{self.response_id}"
        self.user = self.scope["user"]

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = self.user


        await save_message(self.request_id, self.response_id, message, sender)


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
def save_message(request_id, response_id, message, sender):
    try:
        request = RepairRequest.objects.get(id=request_id)
        response = RepairResponse.objects.get(id=response_id, repair_request=request)
    except (RepairRequest.DoesNotExist, RepairResponse.DoesNotExist):
        print(f"❌ Заявка или Отклик не найдены (request_id={request_id}, response_id={response_id})")
        return


    if sender == request.user:
        receiver = response.service
    else:
        receiver = request.user

    if not receiver:
        print("❌ Не найден получатель.")
        return

    try:
        ChatMessage.objects.create(
            repair_request=request,
            response=response,
            sender=sender,
            receiver=receiver,
            message=message
        )
        print(f"✅ Сообщение сохранено: {sender} -> {receiver}")
    except Exception as e:
        print(f"❌ Ошибка при сохранении сообщения: {e}")
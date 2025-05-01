from django.db import models
from django.conf import settings
from repairs.models import RepairRequest, RepairResponse

User = settings.AUTH_USER_MODEL

class ChatMessage(models.Model):

    repair_request = models.ForeignKey(RepairRequest, null=True, on_delete=models.CASCADE, related_name="chat_messages")

    response = models.ForeignKey(RepairResponse, null=True, blank=True, on_delete=models.CASCADE, related_name="chat_messages")

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')

    message = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender} -> {self.receiver} (Заявка #{self.repair_request.id}): {self.message[:30]}"

from django.db import models
from account.models import User

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('accepted', 'Принята'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
        ('canceled', 'Отменена'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_orders')
    service = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='service_orders')
    car_model = models.CharField(max_length=100)
    problem = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    proposed_date = models.DateTimeField(null=True, blank=True)

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Администратор'),
        ('manager', 'Менеджер'),
        ('customer', 'Клиент'),
        ('service', 'Автосервис'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_manager(self):
        return self.role == 'manager'

    @property
    def is_customer(self):
        return self.role == 'customer'

    @property
    def is_service(self):
        return self.role == 'service'

class AutoService(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name='Название автосервиса')
    address = models.TextField(verbose_name='Адрес')
    phone = models.CharField(max_length=20,  verbose_name='Номер для связи')
    description = models.TextField(blank=True, null=True, verbose_name="Описание сервиса")


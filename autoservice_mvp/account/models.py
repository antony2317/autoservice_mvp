from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_service = models.BooleanField(default=False, verbose_name="Автосервис")
    is_customer = models.BooleanField(default=True, verbose_name="Клиент")

    def __str__(self):
        return self.username

class AutoService(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name='Название автосервиса')
    address = models.TextField(verbose_name='Адрес')
    phone = models.CharField(max_length=20,  verbose_name='Номер для связи')

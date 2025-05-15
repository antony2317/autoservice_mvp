from django.db import models
from account.models import AutoService

from account.models import User
from datetime import time
from multiselectfield import MultiSelectField
from django.utils import timezone


class Service(models.Model):
    autoservice = models.ForeignKey(AutoService, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255, verbose_name='Название услуги')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена от')

    def __str__(self):
        return self.name


class Master(models.Model):
    autoservice = models.ForeignKey(AutoService, related_name="masters", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=200)
    experience = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


# class Booking(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     service = models.ForeignKey(Service, on_delete=models.CASCADE)
#     date = models.DateField(default=timezone.now)
#     time = models.TimeField(default=time(9, 0))

# (опционально) рабочие часы, если нужно, можно убрать и жестко задать в коде
# class WorkingHours(models.Model):
#     DAYS_OF_WEEK = [
#         ('Пн', 'Понедельник'),
#         ('Вт', 'Вторник'),
#         ('Ср', 'Среда'),
#         ('Чт', 'Четверг'),
#         ('Пт', 'Пятница'),
#         ('Сб', 'Суббота'),
#         ('Вс', 'Воскресенье'),
#     ]
#
#     autoservice = models.ForeignKey(AutoService, related_name='working_hours', on_delete=models.CASCADE)
#     days_of_week = MultiSelectField(choices=DAYS_OF_WEEK, default=['mon'],)
#     start_time = models.TimeField()
#     end_time = models.TimeField()
#
#     def __str__(self):
#         return f"{self.autoservice.name}: {self.days_of_week} {self.start_time}–{self.end_time}"

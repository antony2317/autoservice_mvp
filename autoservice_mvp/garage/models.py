import datetime

from django.contrib.auth import get_user_model
from django.db import models
from account.models import User, AutoService



class Garage(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название автосервиса")
    address = models.TextField(blank=True, verbose_name="Адрес")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    specialization = models.CharField(max_length=100, blank=True, verbose_name="Специализация")

    class Meta:
        verbose_name = "Автосервис"
        verbose_name_plural = "Автосервисы"
        ordering = ['name']

    def __str__(self):
        return self.name





def get_year_choices():
    current_year = datetime.datetime.now().year
    return [(year, year) for year in range(current_year, current_year - 30, -1)]



class CarBase(models.Model):
    brand = models.CharField(max_length=50, verbose_name='Марка')
    model = models.CharField(max_length=50, verbose_name='Модель')
    generation = models.CharField(max_length=50, verbose_name='Поколение', null=True, blank=True)  # новое поле
    year_from = models.PositiveIntegerField(verbose_name='Год начала выпуска')
    year_to = models.PositiveIntegerField(verbose_name='Год окончания выпуска', null=True, blank=True)
    engine_type = models.CharField(
        max_length=20,
        choices=[
            ('petrol', 'Бензин'),
            ('diesel', 'Дизель'),
            ('hybrid', 'Гибрид'),
            ('electric', 'Электро'),
        ],
        verbose_name='Тип двигателя',
        blank=True,  # позволяет оставлять поле пустым в форме
        null=True,  # позволяет хранить NULL в базе данных
    )
    engine_volume = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True,
                                        verbose_name='Объем двигателя (л)')

    def __str__(self):
        end = self.year_to if self.year_to is not None else 'н.в.'
        gen_part = f" {self.generation}" if self.generation else ""
        return f"{self.brand} {self.model}{gen_part} ({self.year_from}–{end})"

    class Meta:
        verbose_name = 'Авто из базы'
        verbose_name_plural = 'База автомобилей'
        unique_together = ('brand', 'model', 'generation', 'year_from', 'year_to', 'engine_type', 'engine_volume')


ENGINE_TYPE_CHOICES = [
    ('petrol', 'Бензин'),
    ('diesel', 'Дизель'),
    ('hybrid', 'Гибрид'),
    ('electric', 'Электро'),
]

class Car(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')
    base_car = models.ForeignKey(CarBase, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Автомобиль из базы')
    year = models.PositiveIntegerField(verbose_name='Год выпуска', null=True, blank=True)
    engine_type = models.CharField(max_length=20, choices=ENGINE_TYPE_CHOICES, null=True, blank=True)
    engine_volume = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    vin = models.CharField(max_length=17, unique=True, blank=True, null=True, verbose_name='VIN-номер')
    mileage = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name='Пробег (км)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return f"{self.base_car.brand} {self.base_car.model} ({self.year or 'год не указан'})"

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'



class ServiceRecord(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    autoservice = models.ForeignKey(AutoService, on_delete=models.SET_NULL, null=True, blank=True)  # заменили garage
    date = models.DateField()
    mileage = models.PositiveIntegerField()
    service_type = models.CharField(max_length=100, verbose_name='Вид работ')
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Цена')
    receipt = models.FileField(upload_to='service_receipts/', blank=True, verbose_name='фото чека(не обязательно)')
    created_by = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL,
        null=True, blank=True, editable=False, verbose_name='Создатель записи'
    )

    def __str__(self):
        return f"{self.service_type} ({self.date})"


class ServiceRequest(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    description = models.TextField()
    desired_date = models.DateTimeField()
    STATUS_CHOICES = [
        ('pending', 'Ожидает предложений'),
        ('accepted', 'Принята'),
        ('completed', 'Завершена'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')




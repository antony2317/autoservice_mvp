from django.db import models
from django.conf import settings
from garage.models import Car
from django.core.exceptions import ValidationError
from django.utils import timezone


class RepairRequest(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        verbose_name='Автомобиль'
    )
    description = models.TextField('Описание проблемы')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Заявка на ремонт'
        verbose_name_plural = 'Заявки на ремонт'

    def __str__(self):
        return f"Заявка #{self.id} ({self.get_status_display()})"

    @property
    def has_accepted_response(self):
        """Проверяет, есть ли принятое предложение по этой заявке"""
        return self.responses.filter(is_accepted=True).exists()


class RepairResponse(models.Model):
    repair_request = models.ForeignKey(
        RepairRequest,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Заявка'
    )
    service = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'is_service': True},
        verbose_name='Автосервис'
    )
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    proposed_date = models.DateField(verbose_name='Предложенная дата ремонта')
    is_accepted = models.BooleanField(default=False, verbose_name='Подтверждено пользователем')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ответ на заявку'
        verbose_name_plural = 'Ответы на заявки'

    def __str__(self):
        return f"Ответ от {self.service.username} на заявку #{self.repair_request.id}"

    def clean(self):
        # Проверка, что дата не в прошлом
        if self.proposed_date and self.proposed_date < timezone.now().date():
            raise ValidationError("Дата ремонта не может быть в прошлом")

        # Проверка положительной цены
        if self.proposed_price <= 0:
            raise ValidationError("Цена должна быть положительной")

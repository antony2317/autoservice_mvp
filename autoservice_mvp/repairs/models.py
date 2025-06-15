from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

class RepairRequest(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
        ('canceled', 'Отменена'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='repair_requests',
        verbose_name='Пользователь'
    )
    car = models.ForeignKey(
        'garage.Car',  # Используем строковую ссылку с указанием приложения
        on_delete=models.CASCADE,
        related_name='repair_requests',
        verbose_name='Автомобиль'
    )
    description = models.TextField('Описание проблемы')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    executor = models.ForeignKey(
        'account.AutoService',  # Используем строковую ссылку с указанием приложения
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_requests',
        verbose_name='Исполнитель'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Заявка на ремонт'
        verbose_name_plural = 'Заявки на ремонт'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Заявка #{self.id} ({self.get_status_display()})"

    @property
    def has_accepted_response(self):
        """Проверяет, есть ли принятый отклик на заявку"""
        return self.responses.filter(is_accepted=True).exists()

    def get_new_responses_count(self):
        """Возвращает количество новых (непросмотренных) откликов"""
        return self.responses.filter(is_new=True).count()

    def mark_responses_as_viewed(self):
        """Помечает все отклики на эту заявку как просмотренные"""
        updated = self.responses.filter(is_new=True).update(is_new=False)
        return updated > 0

    def get_accepted_response(self):
        """Возвращает принятый отклик (если есть)"""
        return self.responses.filter(is_accepted=True).first()

    def get_active_responses(self):
        """Возвращает активные (не отклоненные) отклики"""
        return self.responses.filter(is_rejected=False)

    def can_accept_responses(self):
        """Проверяет, можно ли принимать новые отклики"""
        return self.status == 'new' and not self.has_accepted_response

    def clean(self):
        """Валидация модели"""
        super().clean()

        if self.executor and not hasattr(self.executor, 'autoservice'):
            raise ValidationError("Исполнителем может быть только автосервис")

        if self.status == 'completed' and not self.has_accepted_response:
            raise ValidationError("Нельзя завершить заявку без принятого отклика")

    def save(self, *args, **kwargs):
        """Переопределение метода save для автоматической валидации"""
        self.full_clean()
        super().save(*args, **kwargs)


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
        limit_choices_to={'role': 'service'},
        related_name='service_responses',
        verbose_name='Автосервис'
    )
    proposed_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Предложенная цена',
        validators=[MinValueValidator(0.01)]
    )
    proposed_date = models.DateField(verbose_name='Предложенная дата ремонта')
    comment = models.TextField('Комментарий сервиса', blank=True)
    is_accepted = models.BooleanField(default=False, verbose_name='Принято')
    is_rejected = models.BooleanField(default=False, verbose_name='Отклонено')
    is_new = models.BooleanField(default=True, verbose_name='Новый отклик')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Ответ на заявку'
        verbose_name_plural = 'Ответы на заявки'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['repair_request', 'service'],
                name='unique_response_per_service'
            ),
            models.CheckConstraint(
                check=~models.Q(is_accepted=True, is_rejected=True),
                name='response_cannot_be_accepted_and_rejected'
            )
        ]

    def __str__(self):
        return f"Ответ от {self.service.username} на заявку #{self.repair_request.id}"

    def clean(self):
        """Валидация модели"""
        super().clean()

        if self.proposed_date and self.proposed_date < timezone.now().date():
            raise ValidationError("Дата ремонта не может быть в прошлом")

        if self.service.role != 'service':
            raise ValidationError("Откликать могут только автосервисы")

        if self.is_accepted and self.repair_request.has_accepted_response:
            raise ValidationError("У заявки уже есть принятый отклик")

    def save(self, *args, **kwargs):
        """Переопределение метода save"""
        self.full_clean()
        super().save(*args, **kwargs)

        if self.is_accepted:
            # Обновляем исполнителя заявки при принятии отклика
            self.repair_request.executor = self.service.autoservice
            self.repair_request.status = 'in_progress'
            self.repair_request.save()
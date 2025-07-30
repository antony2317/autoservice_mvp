from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class RepairCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Категория ремонта')

    class Meta:
        verbose_name = 'Категория ремонта'
        verbose_name_plural = 'Категории ремонта'
        ordering = ['name']

    def __str__(self):
        return self.name


class RepairType(models.Model):
    category = models.ForeignKey(
        RepairCategory,
        on_delete=models.CASCADE,
        related_name='repair_types',
        verbose_name='Категория'
    )
    name = models.CharField(max_length=100, verbose_name='Тип ремонта')

    class Meta:
        verbose_name = 'Тип ремонта'
        verbose_name_plural = 'Типы ремонта'
        unique_together = ('category', 'name')
        ordering = ['category__name', 'name']

    def __str__(self):
        return f"{self.category.name} — {self.name}"


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
        'garage.Car',
        on_delete=models.CASCADE,
        related_name='repair_requests',
        verbose_name='Автомобиль'
    )
    # Временный null=True
    category = models.ForeignKey(
        RepairCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Категория ремонта'
    )
    repair_type = models.ForeignKey(
        RepairType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Тип ремонта'
    )
    description = models.TextField('Дополнительное описание', blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    executor = models.ForeignKey(
        'account.AutoService',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_requests',
        verbose_name='Исполнитель'
    )
    problem_not_listed = models.BooleanField(default=False, verbose_name='Проблема не указана в списке')
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
        return self.responses.filter(is_accepted=True).exists()

    def get_new_responses_count(self):
        return self.responses.filter(is_new=True).count()

    def mark_responses_as_viewed(self):
        updated = self.responses.filter(is_new=True).update(is_new=False)
        return updated > 0

    def get_accepted_response(self):
        return self.responses.filter(is_accepted=True).first()

    def get_active_responses(self):
        return self.responses.filter(is_rejected=False)

    def can_accept_responses(self):
        return self.status == 'new' and not self.has_accepted_response

    def clean(self):
        super().clean()

        if self.category and self.repair_type:
            if self.repair_type.category_id != self.category_id:
                raise ValidationError("Выбранный тип ремонта не относится к указанной категории.")

        if self.executor and not hasattr(self.executor, 'autoservice'):
            raise ValidationError("Исполнителем может быть только автосервис")

        if self.status == 'completed' and not self.has_accepted_response:
            raise ValidationError("Нельзя завершить заявку без принятого отклика")

    def save(self, *args, **kwargs):
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
        validators=[MinValueValidator(0.01)],
        verbose_name='Предложенная цена'
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
        super().clean()

        if self.proposed_date and self.proposed_date < timezone.now().date():
            raise ValidationError("Дата ремонта не может быть в прошлом")

        if self.service.role != 'service':
            raise ValidationError("Откликать могут только автосервисы")

        if self.is_accepted and self.repair_request.has_accepted_response:
            raise ValidationError("У заявки уже есть принятый отклик")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        if self.is_accepted:
            self.repair_request.executor = self.service.autoservice
            self.repair_request.status = 'in_progress'
            self.repair_request.save()

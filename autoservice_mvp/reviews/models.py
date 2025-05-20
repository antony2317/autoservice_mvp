# reviews/models.py
from django.db import models
from django.conf import settings

class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_left',
        verbose_name='Пользователь'
    )
    service = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_received',
        verbose_name='Сервис',
        limit_choices_to={'is_service': True}
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name='Оценка'
    )
    text = models.TextField('Текст отзыва', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('user', 'service')

    def __str__(self):
        return f"Отзыв от {self.user} для {self.service}"

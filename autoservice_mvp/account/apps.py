# account/apps.py
from django.apps import AppConfig

class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'  # Должно совпадать с именем папки приложения
    verbose_name = 'Учетные записи'
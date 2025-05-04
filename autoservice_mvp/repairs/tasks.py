

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def notify_user_about_response(user_email, service_name, price, date):
    subject = "🔧 Новый отклик на вашу заявку"
    message = f"""
Здравствуйте!

Автосервис "{service_name}" откликнулся на вашу заявку на ремонт.

💰 Цена: {price}₽
📅 Дата ремонта: {date}

Зайдите в личный кабинет, чтобы просмотреть все предложения.

Спасибо, что используете наш сервис!
    """

    try:
        print(f"[TASK] Отправка письма на {user_email} от {settings.DEFAULT_FROM_EMAIL}")
        result = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False
        )

        if result == 1:
            print("[TASK] ✅ Письмо успешно отправлено.")
        else:
            print("[TASK] ❌ Письмо не было отправлено.")

    except Exception as e:
        print(f"[TASK] ❗ Ошибка при отправке письма: {e}")

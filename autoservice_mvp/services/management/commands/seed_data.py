from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from orders.models import Order
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными для дашборда автосервиса'

    def handle(self, *args, **options):
        service, created = User.objects.get_or_create(
            username='autoservice',
            defaults={
                'password': 'test123',
                'first_name': 'Автосервис "Руль"',
                'is_service': True
            }
        )
        if created:
            service.set_password('test123')
            service.save()

        client, created = User.objects.get_or_create(
            username='client1',
            defaults={
                'password': 'client123',
                'first_name': 'Иван'
            }
        )
        if created:
            client.set_password('client123')
            client.save()

        statuses = ['new', 'accepted', 'in_progress', 'completed']
        for i in range(1, 15):
            Order.objects.get_or_create(
                client=client,
                service=service,
                car_model=f'BMW X{i % 5}',
                problem=f'Проблема с двигателем #{i}',
                status=statuses[i % 4],
                created_at=datetime.now() - timedelta(days=i),
                proposed_price=1000 * i
            )

        self.stdout.write(self.style.SUCCESS('✅ Тестовые данные успешно созданы!'))
# Generated by Django 4.2.21 on 2025-05-18 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_remove_user_is_customer_remove_user_is_service_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='autoservice',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание сервиса'),
        ),
    ]

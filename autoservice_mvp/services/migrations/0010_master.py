# Generated by Django 4.2.19 on 2025-05-15 20:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_user_is_customer_alter_user_is_service'),
        ('services', '0009_remove_workinghours_autoservice_delete_booking_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Master',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('specialization', models.CharField(max_length=200)),
                ('experience', models.PositiveIntegerField(default=0)),
                ('autoservice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='masters', to='account.autoservice')),
            ],
        ),
    ]

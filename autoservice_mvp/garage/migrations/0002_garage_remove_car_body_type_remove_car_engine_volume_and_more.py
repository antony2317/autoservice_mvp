# Generated by Django 4.2.19 on 2025-04-12 20:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('garage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Garage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('address', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='car',
            name='body_type',
        ),
        migrations.RemoveField(
            model_name='car',
            name='engine_volume',
        ),
        migrations.AddField(
            model_name='car',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default='2024-01-01 00:00'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='car',
            name='mileage',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='car',
            name='vin',
            field=models.CharField(blank=True, max_length=17, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='car',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cars', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='car',
            name='year',
            field=models.PositiveIntegerField(),
        ),
        migrations.CreateModel(
            name='ServiceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('mileage', models.PositiveIntegerField()),
                ('service_type', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('receipt', models.FileField(blank=True, upload_to='service_receipts/')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_history', to='garage.car')),
                ('garage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='garage.garage')),
            ],
        ),
    ]

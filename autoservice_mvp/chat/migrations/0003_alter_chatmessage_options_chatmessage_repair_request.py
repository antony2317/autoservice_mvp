# Generated by Django 4.2.19 on 2025-04-22 19:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('repairs', '0003_alter_repairresponse_options_and_more'),
        ('chat', '0002_remove_chatmessage_is_read'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chatmessage',
            options={},
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='repair_request',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages', to='repairs.repairrequest'),
        ),
    ]

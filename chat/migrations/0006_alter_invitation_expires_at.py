# Generated by Django 5.1.1 on 2024-09-17 05:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_alter_invitation_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitation',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 19, 5, 7, 39, 984983, tzinfo=datetime.timezone.utc)),
        ),
    ]

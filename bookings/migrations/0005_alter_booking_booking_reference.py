# Generated by Django 5.1.5 on 2025-03-01 04:18

import bookings.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0004_alter_booking_booking_reference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='booking_reference',
            field=models.CharField(default=bookings.models.generate_booking_reference, max_length=8),
        ),
    ]

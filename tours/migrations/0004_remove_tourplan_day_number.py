# Generated by Django 5.1.5 on 2025-03-01 00:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0003_tourplan_accommodation_tourplan_inclusion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tourplan',
            name='day_number',
        ),
    ]

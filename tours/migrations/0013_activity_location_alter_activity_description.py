# Generated by Django 5.1.5 on 2025-03-25 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0012_alter_activity_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='location',
            field=models.TextField(blank=True, default='kigali', null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]

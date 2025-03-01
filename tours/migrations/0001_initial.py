# Generated by Django 5.1.5 on 2025-02-24 23:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TourPackage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('location', models.CharField(max_length=100)),
                ('best_time_to_visit', models.CharField(max_length=50)),
                ('duration_days', models.PositiveIntegerField()),
                ('duration_nights', models.PositiveIntegerField()),
                ('min_people', models.PositiveIntegerField(default=1)),
                ('max_people', models.PositiveIntegerField(default=20)),
                ('rating', models.FloatField(default=0.0)),
                ('main_image', models.ImageField(blank=True, null=True, upload_to='tours/main_images/')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tours', to='tours.country')),
            ],
        ),
        migrations.CreateModel(
            name='TourImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='tours/gallery/')),
                ('tour_package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gallery', to='tours.tourpackage')),
            ],
        ),
        migrations.CreateModel(
            name='InclusionExclusion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('INCLUSION', 'Inclusion'), ('EXCLUSION', 'Exclusion')], max_length=10)),
                ('detail', models.CharField(max_length=255)),
                ('tour_package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inclusions_exclusions', to='tours.tourpackage')),
            ],
        ),
        migrations.CreateModel(
            name='Accommodation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('tour_package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accommodations', to='tours.tourpackage')),
            ],
        ),
        migrations.CreateModel(
            name='TourPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_number', models.PositiveIntegerField()),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('tour_package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tour_plans', to='tours.tourpackage')),
            ],
        ),
    ]

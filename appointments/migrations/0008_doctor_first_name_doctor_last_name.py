# Generated by Django 5.1.5 on 2025-02-17 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0007_appointment_availability'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='first_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='doctor',
            name='last_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]

# Generated by Django 5.2.1 on 2025-06-13 23:55

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='contact_number',
            field=models.CharField(blank=True, help_text='Enter 10-digit mobile number.', max_length=15, validators=[django.core.validators.RegexValidator(message='Phone number must be in the format: +91 followed by 10 digits.', regex='^\\+91\\d{10}$')]),
        ),
    ]

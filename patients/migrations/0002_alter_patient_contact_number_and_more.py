# Generated by Django 5.2.1 on 2025-06-12 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='contact_number',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AlterField(
            model_name='patient',
            name='ongoing_conditions',
            field=models.TextField(blank=True, null=True, verbose_name='Ongoing conditions'),
        ),
    ]

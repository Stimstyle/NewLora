# Generated by Django 5.1.3 on 2024-12-05 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('access_control', '0005_districtgroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='districtgroup',
            name='district_name',
            field=models.CharField(max_length=255, verbose_name='Название района, ТСЖ, УК...'),
        ),
    ]

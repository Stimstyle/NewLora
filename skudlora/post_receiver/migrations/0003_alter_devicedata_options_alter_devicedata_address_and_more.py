# Generated by Django 4.0 on 2024-11-20 01:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('post_receiver', '0002_devicedata_address_devicedata_description_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='devicedata',
            options={'verbose_name': 'Добавить устройство', 'verbose_name_plural': 'Добавить устройства'},
        ),
        migrations.AlterField(
            model_name='devicedata',
            name='address',
            field=models.TextField(verbose_name='Адрес установки'),
        ),
        migrations.AlterField(
            model_name='devicedata',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='devicedata',
            name='dev_eui',
            field=models.CharField(max_length=255, verbose_name='DevEUI'),
        ),
        migrations.AlterField(
            model_name='devicedata',
            name='device_class',
            field=models.CharField(choices=[('NbIot', 'NbIot'), ('LoRaWAN', 'LoRaWAN')], default='LoRaWAN', max_length=10, verbose_name='Тип устройства'),
        ),
        migrations.AlterField(
            model_name='devicedata',
            name='device_name',
            field=models.CharField(max_length=255, verbose_name='Пароль'),
        ),
        migrations.AlterField(
            model_name='devicedata',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

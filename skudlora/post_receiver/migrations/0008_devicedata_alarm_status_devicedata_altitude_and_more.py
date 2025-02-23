# Generated by Django 5.1.3 on 2024-11-25 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post_receiver', '0007_alter_apikey_api_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicedata',
            name='alarm_status',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Статус тревоги'),
        ),
        migrations.AddField(
            model_name='devicedata',
            name='altitude',
            field=models.FloatField(blank=True, null=True, verbose_name='Высота'),
        ),
        migrations.AddField(
            model_name='devicedata',
            name='battery_level',
            field=models.FloatField(blank=True, null=True, verbose_name='Уровень заряда'),
        ),
        migrations.AddField(
            model_name='devicedata',
            name='latitude',
            field=models.FloatField(blank=True, null=True, verbose_name='Широта'),
        ),
        migrations.AddField(
            model_name='devicedata',
            name='lock_status',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Статус замка'),
        ),
        migrations.AddField(
            model_name='devicedata',
            name='longitude',
            field=models.FloatField(blank=True, null=True, verbose_name='Долгота'),
        ),
        migrations.AddField(
            model_name='devicedata',
            name='night_mode',
            field=models.BooleanField(default=False, verbose_name='Ночной режим'),
        ),
        migrations.AddField(
            model_name='devicedata',
            name='temperature',
            field=models.FloatField(blank=True, null=True, verbose_name='Температура'),
        ),
    ]

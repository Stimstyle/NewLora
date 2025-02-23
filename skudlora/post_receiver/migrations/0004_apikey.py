# Generated by Django 5.1.3 on 2024-11-21 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post_receiver', '0003_alter_devicedata_options_alter_devicedata_address_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider_name', models.CharField(choices=[('ER-NET', 'ER-NET'), ('MEGAFON', 'MEGAFON')], max_length=255, verbose_name='Поставщик услуг')),
                ('api_key', models.CharField(max_length=255, verbose_name='API ключ')),
            ],
            options={
                'verbose_name': 'API ключ',
                'verbose_name_plural': 'API ключи',
            },
        ),
    ]

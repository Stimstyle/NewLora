# Generated by Django 5.1.3 on 2024-11-21 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post_receiver', '0006_devicedata_api_key_alter_apikey_key_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apikey',
            name='api_key',
            field=models.CharField(max_length=255, unique=True, verbose_name='API ключ'),
        ),
    ]

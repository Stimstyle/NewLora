# Generated by Django 5.1.3 on 2024-11-26 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserDash', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='dev_eui',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

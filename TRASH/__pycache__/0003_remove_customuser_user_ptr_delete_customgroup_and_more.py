# Generated by Django 5.1.3 on 2024-11-20 07:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('access_control', '0002_customgroup_customuser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='user_ptr',
        ),
        migrations.DeleteModel(
            name='CustomGroup',
        ),
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]

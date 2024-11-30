from django.contrib.auth.models import User
from django.db import models
from post_receiver.models import DeviceData

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
        ('info', 'Info'),
        ('system', 'System'),
    ]

    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)  # Время фиксируется автоматически
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    dev_eui = models.CharField(max_length=255, null=True, blank=True)  # Добавили поле DevEUI
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    is_read = models.BooleanField(default=False)  # Флаг прочтения уведомления

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.message} ({self.timestamp})"

from django.db import models
from django.contrib.auth.models import User

class EventNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('warning', 'Предупреждение'),
        ('success', 'Успех'),
        ('error', 'Ошибка'),
        ('info', 'Информация'),
        ('system', 'Системное'),
    ]

    dev_eui = models.CharField(max_length=255, null=True, blank=True, verbose_name="DevEUI")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info', verbose_name="Тип уведомления")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время")

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.dev_eui} - {self.address} ({self.timestamp})"


class DeviceGroup(models.Model):
    group_name = models.CharField(max_length=255, verbose_name="Название группы")
    address = models.TextField(verbose_name="Адрес группы", null=False)
    latitude = models.FloatField(null=True, blank=True, verbose_name="Широта группы")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Долгота группы")
    devices = models.ManyToManyField(DeviceData, related_name="device_groups", verbose_name="Устройства")

    def __str__(self):
        return self.group_name
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    devices = models.ManyToManyField(DeviceData, blank=True, related_name='users_individual')
    device_groups = models.ManyToManyField(DeviceGroup, blank=True, related_name='users_groups')

    def __str__(self):
        return f"Профиль пользователя: {self.user.username}"
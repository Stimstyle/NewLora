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

class DeviceGroup(models.Model):
    group_name = models.CharField(max_length=255, verbose_name="Название группы")
    address = models.TextField(verbose_name="Адрес группы", null=False)
    latitude = models.FloatField(null=True, blank=True, verbose_name="Широта группы")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Долгота группы")
    devices = models.ManyToManyField(DeviceData, related_name="device_groups", verbose_name="Устройства")

    def __str__(self):
        return self.group_name

# access_control/models.py

from django.db import models
from django.contrib.auth.models import User
from post_receiver.models import DeviceData  # Импортируем модель DeviceData
from UserDash.models import DeviceGroup

# Модель устройства
class Device(models.Model):
    dev_eui = models.CharField(max_length=16, unique=True)  # DevEUI
    device_name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.device_name

# Промежуточная модель для разрешений пользователей на устройства
class DevicePermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Внешний ключ на User
    device = models.ForeignKey(DeviceData, on_delete=models.CASCADE)  # Внешний ключ на Device
    can_manage = models.BooleanField(default=False)  # Пользователь может управлять устройством или только смотреть

    def __str__(self):
        return f"{self.user.username} - {self.device.device_name} (Manage: {self.can_manage})"

class DeviceGroupPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_group = models.ForeignKey(DeviceGroup, on_delete=models.CASCADE)
    can_manage = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'device_group')
        verbose_name = 'Разрешение на группу устройств'
        verbose_name_plural = 'Разрешения на группы устройств'

    def __str__(self):
        return f"{self.user.username} - {self.device_group.group_name}"        

# Модель команд для устройства
class Command(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    command_json = models.JSONField()  # Структура JSON команды
    is_sent = models.BooleanField(default=False)  # Статус отправки команды

    def __str__(self):
        return f"Command for {self.device.device_name} - Sent: {self.is_sent}"

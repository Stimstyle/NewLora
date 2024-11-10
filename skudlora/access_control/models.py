from django.db import models
from django.contrib.auth.models import User

# Модель устройства
class Device(models.Model):
    dev_eui = models.CharField(max_length=16, unique=True)  # DevEUI
    device_name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    # Связь с пользователем через разрешения (будет установлена через промежуточную модель)
    users = models.ManyToManyField(User, through='DevicePermission')

    def __str__(self):
        return self.device_name

# Промежуточная модель для разрешений пользователей на устройства
class DevicePermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    can_manage = models.BooleanField(default=False)  # Пользователь может управлять устройством или только смотреть

    def __str__(self):
        return f"{self.user.username} - {self.device.device_name} (Manage: {self.can_manage})"

# Модель команд для устройства
class Command(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    command_json = models.JSONField()  # Структура JSON команды
    is_sent = models.BooleanField(default=False)  # Статус отправки команды

    def __str__(self):
        return f"Command for {self.device.device_name} - Sent: {self.is_sent}"

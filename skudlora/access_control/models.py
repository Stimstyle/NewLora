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


class DistrictGroup(models.Model):
    district_name = models.CharField(max_length=255, verbose_name="Название района (ТСЖ, УК, ТСН, ЖСК)")
    groups = models.ManyToManyField(DeviceGroup, related_name="districts", verbose_name="Группы домов")

    def __str__(self):
        return self.district_name
    

class DistrictGroupPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="district_permissions", verbose_name="Пользователь")
    district_group = models.ForeignKey(DistrictGroup, on_delete=models.CASCADE, related_name="user_permissions", verbose_name="Район")
    can_manage = models.BooleanField(default=False, verbose_name="Может управлять")

    def __str__(self):
        return f"{self.user.username} - {self.district_group.district_name}"

class UserGroup(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название группы")
    users = models.ManyToManyField(User, related_name="custom_user_groups", verbose_name="Пользователи")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    def __str__(self):
        return self.name    

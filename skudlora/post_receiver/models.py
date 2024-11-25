# device_data/models.py
from django.db import models
from django.utils import timezone

class DeviceData(models.Model):
    DEVICE_CLASSES = [
        ('NbIot', 'NbIot'),
        ('LoRaWAN', 'LoRaWAN'),
    ]
    dev_eui = models.CharField(max_length=255, verbose_name="DevEUI")
    device_name = models.CharField(max_length=255, verbose_name="Пароль")
    address = models.TextField(verbose_name="Адрес установки", null=False)
    device_class = models.CharField(max_length=10, choices=DEVICE_CLASSES, default='LoRaWAN', verbose_name="Тип устройства")  # Указываем default
    description = models.TextField(null=True, blank=True, verbose_name="Описание")
    data = models.TextField()
    time = models.DateTimeField(default=timezone.now)  # Устанавливаем значение по умолчанию
    rssi = models.IntegerField(null=True)
    lo_ra_snr = models.IntegerField(null=True)

    latitude = models.FloatField(null=True, blank=True, verbose_name="Широта")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Долгота")
    altitude = models.FloatField(null=True, blank=True, verbose_name="Высота")
    temperature = models.FloatField(null=True, blank=True, verbose_name="Температура")
    battery_level = models.FloatField(null=True, blank=True, verbose_name="Уровень заряда")
    lock_status = models.CharField(max_length=50, null=True, blank=True, verbose_name="Статус замка")
    alarm_status = models.CharField(max_length=50, null=True, blank=True, verbose_name="Статус тревоги")
    night_mode = models.BooleanField(default=False, verbose_name="Ночной режим")
    # Связь с таблицей APIKey
    api_key = models.ForeignKey('APIKey', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="API Ключ")
    



    def __str__(self):
        return f"Device: {self.device_name}, DevEUI: {self.dev_eui}, Time: {self.time}"
    class Meta:
        verbose_name = "Добавить устройство"  # Название модели в единственном числе
        verbose_name_plural = "Добавить устройства"  # Название модели во множественном числе
        
# Модель для хранения API-ключей с выбором поставщика услуг
class APIKey(models.Model):
    PROVIDERS = [
        ('ER-NET', 'ER-NET'),
        ('MEGAFON', 'MEGAFON'),
    ]
    provider_name = models.CharField(max_length=255, choices=PROVIDERS, verbose_name="Поставщик услуг")
    api_key = models.CharField(max_length=255, verbose_name="API ключ", unique=True)
    key_name = models.CharField(max_length=255, verbose_name="Название ключа", default="Введите название, указанное на сайте поставщика услуг")  # Добавлено поле для названия ключа
    
    def __str__(self):
        return f"{self.provider_name} - {self.key_name}"

    class Meta:
        verbose_name = "API ключ"
        verbose_name_plural = "API ключи"

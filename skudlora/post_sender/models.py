# models.py в проекте post_sender
from django.db import models

class DeviceData(models.Model):
    device_name = models.CharField(max_length=255)
    dev_eui = models.CharField(max_length=255)
    data = models.TextField()
    time = models.DateTimeField()
    rssi = models.IntegerField(null=True)
    lo_ra_snr = models.IntegerField(null=True)
    address = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    device_class = models.CharField(max_length=10)

    class Meta:
        db_table = 'device_data'  # Убедитесь, что это совпадает с таблицей в другой базе данных

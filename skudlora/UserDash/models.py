from django.contrib.auth.models import User
from django.db import models

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

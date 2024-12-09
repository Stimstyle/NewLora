# UserDash/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from UserDash.models import Notification, EventNotification



@receiver(post_save, sender=Notification)
def create_event_notification(sender, instance, created, **kwargs):
    if created:
        # Создаем соответствующее уведомление в EventNotification
        EventNotification.objects.create(
            dev_eui=instance.dev_eui,
            address=instance.address,
            user=instance.user,
            notification_type=instance.notification_type,
            timestamp=instance.timestamp,
            message=instance.message  # Копируем сообщение
        )

from django.core.management.base import BaseCommand
from UserDash.models import Notification, EventNotification

class Command(BaseCommand):
    help = 'Copies existing data from Notification to EventNotification'

    def handle(self, *args, **options):
        notifications = Notification.objects.all()
        copied = 0
        for notif in notifications:
            # Проверяем, что запись еще не скопирована
            exists = EventNotification.objects.filter(
                dev_eui=notif.dev_eui,
                address=notif.address,
                user=notif.user,
                notification_type=notif.notification_type,
                timestamp=notif.timestamp
            ).exists()
            if not exists:
                EventNotification.objects.create(
                    dev_eui=notif.dev_eui,
                    address=notif.address,
                    user=notif.user,
                    notification_type=notif.notification_type,
                    timestamp=notif.timestamp
                )
                copied += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully copied {copied} notifications to EventNotification.'))

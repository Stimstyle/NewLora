from django.core.management.base import BaseCommand
from UserDash.models import Notification, EventNotification
from django.db.models import Q

class Command(BaseCommand):
    help = 'Copies existing data from Notification to EventNotification, including message'

    def handle(self, *args, **options):
        notifications = Notification.objects.all()
        created_count = 0
        updated_count = 0

        for notif in notifications:
            # Ищем EventNotification с теми же полями, кроме message
            evn = EventNotification.objects.filter(
                dev_eui=notif.dev_eui,
                address=notif.address,
                user=notif.user,
                notification_type=notif.notification_type,
                timestamp=notif.timestamp
            ).first()

            if evn is None:
                # Создаем новую запись EventNotification, если такой еще нет
                EventNotification.objects.create(
                    dev_eui=notif.dev_eui,
                    address=notif.address,
                    user=notif.user,
                    notification_type=notif.notification_type,
                    timestamp=notif.timestamp,
                    message=notif.message  # Копируем сообщение
                )
                created_count += 1
            else:
                # Если запись есть, но message пустое или None, то обновим
                if not evn.message:
                    evn.message = notif.message
                    evn.save()
                    updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {created_count} new EventNotifications and updated message in {updated_count} existing ones.'
        ))
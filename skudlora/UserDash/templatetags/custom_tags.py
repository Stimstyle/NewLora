from django import template
from UserDash.models import Notification
from datetime import timedelta
from django.utils import timezone

register = template.Library()

@register.simple_tag
def unread_notifications_count(user):
    return Notification.objects.filter(is_read=False, user=user).count()

@register.simple_tag
def warning_notifications_count(user):
    return Notification.objects.filter(is_read=False, user=user, notification_type='warning').count()

@register.simple_tag
def get_unread_notifications(user, notification_type=None, limit=30):
    """
    Получаем последние непрочитанные уведомления для пользователя с фильтрацией по типу.
    Ограничиваем результат последними `limit` уведомлениями.
    """
    notifications = Notification.objects.filter(user=user, is_read=False)

    # Фильтруем по типу, если он указан
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)

    # Ограничиваем 30 последними уведомлениями
    notifications = notifications.order_by('-timestamp')[:limit]

    return notifications


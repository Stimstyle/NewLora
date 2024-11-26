from django import template
from UserDash.models import Notification

register = template.Library()

@register.simple_tag
def unread_notifications_count(user):
    return Notification.objects.filter(is_read=False, user=user).count()

@register.simple_tag
def warning_notifications_count(user):
    return Notification.objects.filter(is_read=False, user=user, notification_type='warning').count()
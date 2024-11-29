# UserDash/admin.py

from django.contrib import admin
from .models import UserProfile, DeviceGroup, Notification

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('devices', 'device_groups')  # Для удобного выбора в админке


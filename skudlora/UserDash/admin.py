# UserDash/admin.py

from django.contrib import admin
from .models import DeviceGroup, DeviceData
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('devices', 'device_groups')  # Для удобного выбора в админке


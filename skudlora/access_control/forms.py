# access_control/forms.py

from django import forms
from .models import Device, DevicePermission
from django.contrib.auth.models import User

# Форма для создания устройства
class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['dev_eui', 'device_name', 'description', 'location']

# Форма для разрешений устройства
class DevicePermissionForm(forms.ModelForm):
    class Meta:
        model = DevicePermission
        fields = ['user', 'device', 'can_manage']

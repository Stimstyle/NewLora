# access_control/forms.py

from django import forms
from access_control.models import Device, DevicePermission
from django.contrib.auth.models import User
from post_receiver.models import DeviceData

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

class DevicePermissionForm(forms.Form):
    devices = forms.ModelMultipleChoiceField(
        queryset=DeviceData.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    can_manage = forms.BooleanField(
        required=False,
        label='Пользователь может управлять устройствами'
    )
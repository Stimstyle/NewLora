# access_control/views.py

from django.shortcuts import render, redirect
from .forms import DeviceForm, DevicePermissionForm
from django.contrib.auth.decorators import login_required
from .models import Device

# Представление для создания устройства
@login_required
def create_device(request):
    if request.method == 'POST':
        device_form = DeviceForm(request.POST)
        permission_form = DevicePermissionForm(request.POST)
        if device_form.is_valid() and permission_form.is_valid():
            # Сохраняем устройство
            device = device_form.save()
            # Сохраняем разрешение
            permission = permission_form.save(commit=False)
            permission.device = device  # Привязываем разрешение к устройству
            permission.save()
            return redirect('device_list')  # Перенаправляем на список устройств
    else:
        device_form = DeviceForm()
        permission_form = DevicePermissionForm()

    return render(request, 'create_device.html', {
        'device_form': device_form,
        'permission_form': permission_form
    })
    
@login_required
def device_list(request):
    devices = Device.objects.all()
    return render(request, 'device_list.html', {'devices': devices})

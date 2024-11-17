# access_control/views.py

from django.shortcuts import render, redirect
from .forms import DeviceForm, DevicePermissionForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .models import Device
from django.contrib import messages


def home(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)  # Вход пользователя
            if user.is_staff:  # Проверяем, является ли пользователь администратором
                return redirect('/admin/')
            else:
                return redirect('user_dashboard')  # Перенаправляем на пользовательскую страницу
        else:
            messages.error(request, 'Неверный логин или пароль.')  # Выводим сообщение об ошибке

    return render(request, 'home.html')


@login_required
def user_dashboard(request):
    return render(request, 'user_dashboard.html')



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

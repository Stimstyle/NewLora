# access_control/urls.py

from django.urls import path
from . import views  # Импортируем представления
from .models import DevicePermission

urlpatterns = [
    path('', views.home, name='home'),
    path('create_device/', views.create_device, name='create_device'),  # Страница для создания устройства
    path('device_list/', views.device_list, name='device_list'),        # Страница для отображения списка устройств
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('device_permissions/', views.device_permissions, name='device_permissions'),
    path('edit_device_permissions/', views.edit_device_permissions, name='edit_device_permissions'),
    path('device-group-permissions/', views.edit_device_group_permissions, name='edit_device_group_permissions'),
    path('edit-devices-in-group/', views.edit_devices_in_group, name='edit_devices_in_group'),
]

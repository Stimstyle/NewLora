# access_control/urls.py

from django.urls import path
from . import views  # Импортируем представления

urlpatterns = [
    path('', views.home, name='home'),
    path('create_device/', views.create_device, name='create_device'),  # Страница для создания устройства
    path('device_list/', views.device_list, name='device_list'),        # Страница для отображения списка устройств
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
]

from django.urls import path
from UserDash.views import index, devices, notification
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('index/', index, name='index'),
    path('devices/', devices, name='devices'),  # Новый маршрут для устройств
    path('notification/', notification, name='notification'),  # Новый маршрут для устройств
]
from django.urls import path
from UserDash.views import index, devices, notification, groups, event
from . import views

urlpatterns = [
    path('index/', index, name='index'),
    path('devices/', devices, name='devices'),  # Новый маршрут для устройств
    path('notification/', notification, name='notification'),  # Новый маршрут для устройств
    path('groups/', groups, name='groups'),  # Новый маршрут для устройств
    path('event/', event, name='event'),   
    path('ajax/user-search/', views.user_search, name='user_search'),
    path('ajax_update_table/', views.ajax_update_table, name='ajax_update_table'),


    # другие маршруты...
]
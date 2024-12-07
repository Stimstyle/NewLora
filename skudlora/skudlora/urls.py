"""
URL configuration for skudlora project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# skudlora/urls.py
from UserDash.views import ajax_update_table
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include  # Импортируем include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('access_control.urls')),  # Подключаем URL-ы приложения access_control
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('post_receiver/', include('post_receiver.urls')),  # Подключаем маршруты из post_receiver
    path('ajax_update_table/', ajax_update_table, name='ajax_update_table'),
    path('UserDash/', include('UserDash.urls')),
]


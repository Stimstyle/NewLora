from django.apps import AppConfig


class AccessControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'access_control'

class CustomAuthConfig(AppConfig):
    name = 'django.contrib.auth'
    verbose_name = 'my super special auth name'
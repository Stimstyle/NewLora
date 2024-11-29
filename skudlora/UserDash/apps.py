from django.apps import AppConfig


class UserdashConfig(AppConfig):
    #default_auto_field = 'django.db.models.BigAutoField'
    name = 'UserDash'
    def ready(self):
        import UserDash.signals  # Подключаем сигналы    

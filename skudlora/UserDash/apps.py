from django.apps import AppConfig

class UserDashConfig(AppConfig):
    name = 'UserDash'

    def ready(self):
        import UserDash.signals  # Импортируем сигналы при готовности приложения
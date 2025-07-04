from django.apps import AppConfig


class NotificationServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notification_service'

    def ready(self):
        import apps.notification_service.signals

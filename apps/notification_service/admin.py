from django.contrib import admin

from apps.notification_service.models import (
    EmailNotification,
    SMSNotification,
    SystemNotification,
    NotificationTemplate,
    Event, NotificationPreference
)
from utils.admins import BaseSilentDeleteAdmin


@admin.register(EmailNotification)
class EmailNotificationAdmin(BaseSilentDeleteAdmin):
    list_display = [
        'title',
        'description',
        'receiver',
        'email',
        'is_deleted',
        'source',
        'create_time', 'priority'
    ]
    list_filter = ['is_viewed', 'priority']
    search_fields = [
        'title',
        'is_deleted',
        'email'
    ]
    raw_id_fields = ('receiver',)
    # readonly_fields = []

    # def get_readonly_fields(self, request, obj=None):
    #     return list(self.readonly_fields) + \
    #         [field.name for field in obj._meta.fields] + \
    #         [field.name for field in obj._meta.many_to_many]
    #
    # def has_add_permission(self, request):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False


@admin.register(SMSNotification)
class SMSNotificationAdmin(BaseSilentDeleteAdmin):
    list_display = [
        'description',
        'receiver',
        'is_deleted',
        'phone_number',
        'source',
        'create_time', 'priority'
    ]
    search_fields = ['phone_number']
    raw_id_fields = ('receiver',)
    list_filter = ['is_viewed', 'priority']


@admin.register(SystemNotification)
class SystemNotificationAdmin(BaseSilentDeleteAdmin):
    list_display = [
        'title',
        'description',
        'receiver',
        'is_deleted',
        'is_viewed',
        'source',
        'create_time', 'priority'
    ]
    search_fields = ['title']
    raw_id_fields = ('receiver',)
    list_filter = ['is_viewed', 'priority']


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(BaseSilentDeleteAdmin):
    list_display = [
        'title',
        'description',
        'template_type'
    ]
    search_fields = ['id', 'title']
    list_filter = ['template_type']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(BaseSilentDeleteAdmin):
    list_display = (
        'id',
        'entity_type',
        'entity_id',
        'get_notification_type_display',
        'is_enabled',
    )
    list_filter = (
        'entity_type',
        'notification_type',
        'is_enabled',
    )
    search_fields = (
        'entity_id',
    )
    ordering = ('-id',)


@admin.register(Event)
class EventAdmin(BaseSilentDeleteAdmin):
    list_display = [
        'event_type',
        'details',
        'timestamp'
    ]
    search_fields = ['id', 'event_type']
    list_filter = ['event_type']

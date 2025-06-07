import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notification_service.models import (
    SystemNotification,
    EmailNotification,
    SMSNotification,
    BaseNotificationModel,
)
from apps.users.models import CompanyUser

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


def should_notify_managers(instance):
    is_critical = instance.priority in {
        BaseNotificationModel.PriorityTypeChoices.HIGH,
        BaseNotificationModel.PriorityTypeChoices.CRITICAL,
    }

    if not is_critical:
        return False

    user = instance.receiver
    is_manager = CompanyUser.objects.filter(
        user=user, role=CompanyUser.RoleChoices.MANAGER
    ).exists()
    is_employee = CompanyUser.objects.filter(
        user=user, role=CompanyUser.RoleChoices.EMPLOYEE
    ).exists()

    if is_manager:
        return True

    notify_types_for_employee = {
        BaseNotificationModel.TypeNotificationChoices.ONLINE_CAMERA,
        BaseNotificationModel.TypeNotificationChoices.OFFLINE_CAMERA,
        BaseNotificationModel.TypeNotificationChoices.CREATE_CUSTOMER_BY_EMPLOYEE,
    }

    return is_employee and instance.type_notification in notify_types_for_employee


def notify_managers(instance):
    if not should_notify_managers(instance):
        return

    notification_data = {
        "id": str(instance.id),
        "title": instance.title,
        "description": instance.description,
        "priority": instance.priority,
        "timestamp": instance.timestamp.isoformat(),
    }

    try:
        async_to_sync(channel_layer.group_send)(
            "notifications_managers",
            {
                "type": "send_notification",
                "content": notification_data,
            }
        )
    except Exception as e:
        logger.error(f"WebSocket notification failed: {e}")


@receiver(post_save, sender=SystemNotification)
@receiver(post_save, sender=EmailNotification)
@receiver(post_save, sender=SMSNotification)
def send_notification_to_managers(sender, instance, created, **kwargs):
    if created:
        notify_managers(instance)

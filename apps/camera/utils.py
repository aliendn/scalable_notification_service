from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils.timezone import now

from apps.notification_service.models import Event, SystemNotification
from apps.users.models import CompanyUser
from utils.functions import stopwatch


@stopwatch(action="log_camera_event_and_notify")
def log_camera_event_and_notify(camera, action, performed_by, extra_metadata=None):
    metadata = {
        "camera_id": camera.id,
        "camera_name": camera.name,
        "action": action,
        "performed_by": performed_by.id if performed_by else None,
        "timestamp": now().isoformat(),
        **(extra_metadata or {}),
    }

    # Save to Event`s model
    event = Event.objects.create(
        event_type="camera_" + action,
        details=metadata,
        timestamp=now()
    )

    # Notify managers
    managers = CompanyUser.objects.filter(company=camera.company, role=CompanyUser.RoleChoices.MANAGER).select_related(
        'user')

    channel_layer = get_channel_layer()
    for manager in managers:
        SystemNotification.objects.create(
            receiver=manager.user,
            title=f"Camera {camera.name} - {action.replace('_', ' ').capitalize()}",
            description=f"{performed_by.full_name} performed action '{action}' on camera '{camera.name}'",
            priority=SystemNotification.PriorityTypeChoices.HIGH,
            source=f"camera:{camera.id}:{action}",
            event=event,
            timestamp=now()
        )

        async_to_sync(channel_layer.group_send)(
            f"user_{manager.user.id}",
            {
                "type": "notify",
                "content": {
                    "title": f"Camera {camera.name} - {action}",
                    "description": f"{performed_by.full_name} performed '{action}'",
                    "priority": "high",
                }
            }
        )
    return event

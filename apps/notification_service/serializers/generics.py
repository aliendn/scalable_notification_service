from rest_framework import serializers

from apps.notification_service.models import SystemNotification


class SystemNotificationSerializer(serializers.ModelSerializer):
    priority_display = serializers.CharField(
        source='get_priority_display',
        read_only=True
    )

    class Meta:
        model = SystemNotification
        fields = [
            'id',
            'title',
            'description',
            'priority',
            'priority_display',
            'is_viewed',
            'timestamp',
            'event'
        ]
        read_only_fields = fields

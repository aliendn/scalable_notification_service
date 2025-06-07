from rest_framework import serializers


class BaseNotificationSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    description = serializers.CharField()
    priority = serializers.IntegerField()
    is_viewed = serializers.BooleanField()
    timestamp = serializers.DateTimeField()
    event = serializers.CharField()
    type = serializers.SerializerMethodField()
    source = serializers.CharField()

    def get_type(self, obj):
        return obj.type if hasattr(obj, 'type') else None


class SelectedSystemNotificationSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        allow_empty=True,
        required=True,
        child=serializers.UUIDField(
            allow_null=False,
            required=True
        )
    )

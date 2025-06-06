from rest_framework import serializers

from apps.camera.models import Camera, CameraActionLog


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class CameraActionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraActionLog
        fields = '__all__'
        read_only_fields = ('id', 'timestamp')

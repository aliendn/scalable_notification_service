from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view
)
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.camera.models import Camera, CameraActionLog
from apps.camera.serializers.generics import CameraSerializer, CameraActionLogSerializer
from apps.camera.utils import log_camera_event_and_notify
from apps.users.permissions import IsCompanyManager


class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    permission_classes = [IsCompanyManager]
    http_method_names = ['get', 'head', 'options', 'post']

    def perform_create(self, serializer):
        serializer.save()
        log_camera_event_and_notify(
            camera=serializer.instance,
            action='created',
            performed_by=self.request.user,
            extra_metadata={"action": "create"}
        )

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        camera = self.get_object()
        camera.status = 'offline' if camera.status == 'online' else 'online'
        camera.save()
        log_camera_event_and_notify(
            camera=camera,
            action='turned_off' if camera.status == 'offline' else 'turned_on',
            performed_by=request.user
        )
        return Response(CameraSerializer(camera).data)

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        camera = self.get_object()
        camera.is_moved = True
        camera.save()
        log_camera_event_and_notify(
            camera=camera,
            action='moved',
            performed_by=request.user
        )
        return Response(CameraSerializer(camera).data)

    @action(detail=True, methods=['post'])
    def toggle_recording(self, request, pk=None):
        camera = self.get_object()
        camera.recording_status = (
            'recording' if camera.recording_status == 'stopped' else 'stopped'
        )
        camera.save()
        log_camera_event_and_notify(
            camera=camera,
            action='started_recording' if camera.recording_status == 'recording' else 'stopped_recording',
            performed_by=request.user
        )
        return Response(CameraSerializer(camera).data)


@extend_schema_view(
    list=extend_schema(tags=['Camera Logs']),
    retrieve=extend_schema(tags=['Camera Logs'])
)
class CameraActionLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CameraActionLog.objects.select_related('camera', 'performed_by').all()
    serializer_class = CameraActionLogSerializer
    permission_classes = [permissions.IsAuthenticated]

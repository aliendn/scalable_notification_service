import logging

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.notification_service.models import SystemNotification
from apps.notification_service.serializers.generics import SystemNotificationSerializer

logger = logging.getLogger(__name__)


class SystemNotificationViewSet(ModelViewSet):
    serializer_class = SystemNotificationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'head', 'options', 'post']

    def get_queryset(self):
        """Return only non-deleted notifications for current user"""
        return SystemNotification.objects.filter(
            receiver=self.request.user,
            is_deleted=False
        ).order_by('-timestamp')

    def get_object(self):
        """Get notification or return 404 with proper permissions"""
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark single notification as read"""
        notification = self.get_object()
        notification.is_viewed = True
        notification.save(update_fields=['is_viewed'])
        return Response({'status': 'marked as read'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_as_delete(self, request, pk=None):
        """Soft delete single notification"""
        notification = self.get_object()
        notification.is_deleted = True
        notification.save(update_fields=['is_deleted'])
        return Response({'status': 'marked as deleted'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def mark_selected_as_read(self, request):
        """Mark multiple notifications as read"""
        notification_ids = request.data.get('ids', [])
        if not notification_ids:
            return Response(
                {'error': 'No notification IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            updated = SystemNotification.objects.filter(
                id__in=notification_ids,
                receiver=request.user,
                is_deleted=False
            ).update(is_viewed=True)

        return Response({'updated_count': updated}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def mark_selected_as_delete(self, request):
        """Soft delete multiple notifications"""
        notification_ids = request.data.get('ids', [])
        if not notification_ids:
            return Response(
                {'error': 'No notification IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            updated = SystemNotification.objects.filter(
                id__in=notification_ids,
                receiver=request.user,
                is_deleted=False
            ).update(is_deleted=True)

        return Response({'deleted_count': updated}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read for current user"""
        updated = SystemNotification.objects.filter(
            receiver=request.user,
            is_deleted=False,
            is_viewed=False
        ).update(is_viewed=True)

        return Response({'updated_count': updated}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def mark_all_as_delete(self, request):
        """Soft delete all notifications for current user"""
        updated = SystemNotification.objects.filter(
            receiver=request.user,
            is_deleted=False
        ).update(is_deleted=True)

        return Response({'deleted_count': updated}, status=status.HTTP_200_OK)

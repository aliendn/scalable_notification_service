import logging

from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiResponse
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.notification_service.models import SystemNotification
from apps.notification_service.serializers.generics import SystemNotificationSerializer

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        tags=['Notifications'],
        summary='List user notifications',
        description='Retrieve all non-deleted notifications for the current user',
        responses={200: SystemNotificationSerializer(many=True)}
    ),
    retrieve=extend_schema(
        tags=['Notifications'],
        summary='Retrieve notification details',
        description='Get details of a specific notification'
    ),
    create=extend_schema(
        tags=['Notifications'],
        summary='Create new notification',
        description='Create a new system notification'
    )
)
class SystemNotificationViewSet(ModelViewSet):
    serializer_class = SystemNotificationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'head', 'options', 'post']

    def get_queryset(self):
        return SystemNotification.objects.filter(
            receiver=self.request.user,
            is_deleted=False
        ).order_by('-timestamp')

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    @extend_schema(
        tags=['Notifications'],
        summary='Mark notification as read',
        description='Mark a single notification as read',
        responses={
            200: OpenApiResponse(description='Notification marked as read'),
            404: OpenApiResponse(description='Notification not found')
        }
    )
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_viewed = True
        notification.save(update_fields=['is_viewed'])
        return Response({'status': 'marked as read'}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Notifications'],
        summary='Delete notification',
        description='Soft delete a single notification',
        responses={
            200: OpenApiResponse(description='Notification marked as deleted'),
            404: OpenApiResponse(description='Notification not found')
        }
    )
    @action(detail=True, methods=['post'])
    def mark_as_delete(self, request, pk=None):
        notification = self.get_object()
        notification.is_deleted = True
        notification.save(update_fields=['is_deleted'])
        return Response({'status': 'marked as deleted'}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Notifications'],
        summary='Mark selected as read',
        description='Mark multiple notifications as read',
        request=OpenApiTypes.OBJECT,
        parameters=[
            OpenApiParameter(
                name='ids',
                type={'type': 'array', 'items': {'type': 'integer'}},
                location=OpenApiParameter.QUERY,
                description='List of notification IDs to mark as read'
            )
        ],
        responses={
            200: OpenApiResponse(description='Count of updated notifications'),
            400: OpenApiResponse(description='Invalid input')
        }
    )
    @action(detail=False, methods=['post'])
    def mark_selected_as_read(self, request):
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

    @extend_schema(
        tags=['Notifications'],
        summary='Delete selected notifications',
        description='Soft delete multiple notifications',
        request=OpenApiTypes.OBJECT,
        parameters=[
            OpenApiParameter(
                name='ids',
                type={'type': 'array', 'items': {'type': 'integer'}},
                location=OpenApiParameter.QUERY,
                description='List of notification IDs to delete'
            )
        ],
        responses={
            200: OpenApiResponse(description='Count of deleted notifications'),
            400: OpenApiResponse(description='Invalid input')
        }
    )
    @action(detail=False, methods=['post'])
    def mark_selected_as_delete(self, request):
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

    @extend_schema(
        tags=['Notifications'],
        summary='Mark all as read',
        description='Mark all notifications as read for current user',
        responses={
            200: OpenApiResponse(description='Count of updated notifications')
        }
    )
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        updated = SystemNotification.objects.filter(
            receiver=request.user,
            is_deleted=False,
            is_viewed=False
        ).update(is_viewed=True)

        return Response({'updated_count': updated}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Notifications'],
        summary='Delete all notifications',
        description='Soft delete all notifications for current user',
        responses={
            200: OpenApiResponse(description='Count of deleted notifications')
        }
    )
    @action(detail=False, methods=['post'])
    def mark_all_as_delete(self, request):
        updated = SystemNotification.objects.filter(
            receiver=request.user,
            is_deleted=False
        ).update(is_deleted=True)

        return Response({'deleted_count': updated}, status=status.HTTP_200_OK)

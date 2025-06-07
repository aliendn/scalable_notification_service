import logging
from itertools import chain

from django.http import Http404
from django.utils.translation import gettext as _
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse, OpenApiExample
)
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from apps.notification_service.models import (
    SystemNotification, EmailNotification, SMSNotification, BaseNotificationModel
)
from apps.notification_service.serializers.base import BaseNotificationSerializer, SelectedSystemNotificationSerializer

logger = logging.getLogger(__name__)


class NotificationsListView(
    mixins.ListModelMixin, GenericViewSet
):
    serializer_class = BaseNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset_all(self):
        user = self.request.user
        type_param = self.request.query_params.get("type")
        valid_types = BaseNotificationModel.TypeNotificationChoices.values

        def filter_by_type(qs, type_val=None):
            if type_val is not None:
                return qs.filter(type_notification=type_val, is_type_enabled=True)
            return qs

        try:
            type_val = int(type_param) if type_param is not None else None
            if type_val is None and type_val not in valid_types:
                raise Http404("Notification type not found")
        except (ValueError, TypeError):
            raise Http404("Invalid notification type")

        system_qs = filter_by_type(
            SystemNotification.objects.filter(receiver=user, is_deleted=False), type_val
        )
        email_qs = filter_by_type(
            EmailNotification.objects.filter(receiver=user, is_deleted=False), type_val
        )
        sms_qs = filter_by_type(
            SMSNotification.objects.filter(receiver=user, is_deleted=False), type_val
        )

        combined = sorted(
            chain(system_qs, email_qs, sms_qs),
            key=lambda x: x.timestamp,
            reverse=True
        )
        return combined

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset_all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class NotificationsDetailView(
    mixins.ListModelMixin, GenericViewSet
):
    serializer_class = BaseNotificationSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        user = request.user
        for model in [SystemNotification, EmailNotification, SMSNotification]:
            try:
                obj = model.objects.get(id=pk, receiver=user, is_deleted=False, is_type_enabled=True)
                return Response(self.get_serializer(obj).data)
            except model.DoesNotExist:
                continue
        raise Http404("Notification not found")


class NotificationActionView(APIView):
    """Base view for marking or soft-deleting single and selected notifications."""
    permission_classes = [IsAuthenticated]
    success_message = ""

    def post(self, request, pk=None):
        instance = self.get_notification_instance(pk)
        if instance:
            self.perform_action(instance)
            return Response(data={"detail": _(self.success_message)}, status=status.HTTP_200_OK)
        raise Http404()

    def perform_action(self, instance):
        """Method to perform action, to be overridden in subclasses."""
        raise NotImplementedError

    def get_notification_instance(self, pk):
        user = self.request.user
        return SystemNotification.objects.filter(
            id=pk, receiver=user, is_deleted=False, is_type_enabled=True
        ).first()


class MarkNotificationAsReadView(NotificationActionView):
    success_message = "system notification marked as read"

    def perform_action(self, instance):
        instance.is_viewed = True
        instance.save()

    @extend_schema(
        summary="Mark Notification as Read",
        description="This endpoint marks a specific notification as read by setting its `is_viewed` field to `True`.",
        responses={
            200: OpenApiResponse(
                description="Notification successfully marked as read",
            ),
            404: OpenApiResponse(
                description="Notification not found",
            )
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SoftDeleteNotificationView(NotificationActionView):
    success_message = "system notification deleted"

    def perform_action(self, instance):
        instance.is_deleted = True
        instance.is_viewed = True
        instance.save()

    @extend_schema(
        summary="Soft-Delete Notification",
        description="This endpoint soft-deletes a specific notification by setting its `is_deleted` field to `True`.",
        request=None,
        responses={
            200: OpenApiResponse(
                description="Notification successfully soft-deleted"
            ),
            404: OpenApiResponse(
                description="Notification not found"
            )
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class BulkNotificationActionView(APIView):
    permission_classes = [IsAuthenticated]
    success_message = ""
    action_field = ""

    @swagger_auto_schema(request_body=SelectedSystemNotificationSerializer)
    def post(self, request):
        serializer = SelectedSystemNotificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                exception=True,
            )
        notification_ids = serializer.validated_data.get("notification_ids", [])

        self.perform_bulk_action(request.user, notification_ids)
        return Response(data={"detail": _(self.success_message)}, status=status.HTTP_200_OK)

    def perform_bulk_action(self, user, notification_ids):
        """Bulk action method to be overridden in subclasses."""
        raise NotImplementedError


class MarkSelectedNotificationsAsReadView(BulkNotificationActionView):
    success_message = "Marked as read for these notifications"
    action_field = "is_viewed"

    def perform_bulk_action(self, user, notification_ids):
        SystemNotification.objects.filter(
            id__in=notification_ids, receiver=user, is_viewed=False,
            is_deleted=False, is_type_enabled=True
        ).update(is_viewed=True)

    @extend_schema(
        summary="Mark Selected Notifications as Read",
        description="This endpoint marks a list of selected notifications as read by setting their `is_viewed` field to `True`.",
        request=SelectedSystemNotificationSerializer,
        responses={
            200: OpenApiResponse(
                description="Notifications successfully marked as read",
                response=SelectedSystemNotificationSerializer,
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={
                            "success": True,
                            "errors": [],
                            "data": None,
                            "message": "Notifications successfully marked as read"
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Notifications not found",
                response=SelectedSystemNotificationSerializer,
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={
                            "success": False,
                            "errors": [],
                            "data": None,
                            "message": "Notifications not found"
                        }
                    )
                ]
            )
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SoftDeleteSelectedNotificationsView(BulkNotificationActionView):
    """
    API endpoint for soft-deleting multiple selected notifications.

    This view allows users to soft-delete a batch of notifications. Notifications are updated in bulk
    with their `is_deleted` field set to `True` and `is_viewed` field set to `True`.

    **Permissions**:
        - Requires authentication.

    **Methods**:
        - POST: Soft-delete selected notifications by updating their `is_deleted` field to `True`.
    """
    success_message = "Deleted for these notifications"
    action_field = "is_deleted"

    def perform_bulk_action(self, user, notification_ids):
        SystemNotification.objects.filter(id__in=notification_ids, receiver=user, is_deleted=False,
                                          is_type_enabled=True).update(
            is_deleted=True, is_viewed=True)

    @extend_schema(
        summary="Soft-Delete Selected Notifications",
        description="This endpoint soft-deletes a list of selected notifications by setting their `is_deleted` field to `True`.",
        request=SelectedSystemNotificationSerializer,
        responses={
            200: OpenApiResponse(
                description="Notifications successfully marked as read",
                response=SelectedSystemNotificationSerializer,
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={
                            "success": True,
                            "errors": [],
                            "data": None,
                            "message": "Notifications successfully deleted"
                        }
                    )
                ]
            )
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MarkAllNotificationsAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Mark All Notifications as Read",
        description="This endpoint marks all unread notifications as read by setting their `is_viewed` field to `True`.",
        responses={
            200: OpenApiResponse(
                description="All notifications successfully marked as read"
            ),
            404: OpenApiResponse(
                description="No notifications found for the user"
            )
        }
    )
    def post(self, request):
        user = request.user
        SystemNotification.objects.filter(receiver=user, is_viewed=False, is_type_enabled=True).update(is_viewed=True)
        return Response(data={"detail": "marked as read all!!!!"}, status=status.HTTP_200_OK)


class SoftDeleteAllNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Soft-Delete All Notifications",
        description="This endpoint soft-deletes all notifications by setting their `is_deleted` field to `True`.",
        request=None,
        responses={
            200: OpenApiResponse(
                description="All notifications successfully soft-deleted"
            ),
            404: OpenApiResponse(
                description="No notifications found for the user"
            )
        }
    )
    def post(self, request):
        user = request.user
        SystemNotification.objects.filter(receiver=user, is_deleted=False, is_type_enabled=True).update(is_deleted=True)
        return Response(data={"detail": "deleted all!!!!"}, status=status.HTTP_200_OK)


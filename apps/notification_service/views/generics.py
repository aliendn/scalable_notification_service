import json
import logging

from django.core.serializers.json import DjangoJSONEncoder
from django.http import Http404
from django.http import StreamingHttpResponse
# from itertools import chain
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from django.utils.translation import gettext as _
from drf_spectacular.utils import (
    OpenApiResponse, OpenApiExample
)
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
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
from apps.notification_service.serializers.generics import SystemNotificationSerializer
from apps.users.permissions import IsCompanyEmployeeTypeChoices

logger = logging.getLogger(__name__)


@extend_schema(
    tags=["Notifications"],
    summary="List notifications",
    description="Retrieve a list of system notifications for the authenticated user with optional filters.",
    parameters=[
        OpenApiParameter(
            name="type",
            type=OpenApiTypes.INT,
            required=False,
            description="Type of notification, integer enum from `TypeNotificationChoices`."
        ),
        OpenApiParameter(
            name="priority",
            type=OpenApiTypes.INT,
            required=False,
            description="Priority level (0=LOW, 1=MEDIUM, 2=HIGH, 3=CRITICAL)."
        ),
        OpenApiParameter(
            name="from_time",
            type=OpenApiTypes.DATETIME,
            required=False,
            description="Start timestamp for filtering (ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`)."
        ),
        OpenApiParameter(
            name="to_time",
            type=OpenApiTypes.DATETIME,
            required=False,
            description="End timestamp for filtering (ISO 8601 format). Defaults to current time if not set."
        ),
    ]
)
class NotificationsListView(
    mixins.ListModelMixin, GenericViewSet
):
    serializer_class = SystemNotificationSerializer
    permission_classes = [IsCompanyEmployeeTypeChoices]

    def get_queryset_all(self):
        user = self.request.user
        params = self.request.query_params

        type_param = params.get("type")
        priority_param = params.get("priority")
        from_time_str = params.get("from_time")
        to_time_str = params.get("to_time")

        valid_types = BaseNotificationModel.TypeNotificationChoices.values
        type_val = None
        if type_param is not None:
            try:
                type_val = int(type_param)
                if type_val not in valid_types:
                    raise Http404("Invalid notification type")
            except (ValueError, TypeError):
                raise Http404("Invalid notification type")

        try:
            priority_val = int(priority_param) if priority_param else None
        except ValueError:
            raise Http404("Invalid priority")

        from_time = parse_datetime(from_time_str) if from_time_str else None
        to_time = parse_datetime(to_time_str) if to_time_str else now()

        if from_time_str and not from_time:
            raise Http404("Invalid from_time format")
        if to_time_str and not to_time:
            raise Http404("Invalid to_time format")

        queryset = SystemNotification.objects.filter(
            receiver=user,
            is_deleted=False,
            is_type_enabled=True,
        )

        if type_val is not None:
            queryset = queryset.filter(type_notification=type_val)

        if priority_param is not None:
            queryset = queryset.filter(priority=priority_val)

        if from_time:
            queryset = queryset.filter(timestamp__range=(from_time, to_time))

        queryset = queryset.values(
            "id", "title", "description", "priority", "timestamp",
            "is_viewed", "type_notification", "source", "event_id"
        )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset_all()
        serializer = self.get_serializer(queryset, many=True)
        return StreamingHttpResponse(self.generator(queryset), content_type='application/json')

    @staticmethod
    def generator(queryset):
        yield '['
        for i, item in enumerate(queryset):
            if i != 0:
                yield ','
            yield json.dumps(item, cls=DjangoJSONEncoder)
        yield ']'


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
                obj.is_viewed = True
                obj.save()
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

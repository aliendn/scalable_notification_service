from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.notification_service.models import Event
from apps.users.models import Company, User
from utils.models import BaseModel


# from psqlextra.models import PostgresPartitionedModel
# from psqlextra.types import PostgresPartitioningMethod


class Camera(BaseModel):
    class StatusChoices(models.IntegerChoices):
        ONLINE = 0, _("ONLINE")
        OFFLINE = 1, _("OFFLINE")

    class RecordingStatusChoices(models.IntegerChoices):
        RECORDING = 0, _("Recording")
        STOPPED = 1, _("Stopped")

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="cameras",
        db_index=True,
        verbose_name=_("Company")
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Camera Name")
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Location")
    )
    ip_address = models.GenericIPAddressField(
        protocol='IPv4',
        verbose_name=_("IP Address"),
        unique=True
    )

    status = models.PositiveSmallIntegerField(
        choices=StatusChoices.choices,
        db_index=True,
        verbose_name=_("status")
    )
    recording_status = models.PositiveSmallIntegerField(
        choices=RecordingStatusChoices.choices,
        db_index=True,
        verbose_name=_("recording status")
    )
    is_moved = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("is moved")
    )

    class Meta:
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["company", "recording_status"]),
        ]
        verbose_name = _("Camera")
        verbose_name_plural = _("Cameras")


class CameraActionLog(BaseModel):
    class ActionChoices(models.IntegerChoices):
        TURNED_OFF = 0, _("TURNED OFF")
        TURNED_ON = 1, _("TURNED ON")
        MOVED = 2, _("MOVED")
        STARTED_RECORDING = 3, _("STARTED RECORDING")
        STOPPED_RECORDING = 4, _("STOPPED RECORDING")

    camera = models.ForeignKey(
        Camera,
        on_delete=models.CASCADE,
        related_name="logs",
        db_index=True,
        verbose_name=_("camera")
    )
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="camera_actions",
        db_index=True,
        verbose_name=_("performed by")
    )
    action = models.PositiveSmallIntegerField(
        choices=ActionChoices.choices,
        db_index=True,
        verbose_name=_("action")
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name=_("timestamp")
    )
    metadata = models.JSONField(default=dict, verbose_name=_("metadata"))
    old_status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("old status")
    )
    new_status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("new status")
    )

    # class PartitioningMeta:
    #     method = PostgresPartitioningMethod.RANGE
    #     key = ['timestamp']

    class Meta:
        indexes = [
            models.Index(fields=["camera", "timestamp"]),
            models.Index(fields=["performed_by"]),
            models.Index(fields=["action", "timestamp"]),
            GinIndex(fields=["metadata"]),
        ]
        verbose_name = _("Camera Action Log")
        verbose_name_plural = _("Camera Action Logs")

    def __str__(self):
        return f"{self.action} - {self.camera.name} by {self.performed_by}"

import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.users.models import User
from utils.models import BaseModel

logger = logging.getLogger(__name__)


class Event(BaseModel):
    event_type = models.CharField(
        max_length=50,
        verbose_name=_("event type")
    )
    details = models.JSONField(
        default=dict,
        verbose_name=_("details")
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("events timestamp")
    )

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')


class BaseNotificationModel(BaseModel):
    class PriorityTypeChoices(models.IntegerChoices):
        LOW = 0, _('LOW')
        MEDIUM = 1, _("MEDIUM")
        HIGH = 2, _("HIGH")
        CRITICAL = 3, _("CRITICAL")

    class TypeNotificationChoices(models.IntegerChoices):
        CREATE_CUSTOMER_BY_EMPLOYEE = 0, _('CREATE_CUSTOMER_BY_EMPLOYEE')
        RECORDING_CAMERA = 1, _("RECORDING_CAMERA")
        STOPPED_CAMERA = 2, _("STOPPED_CAMERA")
        ONLINE_CAMERA = 3, _("ONLINE_CAMERA")
        OFFLINE_CAMERA = 4, _("OFFLINE_CAMERA")

    title = models.CharField(
        max_length=255,
        verbose_name=_('title'),
    )
    description = models.TextField(
        max_length=10000,
        verbose_name=_('description'),
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name=_("is deleted")
    )
    source = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("source of template notification"),
    )
    priority = models.PositiveSmallIntegerField(
        choices=PriorityTypeChoices.choices,
        verbose_name=_("application priority type"),
    )
    event = models.ForeignKey(
        Event,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    is_viewed = models.BooleanField(
        default=False,
        verbose_name=_('viewed by user'),
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("timestamp")
    )
    type_notification = models.PositiveSmallIntegerField(
        choices=TypeNotificationChoices.choices,
        verbose_name=_("application type of notification"),
    )
    is_type_enabled = models.BooleanField(
        default=False,
        verbose_name=_("is type enabled for the user")
    )

    @classmethod
    def get_by_source(cls, source):
        try:
            return cls.objects.get(source=source)
        except ObjectDoesNotExist:
            logger.error(f"NotificationTemplate with source {source} does not exist.")
            return None

    class Meta:
        abstract = True
        verbose_name = _('Base Notification')
        verbose_name_plural = _('Base Notifications')


class EmailNotification(BaseNotificationModel):
    receiver = models.ForeignKey(
        to=User,
        related_name='received_emails',
        on_delete=models.PROTECT,
        verbose_name=_('receiver'),
    )
    email = models.EmailField(
        verbose_name=_('email'),
    )

    def __str__(self) -> str:
        return f"{str(self.id)} {self.title}"

    class Meta:
        verbose_name = _('Email Notification')
        verbose_name_plural = _('Email Notifications')
        indexes = [
            models.Index(fields=["receiver", "is_viewed", "priority"]),
            models.Index(fields=["timestamp"]),
        ]
        ordering = ["-timestamp"]


class SMSNotification(BaseNotificationModel):
    receiver = models.ForeignKey(
        to=User,
        related_name='received_sms',
        on_delete=models.PROTECT,
        verbose_name=_('receiver'),
    )
    phone_number = models.CharField(
        max_length=16,
        verbose_name=_('phone number'),
    )

    def __str__(self) -> str:
        return f"{str(self.id)} {self.title}"

    class Meta:
        verbose_name = _('Sms Notification')
        verbose_name_plural = _('Sms Notifications')
        indexes = [
            models.Index(fields=["receiver", "is_viewed", "priority"]),
            models.Index(fields=["timestamp"]),
        ]
        ordering = ["-timestamp"]


class SystemNotification(BaseNotificationModel):
    receiver = models.ForeignKey(
        to=User,
        related_name='received_system_notifications',
        on_delete=models.PROTECT,
        verbose_name=_('receiver'),
    )

    def __str__(self) -> str:
        return f"{str(self.id)} {self.title}"

    class Meta:
        verbose_name = _('System Notification')
        verbose_name_plural = _('System Notifications')
        indexes = [
            models.Index(fields=["receiver", "is_viewed", "priority"]),
            models.Index(fields=["timestamp"]),
        ]
        ordering = ["-timestamp"]

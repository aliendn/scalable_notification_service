import random

from django.core.management.base import BaseCommand
from faker import Faker

from apps.camera.models import Camera
from apps.notification_service.models import (
    NotificationPreference,
    EmailNotification,
    SMSNotification,
    SystemNotification,
    NotificationTemplate,
    Event,
)
from apps.users.models import User, Company

fake = Faker()


class Command(BaseCommand):
    help = "Generate fake test data for notifications and preferences"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting test data generation...")

        # Get active companies, all cameras, all users
        companies = list(Company.objects.filter(is_active=True))
        cameras = list(Camera.objects.all())
        users = list(User.objects.all())  # Assuming User doesn't have is_active field

        self.stdout.write(f"Found {len(companies)} companies, {len(cameras)} cameras, {len(users)} users.")

        notif_types = [
            NotificationPreference.NotificationTypeChoices.SYSTEM,
            NotificationPreference.NotificationTypeChoices.SMS,
            NotificationPreference.NotificationTypeChoices.EMAIL,
        ]

        # 1. Create NotificationPreferences for companies and cameras
        preferences = []

        # Company preferences
        for company in companies:
            for ntype in notif_types:
                enabled = random.choice([True, False])
                preferences.append(NotificationPreference(
                    entity_type=NotificationPreference.EntityTypeChoices.Company,
                    entity_id=company.pk,  # UUIDField
                    notification_type=ntype,
                    is_enabled=enabled,
                ))

        # Camera preferences
        for camera in cameras:
            for ntype in notif_types:
                enabled = random.choice([True, False])
                preferences.append(NotificationPreference(
                    entity_type=NotificationPreference.EntityTypeChoices.Camera,
                    entity_id=camera.pk,
                    notification_type=ntype,
                    is_enabled=enabled,
                ))

        NotificationPreference.objects.bulk_create(preferences)
        self.stdout.write(f"Created {len(preferences)} notification preferences.")

        # 2. Create sample event for notifications
        event = Event.objects.create(event_type="TEST_EVENT", details={"info": "Fake event for testing"})

        # Create notification templates if not exist
        for ttype in notif_types:
            NotificationTemplate.objects.get_or_create(
                title=f"Template for {NotificationPreference.NotificationTypeChoices(ttype).label}",
                template_type=ttype,
                defaults={
                    "description": f"Description for {NotificationPreference.NotificationTypeChoices(ttype).label}"},
            )

        # 3. Create notifications for users only
        system_notifications = []
        sms_notifications = []
        email_notifications = []

        for user in users:
            system_notifications.append(SystemNotification(
                receiver=user,
                title="System Notification",
                description="This is a fake system notification.",
                source="test_source",
                priority=1,  # MEDIUM priority
                event=event,
            ))

            sms_notifications.append(SMSNotification(
                receiver=user,
                phone_number=fake.msisdn()[:16],  # Truncate to max length 16, generate numeric string
                title="SMS Notification",
                description="This is a fake SMS notification.",
                source="test_source",
                priority=1,
                event=event,
            ))

            email_notifications.append(EmailNotification(
                receiver=user,
                email=user.email,
                title="Email Notification",
                description="This is a fake email notification.",
                source="test_source",
                priority=1,
                event=event,
            ))

        SystemNotification.objects.bulk_create(system_notifications)
        SMSNotification.objects.bulk_create(sms_notifications)
        EmailNotification.objects.bulk_create(email_notifications)

        self.stdout.write(
            f"Created {len(system_notifications)} system, {len(sms_notifications)} sms, and {len(email_notifications)} email notifications."
        )

        self.stdout.write("Test data generation completed successfully.")

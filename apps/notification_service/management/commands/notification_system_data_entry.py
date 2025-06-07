from django.core.management.base import BaseCommand
from faker import Faker

from apps.camera.models import Camera
from apps.notification_service.models import (
    EmailNotification,
    SMSNotification,
    SystemNotification,
    Event,
)
from apps.users.models import User, Company

fake = Faker()


class Command(BaseCommand):
    help = "Generate fake test data for notifications and preferences"

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10)

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting test data generation...")
        data_count = kwargs['count']

        # Get active companies, all cameras, all users
        companies = list(Company.objects.filter(is_active=True))
        cameras = list(Camera.objects.all())
        user = User.objects.get(is_active=True, email="dehghan215@gmail.com")

        self.stdout.write(f"Found {len(companies)} companies, {len(cameras)} cameras, {(user)} users.")

        event = Event.objects.create(
            event_type="TEST_EVENT",
            details={
                "event_type": "camera_manual",
                "details": {
                    "camera_id": "123",
                    "performer_id": "456",
                    "status_change": "ONLINE → OFFLINE"
                }
            }
        )

        system_notifications = []
        sms_notifications = []
        email_notifications = []

        for _ in range(data_count):
            system_notifications.append(SystemNotification(
                receiver=user,
                title=fake.street_name(),
                description=fake.text(max_nb_chars=80),
                source=f"{fake.random_int(min=0, max=1)}",
                priority=fake.random_int(min=0, max=3),
                event=event,
                type_notification=fake.random_int(min=0, max=4)
            ))

            sms_notifications.append(SMSNotification(
                receiver=user,
                phone_number=user.phone_number,  # Truncate to max length 16, generate numeric string
                title=f"sms sent to {fake.name_male()}",
                description="This is a fake SMS notification.",
                source=f"{fake.random_int(min=0, max=1)}",
                priority=fake.random_int(min=0, max=3),
                event=event,
                type_notification=fake.random_int(min=0, max=4)
            ))

            email_notifications.append(EmailNotification(
                receiver=user,
                email=user.email,
                title=f"Email sent to {fake.name_male()}",
                description="This is a fake Email notification.",
                source=f"{fake.random_int(min=0, max=1)}",
                priority=fake.random_int(min=0, max=3),
                event=event,
                type_notification=fake.random_int(min=0, max=4)
            ))

        SystemNotification.objects.bulk_create(system_notifications)
        SMSNotification.objects.bulk_create(sms_notifications)
        EmailNotification.objects.bulk_create(email_notifications)

        self.stdout.write(
            f"Created {len(system_notifications)} system, {len(sms_notifications)} sms, and {len(email_notifications)} email notifications."
        )

        self.stdout.write("Test data generation completed successfully.")

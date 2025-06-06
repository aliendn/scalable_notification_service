import random

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from apps.notification_service.models import (
    SystemNotification,
    EmailNotification,
    SMSNotification,
    NotificationTemplate,
    Event,
)
from apps.users.models import User

fake = Faker()


class Command(BaseCommand):
    help = "Generate test notification data"

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help="Number of each notification type to create")

    def handle(self, *args, **options):
        count = options['count']
        users = list(User.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR("❌ No users found. Create users before running this command."))
            return

        self.stdout.write(f"Creating {count} notifications of each type...")

        # Create Notification Templates
        for _ in range(count):
            NotificationTemplate.objects.create(
                title=fake.sentence(),
                description=fake.paragraph(nb_sentences=5),
                template_type=random.choice([0, 1, 2])
            )

        # Create Events
        events = [
            Event.objects.create(
                event_type=fake.word(),
                details={"context": fake.sentence()},
                timestamp=timezone.now()
            ) for _ in range(count)
        ]

        # System Notifications
        system_notifications = []
        for _ in range(count):
            user = random.choice(users)
            system_notifications.append(SystemNotification(
                receiver=user,
                title=fake.sentence(),
                description=fake.text(),
                priority=random.randint(0, 3),
                event=random.choice(events),
                source="system_test",
                is_viewed=random.choice([True, False])
            ))
        SystemNotification.objects.bulk_create(system_notifications)

        # Email Notifications
        email_notifications = []
        for _ in range(count):
            user = random.choice(users)
            email_notifications.append(EmailNotification(
                receiver=user,
                email=user.email,
                title=fake.sentence(),
                description=fake.text(),
                priority=random.randint(0, 3),
                event=random.choice(events),
                source="email_test",
                is_viewed=random.choice([True, False])
            ))
        EmailNotification.objects.bulk_create(email_notifications)

        # SMS Notifications
        sms_notifications = []
        for _ in range(count):
            user = random.choice(users)
            sms_notifications.append(SMSNotification(
                receiver=user,
                phone_number=user.phone_number,
                title=fake.sentence(),
                description=fake.text(),
                priority=random.randint(0, 3),
                event=random.choice(events),
                source="sms_test",
                is_viewed=random.choice([True, False])
            ))
        SMSNotification.objects.bulk_create(sms_notifications)

        self.stdout.write(self.style.SUCCESS("✅ Notification test data generated successfully."))

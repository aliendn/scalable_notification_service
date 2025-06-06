from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from faker import Faker

from apps.users.models import User, Company, CompanyUser
from apps.camera.models import *
from apps.notification_service.models import Event

import random
from django.utils import timezone

fake = Faker()


class Command(BaseCommand):
    help = 'Generate test data for Users, Companies, Cameras, Logs, and Events'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10)
        parser.add_argument('--cameras', type=int, default=5)
        parser.add_argument('--logs-per-camera', type=int, default=10)

    def handle(self, *args, **options):
        user_count = options['users']
        camera_count = options['cameras']
        logs_per_camera = options['logs_per_camera']

        self.stdout.write("Creating companies...")
        company = Company.objects.create(name=fake.company())

        self.stdout.write("Creating users...")
        users = []
        for i in range(user_count):
            email = f"user{i}_{get_random_string(5)}@example.com"
            phone = f"+989{random.randint(100000000, 999999999)}"
            user = User(
                full_name=fake.name(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=email,
                phone_number=phone,
                username=email,  # ensure uniqueness for bulk_create
            )
            users.append(user)

        users = User.objects.bulk_create(users)

        self.stdout.write("Creating company users...")
        company_users = [
            CompanyUser(
                user=user,
                company=company,
                role=random.choice(list(CompanyUser.RoleChoices.values))
            ) for user in users
        ]
        CompanyUser.objects.bulk_create(company_users)

        self.stdout.write("Creating cameras...")
        cameras = []
        for i in range(camera_count):
            ip = f"192.168.1.{i + 1}"
            camera = Camera(
                company=company,
                name=f"Camera {i + 1}",
                location=fake.address(),
                ip_address=ip,
                status=random.choice([0, 1]),
                recording_status=random.choice([0, 1]),
                is_moved=random.choice([True, False]),
            )
            cameras.append(camera)

        cameras = Camera.objects.bulk_create(cameras)
        trigger_choices = ['TURNED OFF', 'TURNED ON', 'MOVED', 'STARTED RECORDING', 'STOPPED RECORDING']

        self.stdout.write("Creating events and logs...")
        logs = []
        for camera in cameras:
            for _ in range(logs_per_camera):
                performer = random.choice(users)
                action = random.choice(CameraActionLog.ActionChoices.values)
                event = Event.objects.create(
                    event_type=fake.word(),
                    details={
                    "camera_id": str(camera.id),
                    "performer_id": str(performer.id),
                    "status_change": "online → offline"
                },
                    timestamp=timezone.now()
                )
                log = CameraActionLog(
                    camera=camera,
                    performed_by=performer,
                    action=action,
                    timestamp=timezone.now(),
                    metadata={
                        "old_status": "online",
                        "new_status": "offline",
                        "trigger": random.choice(trigger_choices),
                        "ip": f"192.168.1.{random.randint(1, 254)}",
                        "location_change": {
                            "from": fake.building_number(),
                            "to": fake.building_number()
                        },
                        "firmware_version": f"v{random.randint(1, 5)}.{random.randint(0, 9)}",
                        "signal_strength": f"{random.randint(1, 5)} bars"
                    },
                    old_status="online",
                    new_status="offline"
                )
                logs.append(log)

        CameraActionLog.objects.bulk_create(logs)

        self.stdout.write(self.style.SUCCESS("✅ Test data generation completed."))

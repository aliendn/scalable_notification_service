from django.core.management.base import BaseCommand

from apps.notification_service.models import (
    NotificationTemplate,
)


class Command(BaseCommand):
    help = 'Create sample data for email notifications templates in the database'

    def handle(self, *args, **kwargs):
        # Create sample notification templates
        self.stdout.write(self.style.SUCCESS('system notification data entry started.'))

        system_send_success_mail_for_generated_wkk, created = NotificationTemplate.objects.get_or_create(
            title='send_create_snapshot_vm_notification_system',
            description='send_create_snapshot_vm_notification_system.',
            template_type=NotificationTemplate.TemplateTypeChoices.SYSTEM,
            action='vps.send_create_snapshot_vm_notification'
        )
        if created:
            self.stdout.write(self.style.SUCCESS('success create wkk system notification template created.'))

        self.stdout.write(
            self.style.SUCCESS(
                ("attention!!!\n",
                 "If your notification template has been \n",
                 "existing in your database with this \n",
                 "command we don't update it and we \n",
                 "skipped the creation; additionally \n",
                 "checks ensures the notification HTML \n",
                 "template exists in \n",
                 "the template directory \n"
                 )
            ))

        self.stdout.write(self.style.SUCCESS('notification data entry complete successfully.'))

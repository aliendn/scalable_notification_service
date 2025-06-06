# from django.db.models.signals import post_migrate
# from django.dispatch import receiver
#
#
# @receiver(post_migrate)
# def create_default_company_groups(sender, **kwargs):
#     from django.contrib.auth.models import Group
#     from apps.users.constants import ROLES_COMPANIES
#
#     if sender.name == 'apps.users':  # Prevents multiple firing
#         for role in ROLES_COMPANIES:
#             Group.objects.get_or_create(name=f"company_{role}")

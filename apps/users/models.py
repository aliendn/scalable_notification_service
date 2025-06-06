from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.users.constants import MOBILE_REGEX
from utils.models import BaseUserModel, BaseModel


class User(BaseUserModel):
    full_name = models.CharField(max_length=255, verbose_name=_("full name"))
    first_name = models.CharField(max_length=255, verbose_name=_("first name"))
    last_name = models.CharField(max_length=255, verbose_name=_("last name"))

    phone_number = models.CharField(
        db_index=True,
        max_length=14,
        unique=True,
        validators=[RegexValidator(regex=MOBILE_REGEX)],
        verbose_name=_("phone number"),
        help_text=_("Iranian mobile number starting with +989 or 00989 followed by 8 digits")
    )
    email = models.EmailField(unique=True, verbose_name=_("email"))

    def __str__(self):
        return self.full_name or self.email

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.fullname = self.first_name + self.last_name
        if not self.username:
            self.username = self.email
        return super().save(*args, **kwargs)


class Company(BaseModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Company Name")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active Company")
    )

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")


    def __str__(self):
        return self.name


class CompanyUser(BaseModel):
    class RoleChoices(models.IntegerChoices):
        MANAGER = 0, _('Manager')
        EMPLOYEE = 1, _('Employee')
        CUSTOMER = 2, _('Customer')

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='company_memberships',
        verbose_name=_("user")
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name=_("company")
    )
    role = models.PositiveSmallIntegerField(
        choices=RoleChoices.choices,
        verbose_name=_("role")
    )

    class Meta:
        verbose_name = _("Company User Profile")
        verbose_name_plural = _("Company User Profiles")
        unique_together = ('user', 'company')

    def __str__(self):
        return f"{self.user.full_name} ({self.role}) - {self.company.name}"

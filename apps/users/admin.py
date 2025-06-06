from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.users.models import User, Company, CompanyUser
from utils.admins import BaseUserAdmin, BaseSilentDeleteAdmin


class CompanyUserInline(admin.TabularInline):
    model = CompanyUser
    extra = 1
    fields = ('company', 'role')
    autocomplete_fields = ('company',)
    verbose_name = _('Company Profile')
    verbose_name_plural = _('Company Profiles')


class UserAdmin(BaseUserAdmin, BaseSilentDeleteAdmin):
    inlines = [CompanyUserInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change and obj.is_superuser:
            company_name = f"{obj.full_name or obj.email} Company"
            company, created = Company.objects.get_or_create(name=company_name)
            CompanyUser.objects.get_or_create(
                user=obj,
                company=company,
                defaults={'role': CompanyUser.RoleChoices.MANAGER}
            )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active',)
    search_fields = ('name',)


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'role',)
    list_filter = ('role', 'company',)
    search_fields = ('user__full_name', 'company__name',)
    autocomplete_fields = ('user', 'company',)


admin.site.register(User, UserAdmin)

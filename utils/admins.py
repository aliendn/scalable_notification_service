from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _

from utils.models import BaseModel


class BaseSilentDeleteAdmin(admin.ModelAdmin):
    actions = ["silent_delete_object"]

    def silent_delete_object(self, request, queryset):
        queryset.delete()


class BaseAdmin(admin.ModelAdmin):
    list_display = ('__str__',)

    list_filter = ()

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        for col in BaseModel.auto_cols:
            try:
                fields.remove(col)
            except Exception:
                pass
        return fields

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets += (_('other data'), {
            'fields': (
                'create_time',
                'modify_time',
            )
        }),
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        return readonly_fields + ('create_time', 'modify_time',)

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        return list_display + ('modify_time',)


class BaseUserAdmin(UserAdmin):
    list_display = ('email', 'phone_number', 'first_name', 'last_name', 'username',)
    fieldsets = (
        (None, {'fields': ('username', 'password', )}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email',)}),
        (_('Additional Data'), {'fields': ('phone_number',)}),
        (
            _('Permissions'),
            {
                'fields': ('is_active', 'is_superuser',),
            },
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'first_name', 'last_name', 'password1', 'password2', 'phone_number', 'email'),
            },
        ),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')

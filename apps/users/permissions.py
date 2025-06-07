from rest_framework.permissions import BasePermission

from apps.notification_service.models import BaseNotificationModel
from apps.users.models import CompanyUser


class IsCompanyManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.company_memberships.filter(
            role=CompanyUser.RoleChoices.MANAGER.value
        ).exists()


class IsCompanyEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user and (
                request.user.company_memberships.filter(
                    role=CompanyUser.RoleChoices.EMPLOYEE.value
                ).exists() or request.user.company_memberships.filter(
            role=CompanyUser.RoleChoices.MANAGER.value
        ).exists()
        )


class IsCompanyEmployeeTypeChoices(BasePermission):
    def has_permission(self, request, view):
        type = request.__dict__["parser_context"]["kwargs"].get("type", None)
        is_employee = request.user.company_memberships.filter(
            role=CompanyUser.RoleChoices.EMPLOYEE.value
        ).exists()
        is_manager = request.user.company_memberships.filter(
            role=CompanyUser.RoleChoices.MANAGER.value
        ).exists()
        notify_types_for_employee = {
            BaseNotificationModel.TypeNotificationChoices.ONLINE_CAMERA,
            BaseNotificationModel.TypeNotificationChoices.OFFLINE_CAMERA,
            BaseNotificationModel.TypeNotificationChoices.CREATE_CUSTOMER_BY_EMPLOYEE,
        }
        if request.user and is_manager:
            return True
        if request.user and is_employee and type:
            return type in notify_types_for_employee


class IsCompanyCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.company_memberships.filter(
            role=CompanyUser.RoleChoices.CUSTOMER.value
        ).exists()

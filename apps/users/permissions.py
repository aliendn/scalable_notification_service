from rest_framework.permissions import BasePermission

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


class IsCompanyCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.company_memberships.filter(
            role=CompanyUser.RoleChoices.CUSTOMER.value
        ).exists()

from rest_framework.permissions import BasePermission

from apps.users.models import CompanyUser


class IsCompanyManager(BasePermission):
    def has_permission(self, request, view):
        # rules ROLES_COMPANIES[0] means MANAGER
        return request.user and request.user.company_memberships.filter(
            role=CompanyUser.RoleChoices.MANAGER.value
        ).exists()


class IsCompanyEmployee(BasePermission):
    def has_permission(self, request, view):
        # rules ROLES_COMPANIES[1] means EMPLOYEE
        return request.user and (
                request.user.company_memberships.filter(
                    role=CompanyUser.RoleChoices.EMPLOYEE.value
                ).exists() or request.user.company_memberships.filter(
            role=CompanyUser.RoleChoices.MANAGER.value
        ).exists()
        )


class IsCompanyCustomer(BasePermission):
    def has_permission(self, request, view):
        # rules ROLES_COMPANIES[2] means CUSTOMER
        return request.user and request.user.company_memberships.filter(
            role=CompanyUser.RoleChoices.CUSTOMER.value
        ).exists()

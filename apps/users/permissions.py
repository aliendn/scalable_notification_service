from rest_framework.permissions import BasePermission

from apps.users.constants import ROLES_COMPANIES


class IsCompanyManager(BasePermission):
    def has_permission(self, request, view):
        # rules ROLES_COMPANIES[0] means MANAGER
        return request.user and request.user.company_memberships.filter(role=ROLES_COMPANIES[0]).exists()


class IsCompanyEmployee(BasePermission):
    def has_permission(self, request, view):
        # rules ROLES_COMPANIES[1] means EMPLOYEE
        return request.user and request.user.company_memberships.filter(role=ROLES_COMPANIES[1]).exists()


class IsCompanyCustomer(BasePermission):
    def has_permission(self, request, view):
        # rules ROLES_COMPANIES[2] means CUSTOMER
        return request.user and request.user.company_memberships.filter(role=ROLES_COMPANIES[2]).exists()

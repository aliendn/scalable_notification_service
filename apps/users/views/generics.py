import logging

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import Company, CompanyUser
from apps.users.permissions import IsCompanyManager, IsCompanyEmployee
from apps.users.serializers.generics import (
    UserSerializer,
    CompanySerializer,
    CompanyUserSerializer,
    ChangeRoleSerializer
)

logger = logging.getLogger(__name__)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(username=response.data['email'])
        refresh = RefreshToken.for_user(user)
        response.data['access'] = str(refresh.access_token)
        response.data['refresh'] = str(refresh)
        return response


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsCompanyManager]

    def perform_create(self, serializer):
        company = serializer.save()
        # Automatically add creator as manager
        CompanyUser.objects.create(
            user=self.request.user,
            company=company,
            role=CompanyUser.RoleChoices.MANAGER
        )


class CompanyUserViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyUserSerializer
    permission_classes = [IsCompanyManager]

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return CompanyUser.objects.filter(company_id=company_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['company'] = get_object_or_404(Company, id=self.kwargs['company_id'])
        return context

    @action(detail=True, methods=['post'], serializer_class=ChangeRoleSerializer)
    def change_role(self, request, company_id=None, pk=None):
        company_user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_role = serializer.validated_data['role']

        # Prevent removing last manager
        if (company_user.role == CompanyUser.RoleChoices.MANAGER and
                new_role != CompanyUser.RoleChoices.MANAGER):
            managers_count = CompanyUser.objects.filter(
                company_id=company_id,
                role=CompanyUser.RoleChoices.MANAGER
            ).exclude(id=company_user.id).count()
            if managers_count == 0:
                return Response(
                    {"detail": "Cannot remove last manager from company"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        company_user.role = new_role
        company_user.save()
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        company_user = self.get_object()

        # Prevent self-deletion
        if company_user.user == request.user:
            return Response(
                {"detail": "You cannot remove yourself from the company"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Soft delete user
        user = company_user.user
        user.is_active = False
        user.save()

        # Remove from company
        company_user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerCreateViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyUserSerializer
    permission_classes = [IsCompanyEmployee]

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return CompanyUser.objects.filter(
            company_id=company_id,
            role=CompanyUser.RoleChoices.CUSTOMER
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['company'] = get_object_or_404(Company, id=self.kwargs['company_id'])
        return context

    def perform_create(self, serializer):
        serializer.save(
            role=CompanyUser.RoleChoices.CUSTOMER,
            company_id=self.kwargs['company_id']
        )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsCompanyManager]

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return User.objects.filter(
            company_memberships__company_id=company_id,
            is_active=True
        )

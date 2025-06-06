import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse
)
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.notification_service.models import SystemNotification
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


@extend_schema(
    tags=['Users'],
    summary='User registration',
    description='Register a new user account and get JWT tokens',
    responses={
        201: OpenApiResponse(
            response=UserSerializer,
            description='User created successfully with tokens'
        ),
        400: OpenApiResponse(description='Invalid input data')
    }
)
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


@extend_schema_view(
    list=extend_schema(
        tags=['Users'],
        summary='List companies',
        description='List all companies managed by current user (Manager only)'
    ),
    create=extend_schema(
        tags=['Users'],
        summary='Create company',
        description='Create a new company (Manager only)'
    ),
    retrieve=extend_schema(
        tags=['Users'],
        summary='Retrieve company',
        description='Get company details'
    ),
    update=extend_schema(
        tags=['Users'],
        summary='Update company',
        description='Full update of company details'
    ),
    partial_update=extend_schema(
        tags=['Users'],
        summary='Partial update company',
        description='Partial update of company details'
    ),
    destroy=extend_schema(
        tags=['Users'],
        summary='Delete company',
        description='Delete a company'
    )
)
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsCompanyManager]

    @extend_schema(
        tags=['Users'],
        description='Create company and automatically assign creator as manager'
    )
    def perform_create(self, serializer):
        company = serializer.save()
        CompanyUser.objects.create(
            user=self.request.user,
            company=company,
            role=CompanyUser.RoleChoices.MANAGER
        )


@extend_schema_view(
    list=extend_schema(
        tags=['Users'],
        summary='List company users',
        description='List all users in a company (Manager only)',
        parameters=[
            OpenApiParameter(
                name='company_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Company ID'
            )
        ]
    ),
    create=extend_schema(
        tags=['Users'],
        summary='Add user to company',
        description='Add a user to company (Manager only)'
    ),
    retrieve=extend_schema(
        tags=['Users'],
        summary='Get company user details',
        description='Get details of a user in company'
    ),
    destroy=extend_schema(
        tags=['Users'],
        summary='Remove user from company',
        description='Soft delete user and remove from company'
    )
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

    @extend_schema(
        tags=['Users'],
        summary='Change user role',
        description='Change role of a user in company (Manager only)',
        request=ChangeRoleSerializer,
        responses={
            200: OpenApiResponse(description='Role changed successfully'),
            400: OpenApiResponse(description='Cannot remove last manager'),
            403: OpenApiResponse(description='Permission denied')
        }
    )
    @action(detail=True, methods=['post'], serializer_class=ChangeRoleSerializer)
    def change_role(self, request, company_id=None, pk=None):
        company_user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_role = serializer.validated_data['role']

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

    @extend_schema(
        tags=['Users'],
        description='Soft delete user and remove from company',
        responses={
            204: OpenApiResponse(description='User removed successfully'),
            403: OpenApiResponse(description='Cannot remove yourself')
        }
    )
    def destroy(self, request, *args, **kwargs):
        company_user = self.get_object()

        if company_user.user == request.user:
            return Response(
                {"detail": "You cannot remove yourself from the company"},
                status=status.HTTP_403_FORBIDDEN
            )

        user = company_user.user
        user.is_active = False
        user.save()
        company_user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(
        tags=['Users'],
        summary='List customers',
        description='List all customers in a company (Employee only)',
        parameters=[
            OpenApiParameter(
                name='company_id',
                location=OpenApiParameter.PATH,
                description='Company ID'
            )
        ]
    ),
    create=extend_schema(
        tags=['Users'],
        summary='Add customer',
        description='Add a customer to company (Employee only)'
    )
)
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

    @extend_schema(
        tags=['Users'],
        description='Add customer with CUSTOMER role automatically assigned'
    )
    def perform_create(self, serializer):
        company_id = self.kwargs['company_id']
        customer = serializer.save(
            role=CompanyUser.RoleChoices.CUSTOMER,
            company_id=company_id
        )

        # Get all managers of the company
        managers = CompanyUser.objects.filter(
            company_id=company_id,
            role=CompanyUser.RoleChoices.MANAGER
        ).select_related('user')

        channel_layer = get_channel_layer()
        for manager in managers:
            notif = SystemNotification.objects.create(
                receiver=manager.user,
                title="New Customer Added",
                description=f"A new customer '{customer.user.full_name}' was added to your company.",
                priority=SystemNotification.PriorityTypeChoices.MEDIUM
            )

            # Send WebSocket notification
            async_to_sync(channel_layer.group_send)(
                f"user_{manager.user.id}",
                {
                    "type": "send.notification",
                    "content": {
                        "id": notif.id,
                        "title": notif.title,
                        "description": notif.description,
                        "timestamp": notif.timestamp.isoformat(),
                        "priority": notif.priority,
                    }
                }
            )


@extend_schema_view(
    list=extend_schema(
        tags=['Users'],
        summary='List company members',
        description='List all active users in a company (Manager only)',
        parameters=[
            OpenApiParameter(
                name='company_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Company ID'
            )
        ]
    ),
    retrieve=extend_schema(
        tags=['Users'],
        summary='Get member details',
        description='Get details of a company member'
    )
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

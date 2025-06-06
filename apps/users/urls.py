from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.users.views.generics import (
    UserRegistrationView,
    CompanyViewSet,
    CompanyUserViewSet,
    CustomerCreateViewSet,
    UserViewSet
)

app_name = 'users'
router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')

USER_API_V1 = [
    path('', include(router.urls)),
    path('companies/<str:company_id>/users/',
         CompanyUserViewSet.as_view({
             'get': 'list',
             'post': 'create'
         }), name='company-users'),
    path('companies/<str:company_id>/users/<str:pk>/',
         CompanyUserViewSet.as_view({
             'get': 'retrieve',
             'delete': 'destroy'
         }), name='company-user-detail'),
    path('companies/<str:company_id>/users/<str:pk>/change_role/',
         CompanyUserViewSet.as_view({'post': 'change_role'}),
         name='change-role'),
    path('companies/<str:company_id>/customers/',
         CustomerCreateViewSet.as_view({
             'get': 'list',
             'post': 'create'
         }), name='customers'),
    path('companies/<str:company_id>/members/',
         UserViewSet.as_view({'get': 'list'}),
         name='company-members'),
    path('companies/<str:company_id>/members/<str:pk>/',
         UserViewSet.as_view({'get': 'retrieve'}),
         name='member-detail'),
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


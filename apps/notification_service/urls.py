from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.notification_service.views.generics import (NotificationsListView, NotificationsDetailView,
                                                      MarkNotificationAsReadView, SoftDeleteNotificationView,
                                                      MarkSelectedNotificationsAsReadView,
                                                      SoftDeleteSelectedNotificationsView,
                                                      MarkAllNotificationsAsReadView, SoftDeleteAllNotificationsView, )

app_name = 'notification_service'

router = DefaultRouter()
# router.register(r'', SystemNotificationViewSet, basename='notification')

NOTIFICATION_API_V1 = [
    #     path('', include(router.urls)),
    path('', NotificationsListView.as_view({'get': 'list'}), name='notification-list'),
    path('<str:pk>/', NotificationsDetailView.as_view({'get': 'retrieve'}),
         name='notification-detail'),
    path('<str:pk>/mark_as_read/', MarkNotificationAsReadView.as_view(),
         name='mark-notification-as-read'),
    path('<str:pk>/mark_as_delete/', SoftDeleteNotificationView.as_view(),
         name='mark_as_delete'),
    path('mark_selected_as_read/', MarkSelectedNotificationsAsReadView.as_view(),
         name='mark-selected-notifications'),
    path('mark_selected_as_delete/', SoftDeleteSelectedNotificationsView.as_view(),
         name='delete-selected-notifications'),
    path('mark_all_as_read/', MarkAllNotificationsAsReadView.as_view(), name='mark-all-notifications'),
    path('mark_all_as_delete/', SoftDeleteAllNotificationsView.as_view(), name='delete-all-notifications'),
]

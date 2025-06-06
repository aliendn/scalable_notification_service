from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from apps.notification_service import consumers
from apps.notification_service.views.generics import SystemNotificationViewSet

app_name = 'notification_service'

router = DefaultRouter()
router.register(r'', SystemNotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('<str:pk>/mark_as_read/',
         SystemNotificationViewSet.as_view({'post': 'mark_as_read'}),
         name='mark-notification-as-read'),
    path('<str:pk>/mark_as_delete/',
         SystemNotificationViewSet.as_view({'post': 'mark_as_delete'}),
         name='mark_as_delete'),
    path('mark_selected_as_read/',
         SystemNotificationViewSet.as_view({'post': 'mark_selected_as_read'}),
         name='mark-selected-notifications'),
    path('mark_selected_as_delete/',
         SystemNotificationViewSet.as_view({'post': 'mark_selected_as_delete'}),
         name='delete-selected-notifications'),
    path('mark_all_as_read/',
         SystemNotificationViewSet.as_view({'post': 'mark_all_as_read'}),
         name='mark-all-notifications'),
    path('mark_all_as_delete/',
         SystemNotificationViewSet.as_view({'post': 'mark_all_as_delete'}),
         name='delete-all-notifications'),
]

websocket_urlpatterns = [
    re_path(r"ws/notifications/(?P<room_name>\w+)/$", consumers.NotificationConsumer.as_asgi()),
]

NOTIFICATION_API_V1 = urlpatterns + websocket_urlpatterns

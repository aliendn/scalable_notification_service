from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.camera.views.generics import CameraViewSet, CameraActionLogViewSet

app_name = 'camera'

router = DefaultRouter()

router.register(r'camera-logs', CameraActionLogViewSet, basename='camera-log')

CAMERA_API_V1 = [
    path('', include(router.urls)),

    # Custom actions
    path('cameras/<int:pk>/toggle_status/',
         CameraViewSet.as_view({'post': 'toggle_status'}),
         name='camera-toggle-status'),
    path('cameras/<int:pk>/move/',
         CameraViewSet.as_view({'post': 'move'}),
         name='camera-move'),
    path('cameras/<int:pk>/toggle_recording/',
         CameraViewSet.as_view({'post': 'toggle_recording'}),
         name='camera-toggle-recording'),
]

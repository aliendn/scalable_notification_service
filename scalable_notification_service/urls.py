from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)
from apps.users.urls import USER_API_V1
from apps.notification_service.urls import NOTIFICATION_API_V1
from apps.camera.urls import CAMERA_API_V1

API_V1 = [
    path('users/', include(USER_API_V1)),
    path('notifications/', include(NOTIFICATION_API_V1)),
    path('camera_service/', include(CAMERA_API_V1)),
]

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('jkS2-A4ds-ot50-admin/', admin.site.urls),
    path(settings.API_V1_PREFIX, include(API_V1))
]

##################
# Admin information's
##################
admin.site.site_header = settings.ADMIN_HEADER
admin.site.index_title = settings.ADMIN_INDEX_TITLE

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

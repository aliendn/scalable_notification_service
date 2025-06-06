from django.contrib import admin

from apps.camera.models import Camera, CameraActionLog


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company', 'status', 'recording_status', 'is_moved', 'ip_address')
    search_fields = ('name', 'ip_address', 'company__name')
    list_filter = ('status', 'recording_status', 'company')


@admin.register(CameraActionLog)
class CameraActionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'camera', 'action', 'performed_by', 'timestamp')
    search_fields = ('camera__name', 'performed_by__full_name')
    list_filter = ('action', 'timestamp')

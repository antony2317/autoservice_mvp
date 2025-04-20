from django.contrib import admin
from .models import Garage, ServiceRecord


@admin.register(Garage)
class GarageAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone')
    search_fields = ('name', 'address')


@admin.register(ServiceRecord)
class ServiceRecordAdmin(admin.ModelAdmin):
    exclude = ('created_by',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

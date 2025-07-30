from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models import RepairCategory, RepairType, RepairRequest, RepairResponse


@admin.register(RepairRequest)
class RepairRequestAdmin(ModelAdmin):
    list_display = ('id', 'user_info', 'car_info', 'status', 'formatted_status', 'created_at', 'short_description')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'car__base_car__brand', 'car__base_car__model', 'description')
    list_editable = ('status',)
    actions = ['mark_as_in_progress', 'mark_as_completed']
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'car', 'car__base_car')

    def user_info(self, obj):
        return f"{obj.user.username} ({obj.user.email})"
    user_info.short_description = 'Пользователь'

    def car_info(self, obj):
        car = obj.car
        brand = car.base_car.brand if car.base_car else "Не указано"
        model = car.base_car.model if car.base_car else "Не указано"
        vin_info = f" (VIN: {car.vin})" if car.vin else ""
        return f"{brand} {model}{vin_info}"
    car_info.short_description = 'Автомобиль'

    def formatted_status(self, obj):
        status_map = {
            'new': '<span style="color: green;">🟢 Новая</span>',
            'in_progress': '<span style="color: orange;">🟡 В работе</span>',
            'completed': '<span style="color: blue;">🔵 Завершена</span>'
        }
        return format_html(status_map.get(obj.status, obj.status))
    formatted_status.short_description = 'Статус'
    formatted_status.admin_order_field = 'status'

    def short_description(self, obj):
        return obj.description[:100] + ('...' if len(obj.description) > 100 else '')
    short_description.short_description = 'Описание'

    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f"Обновлено {updated} заявок (статус: В работе)")
    mark_as_in_progress.short_description = "Перевести в статус 'В работе'"

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f"Обновлено {updated} заявок (статус: Завершена)")
    mark_as_completed.short_description = "Перевести в статус 'Завершена'"


@admin.register(RepairResponse)
class RepairResponseAdmin(ModelAdmin):
    list_display = ('id', 'request_info', 'service_info', 'proposed_price',
                   'proposed_date', 'is_accepted', 'acceptance_status', 'created_at')
    list_filter = ('is_accepted', 'proposed_date', 'repair_request__status')
    search_fields = ('repair_request__id', 'service__username', 'proposed_price')
    list_editable = ('is_accepted',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'proposed_date'

    def request_info(self, obj):
        return f"Заявка #{obj.repair_request.id} ({obj.repair_request.get_status_display()})"
    request_info.short_description = 'Заявка на ремонт'

    def service_info(self, obj):
        return f"{obj.service.username} ({obj.service.email})"
    service_info.short_description = 'Автосервис'

    def acceptance_status(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if obj.is_accepted else 'red',
            '✅ Подтверждено' if obj.is_accepted else '❌ Не подтверждено'
        )
    acceptance_status.short_description = 'Статус подтверждения'
    acceptance_status.admin_order_field = 'is_accepted'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(service=request.user)
        return qs


@admin.register(RepairCategory)
class RepairCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(RepairType)
class RepairTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)

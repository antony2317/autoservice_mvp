from django.contrib import admin
from django.contrib.auth import get_user_model
from unfold.admin import ModelAdmin, TabularInline

from .models import Car, ServiceRecord, ServiceRequest, CarBase
from .models import CAR_BRANDS

from django.utils.html import format_html

User = get_user_model()


admin.site.site_header = "Панель администратора автосервиса"
admin.site.site_title = "Администрирование автосервиса"
admin.site.index_title = "Управление данными"




@admin.register(CarBase)
class CarBaseAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'year_range', 'engine_type', 'engine_volume')
    list_filter = ('brand', 'engine_type')
    search_fields = ('brand', 'model')

    def year_range(self, obj):
        return f"{obj.year_from}–{obj.year_to}"
    year_range.short_description = 'Годы выпуска'


@admin.register(Car)
class CarAdmin(ModelAdmin):
    list_display = ('full_name', 'user', 'get_year', 'mileage', 'vin_display')
    list_filter = ('base_car__brand', 'base_car__year_from', 'base_car__year_to', 'user')
    search_fields = ('base_car__brand', 'base_car__model', 'vin', 'user__username')
    raw_id_fields = ('user',)
    ordering = ('-created_at',)

    fieldsets = (
        ('Основные данные', {
            'fields': ('user', 'base_car', 'vin')
        }),
        ('Технические характеристики', {
            'fields': ('mileage',)
        }),
    )

    def full_name(self, obj):
        return f"{obj.base_car.brand} {obj.base_car.model}"
    full_name.short_description = 'Автомобиль'

    def get_year(self, obj):
        return obj.year
    get_year.short_description = 'Год выпуска'

    def vin_display(self, obj):
        return obj.vin if obj.vin else "-"
    vin_display.short_description = 'VIN-номер'



@admin.register(ServiceRecord)
class ServiceRecordAdmin(ModelAdmin):
    list_display = ('car_info', 'autoservice', 'date', 'service_type', 'cost_display', 'has_receipt')
    list_filter = ('service_type', 'autoservice', 'date')
    search_fields = ('car__brand', 'car__model', 'description', 'autoservice__name')
    raw_id_fields = ('car', 'autoservice', 'created_by')
    date_hierarchy = 'date'
    list_per_page = 20

    fieldsets = (
        ('Общая информация', {
            'fields': ('car', 'autoservice', 'date', 'mileage')
        }),
        ('Детали обслуживания', {
            'fields': ('service_type', 'description', 'cost')
        }),
        ('Документы', {
            'fields': ('receipt',)
        }),
    )

    def car_info(self, obj):
        return f"{obj.car.brand} {obj.car.model} ({obj.car.user})"
    car_info.short_description = 'Автомобиль'

    def cost_display(self, obj):
        return f"{obj.cost} ₽" if obj.cost else "-"
    cost_display.short_description = 'Стоимость'

    def has_receipt(self, obj):
        return bool(obj.receipt)
    has_receipt.boolean = True
    has_receipt.short_description = 'Наличие чека'

    class Meta:
        verbose_name = 'Запись о сервисе'
        verbose_name_plural = 'Записи о сервисе'




@admin.register(ServiceRequest)
class ServiceRequestAdmin(ModelAdmin):
    list_display = ('car_info', 'status', 'status_display', 'desired_date', 'short_description')
    list_filter = ('status', 'desired_date')
    search_fields = ('car__brand', 'car__model', 'description')
    raw_id_fields = ('car',)
    actions = ['mark_as_completed', 'mark_as_accepted']
    list_editable = ('status',)

    fieldsets = (
        ('Основные данные', {
            'fields': ('car', 'status', 'desired_date')
        }),
        ('Описание проблемы', {
            'fields': ('description',)
        }),
    )

    def car_info(self, obj):
        return f"{obj.car.brand} {obj.car.model} ({obj.car.user})"

    car_info.short_description = 'Автомобиль'

    def status_display(self, obj):
        status_map = {
            'pending': '🟡 Ожидает',
            'accepted': '🟢 Принята',
            'completed': '🔵 Завершена'
        }
        return status_map.get(obj.status, obj.status)

    status_display.short_description = 'Статус'

    def short_description(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description

    short_description.short_description = 'Описание проблемы'

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f"{updated} заявок помечено как завершенные")

    mark_as_completed.short_description = "Пометить как завершенные"

    def mark_as_accepted(self, request, queryset):
        updated = queryset.update(status='accepted')
        self.message_user(request, f"{updated} заявок помечено как принятые")

    mark_as_accepted.short_description = "Пометить как принятые"

    class Meta:
        verbose_name = 'Заявка на ремонт'
        verbose_name_plural = 'Заявки на ремонт'



class ServiceRecordInline(TabularInline):
    model = ServiceRecord
    extra = 0
    fields = ('autoservice', 'date', 'service_type', 'cost')
    readonly_fields = ('date', 'service_type', 'cost')
    verbose_name = 'Запись о сервисе'
    verbose_name_plural = 'История обслуживания'

    def has_add_permission(self, request, obj):
        return False


CarAdmin.inlines = [ServiceRecordInline]

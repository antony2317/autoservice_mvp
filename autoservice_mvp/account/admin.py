from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from unfold.admin import ModelAdmin

from .models import User, AutoService



class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'display_role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def display_role(self, obj):
        return dict(obj.ROLE_CHOICES).get(obj.role, 'Неизвестно')
    display_role.short_description = 'Роль'


class AutoServiceAdmin(ModelAdmin):
    list_display = ('name', 'user', 'phone')
    search_fields = ('name', 'user__username', 'phone')
    raw_id_fields = ('user',)



admin.site.register(User, CustomUserAdmin)
admin.site.register(AutoService, AutoServiceAdmin)

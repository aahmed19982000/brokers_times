from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'preferred_language', 'is_staff', 'is_active']
    list_filter = ['role', 'preferred_language', 'is_staff', 'is_active']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Profile Fields', {
            'fields': ('role', 'preferred_language', 'bio', 'avatar', 'facebook_url', 'linkedin_url')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Profile Fields', {
            'fields': ('role', 'preferred_language', 'bio', 'avatar', 'facebook_url', 'linkedin_url')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
